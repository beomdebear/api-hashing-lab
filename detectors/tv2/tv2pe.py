"""Minimal, bounds-checked PE32+ reader used by the TV2 static detector.

It only reads bytes of the input file. It never loads or executes the sample.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass


class PeError(Exception):
    """The input is not a PE file that can be parsed (analysis_error)."""


class PeUnsupported(PeError):
    """Valid PE, but outside the supported scope: PE32+ / x86-64 (unsupported)."""


IMAGE_SCN_MEM_EXECUTE = 0x20000000
DIR_EXPORT, DIR_IMPORT, DIR_EXCEPTION = 0, 1, 3
MAX_IMPORT_DLLS = 512
MAX_THUNKS = 20000
MAX_STRINGS = 5000


@dataclass(frozen=True)
class Section:
    name: str
    rva: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int

    @property
    def executable(self) -> bool:
        return bool(self.characteristics & IMAGE_SCN_MEM_EXECUTE)

    @property
    def mapped_size(self) -> int:
        return max(self.virtual_size, self.raw_size)


@dataclass(frozen=True)
class ImportEntry:
    dll: str
    name: str
    iat_rva: int


class PeFile:
    def __init__(self, data: bytes):
        self.data = data
        self.sha256 = hashlib.sha256(data).hexdigest().upper()
        self._parse_headers()
        self.imports = self._parse_imports()
        self.iat = {i.iat_rva: i for i in self.imports}
        self.runtime_functions = self._parse_pdata()

    @classmethod
    def from_path(cls, path: str) -> "PeFile":
        with open(path, "rb") as handle:
            return cls(handle.read())

    def _u(self, fmt: str, offset: int):
        size = struct.calcsize(fmt)
        if offset < 0 or offset + size > len(self.data):
            raise PeError(f"read outside file at offset {offset:#x}")
        return struct.unpack_from(fmt, self.data, offset)

    def _parse_headers(self) -> None:
        if len(self.data) < 0x40 or self.data[:2] != b"MZ":
            raise PeError("missing MZ header")
        nt = self._u("<I", 0x3C)[0]
        if self.data[nt:nt + 4] != b"PE\0\0":
            raise PeError("missing PE signature")
        self.machine, count, _, _, _, opt_size, self.file_characteristics = self._u("<HHIIIHH", nt + 4)
        opt = nt + 24
        magic = self._u("<H", opt)[0]
        if magic != 0x20B or self.machine != 0x8664:
            raise PeUnsupported(f"unsupported machine={self.machine:#x} optional_magic={magic:#x}")
        self.entry_rva = self._u("<I", opt + 16)[0]
        self.image_base = self._u("<Q", opt + 24)[0]
        self.size_of_image = self._u("<I", opt + 56)[0]
        dir_count = min(self._u("<I", opt + 108)[0], 16)
        self.directories = [self._u("<II", opt + 112 + 8 * i) for i in range(dir_count)]
        self.sections = []
        table = opt + opt_size
        for i in range(count):
            raw = self._u("<8sIIIIIIHHI", table + 40 * i)
            name = raw[0].split(b"\0", 1)[0].decode("ascii", "replace")
            self.sections.append(Section(name, raw[2], raw[1], raw[4], raw[3], raw[9]))
        if not self.sections:
            raise PeError("no sections")

    def section_of(self, rva: int):
        for section in self.sections:
            if section.rva <= rva < section.rva + section.mapped_size:
                return section
        return None

    def rva_to_offset(self, rva: int):
        section = self.section_of(rva)
        if section is None:
            return None
        delta = rva - section.rva
        return section.raw_offset + delta if delta < section.raw_size else None

    def va(self, rva: int) -> int:
        return self.image_base + rva

    def read_rva(self, rva: int, size: int) -> bytes:
        offset = self.rva_to_offset(rva)
        return b"" if offset is None else self.data[offset:offset + size]

    def cstring(self, rva: int, limit: int = 512) -> str:
        offset = self.rva_to_offset(rva)
        if offset is None:
            return ""
        raw = self.data[offset:offset + limit]
        return raw.split(b"\0", 1)[0].decode("ascii", "replace")

    def _directory(self, index: int):
        return self.directories[index] if index < len(self.directories) else (0, 0)

    def _parse_imports(self):
        rva, size = self._directory(DIR_IMPORT)
        entries = []
        if not rva or not size:
            return entries
        for index in range(MAX_IMPORT_DLLS):
            raw = self.read_rva(rva + 20 * index, 20)
            if len(raw) < 20:
                raise PeError("truncated import directory")
            original, _, _, name_rva, first = struct.unpack("<IIIII", raw)
            if not any((original, name_rva, first)):
                return entries
            dll = self.cstring(name_rva)
            lookup = original or first
            for slot in range(MAX_THUNKS):
                thunk = self.read_rva(lookup + 8 * slot, 8)
                if len(thunk) < 8:
                    raise PeError("truncated import thunk table")
                value = struct.unpack("<Q", thunk)[0]
                if value == 0:
                    break
                if value >> 63:
                    name = f"#ordinal{value & 0xFFFF}"
                else:
                    name = self.cstring((value & 0x7FFFFFFF) + 2)
                entries.append(ImportEntry(dll, name, first + 8 * slot))
        raise PeError("import directory has no terminator")

    def _parse_pdata(self):
        rva, size = self._directory(DIR_EXCEPTION)
        result = []
        if not rva or not size:
            return result
        for index in range(size // 12):
            raw = self.read_rva(rva + 12 * index, 12)
            if len(raw) < 12:
                break
            begin, end, _ = struct.unpack("<III", raw)
            section = self.section_of(begin)
            if begin < end and section is not None and section.executable:
                result.append((begin, end))
        return sorted(set(result))

    def strings(self, min_len: int = 5):
        """ASCII and UTF-16LE strings from non-executable sections."""
        found = []
        for section in self.sections:
            if section.executable or not section.raw_size:
                continue
            blob = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            found.extend(_scan_ascii(blob, section, min_len))
            found.extend(_scan_utf16(blob, section, min_len))
        found.sort(key=lambda item: (item["rva"], item["encoding"]))
        return found[:MAX_STRINGS]


def _printable(byte: int) -> bool:
    return 0x20 <= byte < 0x7F


def _scan_ascii(blob: bytes, section: Section, min_len: int):
    out, start = [], None
    for index, byte in enumerate(blob + b"\0"):
        if _printable(byte):
            start = index if start is None else start
            continue
        if start is not None and index - start >= min_len:
            out.append(_string_item(section, start, blob[start:index].decode("ascii"), "ascii"))
        start = None
    return out


def _scan_utf16(blob: bytes, section: Section, min_len: int):
    out, index = [], 0
    while index + 1 < len(blob):
        start = index
        chars = []
        while index + 1 < len(blob) and blob[index + 1] == 0 and _printable(blob[index]):
            chars.append(chr(blob[index]))
            index += 2
        if len(chars) >= min_len:
            out.append(_string_item(section, start, "".join(chars), "utf-16le"))
        index = index + 2 if index == start else index
    return out


def _string_item(section: Section, offset: int, value: str, encoding: str):
    return {
        "rva": section.rva + offset,
        "file_offset": section.raw_offset + offset,
        "section": section.name,
        "encoding": encoding,
        "value": value,
    }
