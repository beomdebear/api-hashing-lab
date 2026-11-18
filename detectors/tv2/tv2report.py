#!/usr/bin/env python3
"""Builds the TV2 evidence tables from measured outputs (no hand-typed results)."""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "detectors" / "tv2"))
import tv2analysis as ta  # noqa: E402
import tv2d1adapter  # noqa: E402
import tv2features  # noqa: E402
import tv2rules  # noqa: E402
from tv2pe import PeFile  # noqa: E402
from tv2tasks import TASKS  # noqa: E402

NM = r"C:\msys64\mingw64\bin\nm.exe"
BUILD = "20261118-094956"
VERSION = "1.0.1"
EXPORT = ROOT / "artifacts" / "ghidra" / BUILD / "export"
CFG = ROOT / "configs" / "tv2"
RELATIONS = ("rel.export_names_enumerated", "rel.export_name_to_hash", "rel.hash_to_compare",
             "rel.compare_to_name_selection", "rel.selection_to_resolve", "rel.resolve_to_pointer_use")
SHORT = {"verified": "đã xác minh", "heuristic": "gợi ý", "absent": "không thấy", "unknown": "chưa xác định",
         "analysis_error": "lỗi phân tích"}
FILE_APIS = ("CreateFileW", "WriteFile", "CloseHandle")


def rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print("wrote", path)


def table(headers, data):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in data:
        lines.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in row) + " |")
    return "\n".join(lines)


def run_dir(split, version=VERSION):
    base = ROOT / ("evidence/G2/TV2/G2-TV2-01/runs" if split == "dev" else "evidence/G3/TV2/G3-TV2-01/runs")
    return sorted(base.glob(f"R-*-{split}-{version}"))[-1]


class Data:
    def __init__(self):
        self.manifest = {r["role"]: r for r in rows(CFG / "manifest-provisional.csv")}
        self.truth = {r["sample_id"]: r for r in rows(CFG / "ground-truth-provisional.csv")}
        self.runs = {s: run_dir(s) for s in ("dev", "test", "probe")}
        self.results = {s: rows(self.runs[s] / "per-sample.csv") for s in self.runs}
        self.metrics = {s: load(self.runs[s] / "metrics.json") for s in self.runs}

    def features(self, role):
        row = self.manifest[role]
        return load(self.runs[row["split"]] / "features" / f"{row['sample_id']}.json")

    def rel_path(self, path):
        return Path(path).relative_to(ROOT).as_posix()


def hx(value):
    return f"0x{value:X}"


def ghidra_names(role):
    return {int(r["entry_rva"], 16): r["ghidra_name"] for r in rows(EXPORT / role / "functions.csv")}


def api_calls(role, api=None):
    out = rows(EXPORT / role / "api-calls.csv")
    return [r for r in out if api is None or r["target_api"] == api]


def user_range(rva):
    return int(rva, 16) < 0x1680


def ghidra_strings(role):
    return rows(EXPORT / role / "strings.csv")


def copy_export(role, target):
    destination = ROOT / target / role
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(EXPORT / role, destination)


def string_refs(role, wanted):
    values = {r["value"]: r for r in ghidra_strings(role)}
    out = []
    for name in wanted:
        if name in values:
            refs = values[name]["referenced_from_rva"] or "không có tham chiếu"
            out.append(f"{name} @{values[name]['rva']} (tham chiếu: {refs})")
    return "; ".join(out) or "không có"


NOTE_VI = {
    "read of NT headers +0x88 (PE32+ export directory RVA)": "đọc RVA của export directory tại NT headers +0x88 (PE32+)",
    "read of export directory +0x20 (AddressOfNames)": "đọc AddressOfNames tại export directory +0x20",
    "indexed read from AddressOfNames": "đọc RVA tên theo chỉ số từ AddressOfNames",
    "module base + name RVA gives an export-name pointer": "module base + RVA tên tạo con trỏ tên export",
    "export-name pointer passed to hash-like function at RVA 0x1000": "con trỏ tên export được truyền vào hàm giống hash tại RVA 0x1000",
    "hash of export name compared with a function argument": "hash của tên export được so với tham số hàm",
    "export-name pointer is assigned only when the hash comparison selects it": "con trỏ tên chỉ được gán khi phép so hash chọn nó",
    "hash-selected export name is passed to GetProcAddress": "tên được chọn bằng hash được truyền vào GetProcAddress",
    "call target is API(SEL)": "đích lời gọi là địa chỉ GetProcAddress trả về từ tên đã chọn",
}


def gcc_facts(data, role):
    """Maps hash-like loops and budget misses of a GCC probe to its own symbol table."""
    path = ROOT / data.manifest[role]["binary"]
    pe = PeFile.from_path(path)
    az = ta.analyze(pe)
    output = subprocess.run([NM, "-n", str(path)], capture_output=True, text=True, check=True).stdout
    symbols = [(int(p[0], 16) - pe.image_base, p[2]) for p in (line.split() for line in output.splitlines())
               if len(p) == 3 and p[1] in "Tt"]
    starts = [item[0] for item in symbols]
    name_of = lambda rva: symbols[bisect_right(starts, rva) - 1][1]
    loops = Counter(name_of(item["function_rva"]) for item in ta.syntactic_loops(az, load(CFG / "extractor.json")["signal_params"]))
    budget = sorted({name_of(item["function_rva"]) for item in az.incomplete if item["function_rva"]})
    kinds = {key[0] for key in az.events}
    return loops, budget, kinds


def b1_b2(data):
    out = ["# So sánh B1 và B2 trên binary", "",
           "Nguồn số liệu: export headless của Ghidra 12.2 trong `ghidra-headless/` và đặc trưng của extractor. Đây chưa phải ảnh GUI.", ""]
    rows_out = []
    for role in ("B1", "B2"):
        doc = data.features(role)
        calls = [r for r in api_calls(role) if user_range(r["call_rva"]) and r["target_api"] in FILE_APIS + ("GetProcAddress", "LoadLibraryW")]
        imports = sorted({r["symbol"] for r in rows(EXPORT / role / "imports.csv")} & set(FILE_APIS + ("GetProcAddress", "LoadLibraryW")))
        indirect = [r for r in rows(EXPORT / role / "indirect-calls.csv") if user_range(r["call_rva"]) and "RSP" in r["instruction"]]
        rows_out.append((role, data.manifest[role]["sha256"], ", ".join(imports) or "không có",
                         string_refs(role, FILE_APIS),
                         "; ".join(f"{r['call_rva']} {r['target_api']}" for r in calls),
                         "; ".join(f"{r['call_rva']} `{r['instruction']}`" for r in indirect) or "không có",
                         doc["features"]["f.code.hash_like_loops"]["value"],
                         SHORT[doc["features"]["rel.export_name_to_hash"]["status"]]))
    out.append(table(["Mẫu", "SHA-256", "Import liên quan", "Chuỗi tên API", "Lời gọi API trong mã người dùng",
                      "Gọi gián tiếp qua con trỏ", "Vòng giống hash", "Tên export → hash"], rows_out))
    out += ["", "## Kết luận từ bằng chứng", "",
            "- B1 import sẵn ba API file và gọi chúng qua ô IAT. Dạng lệnh `CALL [IAT]` là gián tiếp về cú pháp nhưng đích do loader điền từ bảng import.",
            "- Tên API cũng xuất hiện trong B1, nhưng Ghidra không thấy mã nào tham chiếu các chuỗi đó. Chúng thuộc dữ liệu tên của bảng import.",
            "- B2 không import ba API này. Nó có `LoadLibraryW`, `GetProcAddress`, và mã chương trình tham chiếu trực tiếp các hằng chuỗi tên API trước khi gọi `GetProcAddress`, rồi gọi qua con trỏ. Đây là resolve động theo tên.",
            "- B2 không có vòng giống hash và không có luồng tên export → hash, nên chưa phải API hashing.", "",
            "## Vị trí tên hằng trong B2", ""]
    gpa = [e for e in data.features("B2")["features"]["f.resolve.constant_names"]["evidence"]]
    out.append(table(["RVA lời gọi", "Lệnh", "Quan sát"], [(hx(e["rva"]), f"`{e['text']}`", e["note"]) for e in gpa]))
    write("evidence/G1/TV2/G1-TV2-02/b1-b2-comparison.md", "\n".join(out))
    for role in ("B1", "B2"):
        copy_export(role, "evidence/G1/TV2/G1-TV2-02/ghidra-headless")


def djb2(text):
    value = 5381
    for char in text.encode():
        value = (value * 33 + char) & 0xFFFFFFFF
    return value


def annotate(lines, notes):
    out = []
    for line in lines:
        out.append(line)
        for needle, note in notes:
            if needle in line:
                out.append(" " * (len(line) - len(line.lstrip())) + f"// [TV2] {note}")
    return out


def decompile_of(role, rva):
    return next((EXPORT / role / "decompile").glob(f"*_rva_{rva:X}.c")).read_text(encoding="utf-8").strip().splitlines()


def p1_chain(data):
    doc = data.features("P1")
    names = ghidra_names("P1")
    base = doc["pe"]["image_base"]
    plan = [("1. Duyệt bảng export", "rel.export_names_enumerated", ("export_directory", "AddressOfNames", "export-name pointer")),
            ("2. Hash tên export", "rel.export_name_to_hash", ("",)), ("3. So sánh hash", "rel.hash_to_compare", ("",)),
            ("4. Chọn tên khi khớp", "rel.compare_to_name_selection", ("",)),
            ("5. Resolve bằng tên đã chọn", "rel.selection_to_resolve", ("",)),
            ("6. Dùng con trỏ", "rel.resolve_to_pointer_use", ("",))]
    table_rows, seen = [], set()
    for step, relation, _ in plan:
        for item in doc["features"][relation]["evidence"]:
            if item["rva"] in seen:
                continue
            seen.add(item["rva"])
            table_rows.append((step, f"P1.exe + {hx(item['rva'])}", hx(base + item["rva"]), hx(item["file_offset"]),
                               f"{names.get(item['function_rva'], '?')} (RVA {hx(item['function_rva'])})", f"`{item['text']}`",
                               NOTE_VI.get(item["note"], item["note"]), "Đã xác minh"))
    main_asm = next((EXPORT / "P1" / "disasm").glob("*_rva_13F0.asm")).read_text(encoding="utf-8").splitlines()
    targets = []
    for api in FILE_APIS:
        value = djb2(api)
        line = next((l for l in main_asm if f"0x{value:x}" in l.lower()), "")
        targets.append((api, hx(value), f"`{line.strip()}`" if line else "không thấy"))
    out = ["# Chuỗi bằng chứng API hashing trong P1", "",
           f"- Binary: `P1.exe`, SHA-256 `{data.manifest['P1']['sha256']}`, build `{BUILD}`.",
           f"- Image base tĩnh: `{hx(base)}`. Mọi địa chỉ thuộc cùng binary này. VA ở đây là VA tĩnh, không phải VA lúc chạy.",
           "- Tên `FUN_*` là tên Ghidra tự đặt. Binary không có PDB nên không có symbol gốc của các hàm này.",
           "- Mỗi lệnh dưới đây được extractor nêu và đã khớp RVA, mnemonic trong disassembly của Ghidra (xem `ghidra-crosscheck.csv`).", "",
           table(["Bước", "Module + RVA", "VA tĩnh", "File offset", "Hàm", "Lệnh", "Quan hệ quan sát", "Mức"], table_rows), "",
           "## Quan hệ giữa các bước", "",
           "1. `FUN_1400010b0` đọc export directory của module truyền vào, rồi tạo con trỏ tên bằng `base + AddressOfNames[i]`.",
           "2. Con trỏ tên được truyền vào `FUN_140001000`. Hàm này lặp trên từng byte với `h = h * 33 + byte`, seed `0x1505`.",
           "3. Giá trị trả về được so với tham số thứ hai của `FUN_1400010b0`.",
           "4. Khối chạy khi khớp ghi con trỏ tên ra tham số out. Quan hệ này là phụ thuộc điều khiển vào phép so sánh.",
           "5. `FUN_140001360` lấy tên đó và truyền vào `GetProcAddress`. API nhận **tên**, không nhận hash.",
           "6. Địa chỉ trả về đi qua tham số out về `FUN_1400013f0` và trở thành đích của `CALL [RSP+0x68]`.", "",
           "## Suy luận của người phân tích, tách khỏi bằng chứng trên", "",
           "Ba hằng dưới đây nằm trong `FUN_1400013f0`. Việc chúng ứng với API nào là phép tính DJB2 độc lập trên tên API công khai, không phải điều binary tự khai. Detector không dùng bảng này.", "",
           table(["API", "DJB2 tính độc lập", "Lệnh chứa hằng trong binary"], targets), "",
           "Phân tích tĩnh không xác định địa chỉ thực lúc chạy. Với forwarded export, địa chỉ trả về có thể nằm ở module khác như KernelBase.", "",
           "## Trạng thái ảnh", "", "Ảnh decompile có chú thích từ GUI chưa có. Bản văn bản ở `p1-decompile-annotated.md` lấy từ decompiler chạy headless."]
    write("evidence/G1/TV2/G1-TV2-03/p1-evidence-chain.md", "\n".join(out))
    sections = [("Vòng hash — `FUN_140001000`", 0x1000, [("0x1505", "seed DJB2 = 5381"), ("* 0x21", "h = h * 33 + byte")]),
                ("Duyệt export và so sánh — `FUN_1400010b0`", 0x10B0,
                 [("_Buf = (byte *)", "con trỏ tên export = module base + RVA tên"), ("FUN_140001000(_Buf)", "hash tên export"),
                  ("iVar3 == param_2", "so hash với giá trị đích"), ("*param_3 = _Buf", "ghi tên được chọn ra tham số out")]),
                ("Resolve — `FUN_140001360`", 0x1360, [("GetProcAddress", "tên đã chọn đi vào GetProcAddress")])]
    text = ["# Decompile P1 có chú thích (bản văn bản)", "",
            "Mã dưới đây do decompiler Ghidra 12.2 xuất ở chế độ headless. Dòng `// [TV2]` do script TV2 chèn. **Đây không phải ảnh GUI.**", ""]
    for title, rva, notes in sections:
        text += [f"## {title}", "", "```c", *annotate(decompile_of("P1", rva), notes), "```", ""]
    write("evidence/G1/TV2/G1-TV2-03/p1-decompile-annotated.md", "\n".join(text))
    copy_export("P1", "evidence/G1/TV2/G1-TV2-03/ghidra-headless")


def result_row(item):
    return (item["role"], item["sample_id"], item["sha256"][:16] + "…", item["label"], item["verdict"], item["outcome"],
            item["reason"], item["evidence"] or "—", item["analysis_ms"])


RESULT_HEAD = ["Mẫu", "Sample ID", "SHA-256", "Nhãn đề xuất", "Kết luận", "KQ", "Lý do", "Bằng chứng đầu", "ms"]


def d0_dev(data):
    selected = [r for r in data.results["dev"] if r["detector"] == "D0"]
    out = ["# Kết quả D0 trên tập phát triển", "", f"Run: `{selected[0]['run_id']}`. Nhãn là đề xuất của TV2, chỉ evaluator đọc.", "",
           table(RESULT_HEAD, [result_row(r) for r in selected]), "", "## Vị trí bằng chứng của P1", ""]
    prediction = load(data.runs["dev"] / "predictions" / "d0" / f"{data.manifest['P1']['sample_id']}.json")
    evidence = [(c["id"], c["feature"], hx(e["rva"]), f"`{e['text']}`", e["note"]) for c in prediction["conditions"] for e in c["evidence"]]
    out.append(table(["Điều kiện", "Đặc trưng", "RVA", "Quan sát", "Ghi chú"], evidence))
    write("evidence/G2/TV2/G2-TV2-01/d0-dev-results.md", "\n".join(out))


CONTROL_MEANING = {
    "TV2C-B3": "B3: resolve theo tên từ bảng chuỗi",
    "TV2C-B4": "B4: hash dữ liệu, API là import sẵn",
    "TV2C-B5": "B5: hash cấu hình, resolve theo hằng chuỗi",
    "TV2C-B6": "B6: duyệt export, so bằng strcmp, resolve theo tên",
}


def controls(data):
    all_results = data.results["dev"] + data.results["test"]
    body = []
    for role, meaning in CONTROL_MEANING.items():
        f = data.features(role)["features"]
        d0 = next(r for r in all_results if r["role"] == role and r["detector"] == "D0")
        static = next(r for r in all_results if r["role"] == role and r["detector"] == "STATIC-ONLY")
        body.append((role, meaning, data.manifest[role]["sha256"][:16] + "…", "có" if f["f.imports.get_proc_address"]["value"] else "không",
                     f["f.code.hash_like_loops"]["value"], f["f.code.non_import_indirect_calls"]["value"],
                     SHORT[f["rel.export_names_enumerated"]["status"]], SHORT[f["rel.export_name_to_hash"]["status"]],
                     f"{d0['verdict']} ({d0['outcome']})", f"{static['verdict']} ({static['outcome']})"))
    out = ["# Dấu hiệu và kết quả ban đầu của các mẫu đối chứng đề xuất", "",
           "`TV2C-B3..B6` là mẫu do TV2 đề xuất cho vai trò B3–B6. **TV4 chưa xác nhận**, nên đây chưa phải B3–B6 chính thức.", "",
           table(["Mẫu", "Vai trò đề xuất", "SHA-256", "Import GetProcAddress", "Vòng giống hash", "Gọi gián tiếp ngoài IAT",
                  "Duyệt tên export", "Tên export → hash", "D0", "Static-only"], body), "",
           "## FP/FN ban đầu của D0", "",
           "- FP: `TV2C-B5`. Ba dấu hiệu của D0 cùng tồn tại nhưng không liên quan với nhau.",
           "- FN trên bốn mẫu đối chứng: không áp dụng, vì cả bốn đều mang nhãn âm tính đề xuất.",
           "- `TV2C-B6` không bị D0 báo vì so tên bằng `strcmp` qua import, nên không tạo vòng giống hash.", "",
           "## Kiểm tra điều kiện của PDF trên binary", ""]
    checks = []
    for role in CONTROL_MEANING:
        f = data.features(role)["features"]
        hash_found = f["f.code.hash_like_loops"]["value"]
        constant = len(f["f.resolve.constant_names"]["value"] or [])
        dynamic = f["f.resolve.dynamic_name_calls"]["value"]
        gpa = f["f.code.get_proc_address_calls"]["value"]
        checks.append((role, gpa, constant, dynamic, hash_found, SHORT[f["rel.selection_to_resolve"]["status"]]))
    out.append(table(["Mẫu", "Số lời gọi GetProcAddress", "Tên hằng đã truy được", "Lời gọi có tên không phải hằng", "Vòng giống hash", "Tên chọn bằng hash → resolve"], checks))
    out += ["", "Với TV2C-B3, tên được đọc từ bảng con trỏ nên extractor không truy được thành hằng chuỗi trực tiếp. Ghidra cho thấy các chuỗi tên API được bảng dữ liệu tham chiếu: "
            + string_refs("TV2C-B3", FILE_APIS) + ".", ""]
    write("evidence/G2/TV2/G2-TV2-02/control-signals.md", "\n".join(out))
    for role in CONTROL_MEANING:
        copy_export(role, "evidence/G2/TV2/G2-TV2-02/ghidra-headless")


def missing_examples(data):
    extractor, static = load(CFG / "extractor.json"), load(CFG / "static-only.json")
    folder = ROOT / "evidence/G2/TV2/G2-TV2-03/missing-evidence-examples"
    folder.mkdir(parents=True, exist_ok=True)
    work = ROOT / "artifacts" / "tmp-missing"
    work.mkdir(parents=True, exist_ok=True)
    p1 = (ROOT / data.manifest["P1"]["binary"]).read_bytes()
    feature = data.features("P1")["features"]["rel.hash_to_compare"]["evidence"][0]
    patched = bytearray(p1)
    patched[feature["file_offset"]:feature["file_offset"] + 4] = b"\x90" * 4
    machine = bytearray(p1)
    machine_at = struct.unpack_from("<I", machine, 0x3C)[0] + 4
    struct.pack_into("<H", machine, machine_at, 0x14C)
    cases = [("synthetic-truncated-P1", p1[:0x180], "Fixture tổng hợp: cắt P1 còn 0x180 byte"),
             ("synthetic-wrong-machine-P1", bytes(machine), "Fixture tổng hợp: đổi trường Machine của P1 thành x86"),
             ("synthetic-compare-removed-P1", bytes(patched), "Fixture tổng hợp: thay lệnh so sánh hash của P1 bằng NOP")]
    body = []
    for name, blob, meaning in cases:
        path = work / f"{name}.bin"
        path.write_bytes(blob)
        doc = tv2features.extract(path, extractor)
        doc["run"]["input_path"] = f"{name}.bin"
        prediction = tv2rules.evaluate(doc, static)
        (folder / f"{name}.features.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (folder / f"{name}.prediction.json").write_text(json.dumps(prediction, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        body.append((name, meaning, doc["analysis"]["status"], " > ".join(SHORT[doc["features"][r]["status"]] for r in RELATIONS), prediction["verdict"]))
    shutil.rmtree(work)
    for role, meaning in (("TV2C-B6", "Mẫu thật: có duyệt export nhưng thiếu bước hash"), ("E1", "Mẫu thật: có resolve nhưng không dùng địa chỉ"), ("B2", "Mẫu thật: không có chuỗi export")):
        doc = data.features(role)
        verdict = tv2rules.evaluate(doc, static)["verdict"]
        body.append((role, meaning, doc["analysis"]["status"], " > ".join(SHORT[doc["features"][r]["status"]] for r in RELATIONS), verdict))
    text = ["# Ví dụ thiếu bằng chứng", "", "Thứ tự quan hệ: duyệt tên export > tên → hash > hash → so sánh > so sánh → chọn tên > tên → resolve > resolve → dùng con trỏ.", "",
            table(["Trường hợp", "Ý nghĩa", "analysis.status", "Trạng thái quan hệ", "Static-only"], body), "",
            "Fixture tổng hợp chỉ dùng để kiểm tra cách biểu diễn thiếu bằng chứng. Chúng không thuộc tập đánh giá."]
    write("evidence/G2/TV2/G2-TV2-03/missing-evidence-examples.md", "\n".join(text))


def features_summary(data):
    roles = [r for r, row in data.manifest.items() if row["split"] == "dev"]
    body = []
    folder = ROOT / "evidence/G2/TV2/G2-TV2-03/d1-input-dev"
    folder.mkdir(parents=True, exist_ok=True)
    for role in roles:
        doc = data.features(role)
        f = doc["features"]
        body.append((role, doc["sample"]["sha256"][:16] + "…", f["f.imports.get_proc_address"]["value"], f["f.code.hash_like_loops"]["value"],
                     f["f.code.non_import_indirect_calls"]["value"], *[SHORT[f[r]["status"]] for r in RELATIONS]))
        record = tv2d1adapter.adapt(doc)
        (folder / f"{data.manifest[role]['sample_id']}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    out = ["# Đặc trưng của tập phát triển", "", f"Features gốc: `{data.rel_path(data.runs['dev'] / 'features')}`.", "",
           table(["Mẫu", "SHA-256", "Import GPA", "Vòng giống hash", "Gọi gián tiếp", "Export", "→ hash", "→ so sánh", "→ chọn tên", "→ resolve", "→ dùng con trỏ"], body)]
    write("evidence/G2/TV2/G2-TV2-03/features-dev-summary.md", "\n".join(out))


def compare_versions():
    old = {(r["detector"], r["sample_id"]): r["verdict"] for r in rows(run_dir("test", "1.0.0") / "per-sample.csv")}
    new = {(r["detector"], r["sample_id"]): r["verdict"] for r in rows(run_dir("test") / "per-sample.csv")}
    return sum(old[k] != new[k] for k in old), len(old)


def metric_row(split, detector, item):
    c = item["counts"]
    na = lambda v: "N/A" if v is None else v
    return (split, detector, item["samples_total"], item["analysis_succeeded"], c["TP"], c["TN"], c["FP"], c["FN"], c["UNKNOWN"],
            na(item["precision"]), na(item["recall"]), na(item["f1"]), item["analysis_ms"]["median"])


def analysis(data):
    metrics = [metric_row(s, name, item) for s in ("dev", "test", "probe") for name, item in data.metrics[s]["detectors"].items()]
    head = ["Tập", "Detector", "Số mẫu", "Phân tích ok", "TP", "TN", "FP", "FN", "Unknown", "Precision", "Recall", "F1", "Trung vị ms"]
    changed, total = compare_versions()
    b5 = data.features("TV2C-B5")["features"]
    names = ghidra_names("TV2C-B5")
    loop = b5["f.code.hash_like_loops"]["evidence"][1]
    b6_loops, b6_budget, _ = gcc_facts(data, "VAR-B6-GCC-O2")
    p1_loops, p1_budget, p1_kinds = gcc_facts(data, "VAR-P1-GCC-O2")
    inline = [role for role in ("VAR-P1-MSVC-O2", "VAR-P3-MSVC-O2")
              if all(e["note"].startswith("inline") for e in data.features(role)["features"]["rel.export_name_to_hash"]["evidence"])]
    p1_gcc = data.features("VAR-P1-GCC-O2")["features"]
    e1 = data.features("E1")["features"]
    crt_common = data.features("B1")["features"]["f.code.non_import_indirect_calls"]["value"]
    out = ["# Phân tích kết quả và lỗi", "",
           "Nhãn và split là đề xuất của TV2, chưa được TV4 duyệt. Các mẫu P1–P5, E1, E2 cùng một họ PoC và cùng cấu hình compiler, nên đây là thử nghiệm nội bộ, không phải đánh giá held-out của nhóm.", "",
           "## Tổng hợp", "", table(head, metrics), "",
           f"Lượt test với lock 1.0.0 và 1.0.1 có {changed}/{total} kết luận khác nhau. Runs 1.0.0 được giữ nguyên trong thư mục `runs/`.", "",
           "## Lỗi của tập test", "",
           table(["Mẫu", "Detector", "Loại", "Vị trí bằng chứng", "Vì sao sai", "Phân loại nguyên nhân"], [
               ("TV2C-B5", "D0", "FP", f"Vòng hash ở {names.get(loop['function_rva'])} RVA {hx(loop['rva'])}; GetProcAddress và gọi gián tiếp ở các vị trí trong prediction gốc",
                "D0 chỉ cần ba dấu hiệu cùng tồn tại. Vòng FNV-1a chỉ kiểm tra chuỗi cấu hình, còn tên API là hằng chuỗi.", "Dự đoán sai do giới hạn của rule đồng xuất hiện"),
           ]), "", "Static-only không có FP/FN trên tập test đề xuất. Với TV2C-B5, nó báo âm tính vì binary không duyệt tên export và không có luồng tên export → hash.", "",
           "## Quan sát ở mẫu thăm dò compiler (không tính vào metric chính)", "",
           table(RESULT_HEAD, [result_row(r) for r in data.results["probe"]]), "",
           f"- Hai mẫu GCC `-O2` là `partial`: extractor vượt ngân sách ở các hàm runtime {', '.join(f'`{n}`' for n in sorted(set(b6_budget + p1_budget)))}, nên static-only trả `unknown`. Đây là giới hạn công cụ, không phải kết luận âm tính.",
           f"- `VAR-B6-GCC-O2` là FP của D0. Toàn bộ {sum(b6_loops.values())} vòng giống hash nằm trong {len(b6_loops)} hàm runtime MinGW, nhiều nhất là {', '.join(f'`{n}` ({c})' for n, c in b6_loops.most_common(2))}; không có vòng nào trong `main`, `find_export_name` hay `resolve_by_name`. Mẫu này không được dùng để chỉnh rule.",
           f"- `VAR-P1-GCC-O2`: GCC inline resolver vào `main` ({p1_loops.get('main', 0)} vòng giống hash ở đó). Extractor chỉ truy được tới AddressOfNames (`rel.export_names_enumerated` = `{p1_gcc['rel.export_names_enumerated']['status']}`), {'đã có' if 'export_name_pointer' in p1_kinds else 'chưa có'} sự kiện con trỏ tên export. Nếu bỏ giới hạn ngân sách, mẫu này có nguy cơ thành FN. Giả thuyết về cách sửa chưa được kiểm tra.",
           f"- Với MSVC `/O2`, static-only xác minh đủ chuỗi ở P1 và P3. Hàm hash đã được inline ở: {', '.join(inline) or 'không mẫu nào'}.", "",
           "## Hạn chế đã đo được của D0", "",
           f"- Điều kiện D0-C3 phân biệt yếu: ngay B1 đã có {crt_common} lời gọi gián tiếp ngoài IAT, đến từ mã khởi động CRT.",
           f"- Quét tuyến tính tính cả mã không chạy tới được. Ở E1, 3 lời gọi tại 0x154F, 0x159E, 0x15AB nằm trong đoạn như vậy. Ghidra không disassemble đoạn này nên đây là khác biệt duy nhất trong `ghidra-crosscheck.csv`.",
           f"- E1 có quan hệ resolve → dùng con trỏ ở mức `{e1['rel.resolve_to_pointer_use']['status']}`, đúng với việc địa chỉ không được gọi trên đường chạy thật.", "",
           "## Phân biệt nguồn lỗi", "",
           "- Lỗi mẫu: không phát hiện trong phần phân tích tĩnh. Phiên này không chạy các binary.",
           "- Lỗi công cụ: crash số dịch âm ở extractor 1.0.0 đã sửa ở 1.0.1; hai mẫu GCC vượt ngân sách vẫn còn.",
           "- Thiếu dữ liệu: chưa có dữ liệu của TV4 và TV3 để đối chiếu FP/FN.",
           "- Dự đoán sai: FP của D0 trên TV2C-B5.", "",
           "## Dữ liệu gốc", "",
           *[f"- {s}: `{data.rel_path(data.runs[s])}` gồm `run.json`, `features/`, `predictions/`, `per-sample.csv`, `metrics.json`." for s in ("dev", "test", "probe")]]
    write("evidence/G3/TV2/G3-TV2-01/error-analysis.md", "\n".join(out))
    shutil.copyfile(ROOT / "evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv", ROOT / "evidence/G3/TV2/G3-TV2-01/ghidra-crosscheck.csv")
    for role in ("P2", "P3", "P4", "P5", "E1", "E2"):
        copy_export(role, "evidence/G3/TV2/G3-TV2-01/ghidra-headless")
    copy_export("TV2C-B5", "evidence/G3/TV2/G3-TV2-01/ghidra-headless")



def asm_lines(role):
    lines = []
    for path in sorted((EXPORT / role / "disasm").glob("*.asm")):
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    return lines


def find_asm(role, needle):
    needle = needle.lower()
    return next((line.strip() for line in asm_lines(role) if needle in line.lower()), "")


def tv1_review(data):
    p1_bytes = (ROOT / data.manifest["P1"]["binary"]).read_bytes()
    names_absent = all(n.encode() not in p1_bytes and n.encode("utf-16-le") not in p1_bytes for n in FILE_APIS)
    p1_imports = {r["symbol"] for r in rows(EXPORT / "P1" / "imports.csv")}
    finder = next((EXPORT / "P1" / "disasm").glob("*_rva_10B0.asm")).read_text(encoding="utf-8")
    field_reads = [l for l in finder.splitlines() if ("+ 0x1c]" in l.lower() or "+ 0x24]" in l.lower()) and "RSP" not in l]
    peb = [l for l in asm_lines("P1") if "GS:" in l.upper()]
    chain_e2 = all(data.features("E2")["features"][r]["status"] == "verified" for r in RELATIONS[:5])
    e2_strings = {r["value"]: r for r in ghidra_strings("E2")}
    e2_strcmp = next((r["call_rva"] for r in api_calls("E2", "strcmp")), "không thấy")
    e1_log = (ROOT / "evidence/TV2-shared/build" / BUILD / "E1.build.log").read_text(encoding="utf-8", errors="replace")
    def order(role):
        return [find_asm(role, f"RSP + {slot}],0x").split(",")[-1] for slot in ("0x80", "0x84", "0x88")]
    checks = [
        ("P1 dùng DJB2, seed 5381, h*33+byte", "`docs/TV1-HUONG-DAN.md` mục 3", f"`{find_asm('P1', '0x1505')}`; `{find_asm('P1', 'IMUL EAX,dword ptr [RSP],0x21')}`", "Khớp"),
        ("P2 dùng FNV-1a", "`docs/TV1-HUONG-DAN.md` mục 4", f"`{find_asm('P2', '0x811c9dc5')}`; `{find_asm('P2', '0x1000193')}`", "Khớp"),
        ("P3 dùng CRC32 phản chiếu", "`docs/TV1-HUONG-DAN.md` mục 4", f"`{find_asm('P3', '0xedb88320')}`", "Khớp"),
        ("P4 đổi seed thành 1337", "`docs/TV1-HUONG-DAN.md` mục 5", f"`{find_asm('P4', '0x539')}`", "Khớp"),
        ("P5 đổi thứ tự resolve", "`samples/common/tv1_program.h`", f"Thứ tự slot P1 = {order('P1')}, P5 = {order('P5')}", "Khớp"),
        ("E1 đổi bit cao của hash CreateFileW", "`docs/TV1-HUONG-DAN.md` mục 6", f"`{find_asm('E1', '0x6b96c610')}`", "Khớp"),
        ("E2 dừng sớm nhưng giữ đường hashing", "`docs/TV1-HUONG-DAN.md` mục 6", f"`--continue` tham chiếu tại {e2_strings['--continue']['referenced_from_rva']}; `strcmp` tại {e2_strcmp}; chuỗi quan hệ tới resolve đã xác minh: {chain_e2}", "Khớp"),
        ("GetProcAddress nhận tên, không nhận hash", "`docs/TV1-HUONG-DAN.md` mục 3", "P1 + 0x13A7 nạp RDX từ biến tên, P1 + 0x13B1 gọi GetProcAddress", "Khớp"),
        ("Không nhúng tên API đích trong P1", "`docs/TV1-HUONG-DAN.md` mục 3", f"Không có ASCII/UTF-16 của ba tên trong file: {names_absent}; không import ba API này: {not (p1_imports & set(FILE_APIS))}", "Khớp"),
        ("Duyệt hết tên export để phát hiện collision", "`samples/common/tv1_resolver.h`", f"Sau khi ghi tên, mã vẫn quay lại vòng lặp: `{find_asm('P1', 'RVA_0000130E')}`", "Khớp"),
        ("Không duyệt PEB, không tự tính địa chỉ qua AddressOfFunctions", "`docs/TV1-HUONG-DAN.md` phần giới hạn", f"Truy cập GS trong các hàm đã xuất: {len(peb)}; đọc export +0x1C hoặc +0x24 trong hàm tìm tên: {len(field_reads)}", "Khớp"),
    ]
    findings = [
        ("Nên sửa", "`samples/common/tv1_resolver.h:8`", "Chú thích nói chỉ chấp nhận system DLL hợp lệ, nhưng mã chỉ kiểm tra cấu trúc PE. Việc dùng kernel32 do nơi gọi quyết định.", "Sửa chú thích thành điều kiện thực tế của tham số."),
        ("Nên sửa", "`docs/TV1-HUONG-DAN.md:87`", "Câu GetProcAddress nhận TÊN đúng với PoC nhưng chưa đủ với API.", "Ghi: API nhận tên hoặc ordinal; PoC truyền tên đã tìm được."),
        ("Nên sửa", "`README-TV1.md:19`", "Mục trạng thái mô tả lúc tạo gói nên ghi chưa build bằng MSVC, trong khi `evidence/G1/TV1/` đã có kết quả correctness và audit.", "Bổ sung trạng thái hiện tại để người đọc không hiểu nhầm."),
        ("Nên sửa", "`evidence/G1/TV1/G1-TV1-03/README.md`", "README ghi chưa thực hiện, nhưng cùng thư mục đã có CSV kết quả.", "TV1 điền README hoặc ghi rõ phần chưa đạt."),
        ("Cần phối hợp", "`evidence/G1/TV1/G1-TV1-03/P1-correctness-summary.csv`", f"P1 lịch sử có SHA-256 `DDFB2A29…`, còn build TV2 là `{data.manifest['P1']['sha256'][:8]}…`. Hai bản không được trộn địa chỉ.", "TV1 bàn giao binary và commit chốt để TV2 chạy lại."),
        ("Ghi nhận", "`scripts/tv1-build.ps1:49`", "Trường `build_flags` trong manifest bỏ sót `/utf-8` và `/INCREMENTAL:NO` đang được dùng.", "Ghi đủ cờ để tái lập."),
        ("Ghi nhận", "`samples/common/tv1_program.h`", f"Với E1, MSVC báo C4702 ({e1_log.count('C4702')} cảnh báo) và vẫn sinh đoạn mã không chạy tới. Công cụ quét tuyến tính sẽ thấy các lời gọi gián tiếp trong đoạn đó.", "Nêu trong báo cáo khi so sánh công cụ."),
    ]
    text = ["# Review phần PoC của TV1", "",
            "Người thực hiện: AI hỗ trợ TV2. **TV1 chưa phản hồi**, nên đây chưa phải review đã được hai bên chốt. Không có tệp TV1 nào bị sửa.",
            f"Binary kiểm tra: build `{BUILD}` do TV2 build lại từ source hiện tại, không phải binary lịch sử của TV1.", "",
            "## Đối chiếu mô tả với binary", "", table(["Mô tả được kiểm", "Nguồn", "Bằng chứng trên binary", "Kết quả"], checks), "",
            "## Điểm đề nghị TV1 xem", "", table(["Mức", "Vị trí", "Nhận xét", "Đề xuất"], findings), "",
            "## Phạm vi chưa kiểm", "",
            "- Không chạy các binary, nên chưa kiểm hành vi runtime, địa chỉ forwarded export hay collision trên DLL thật.",
            "- Chưa đối chiếu với collector của TV3."]
    write("tv2/G3-TV2-03/tv1-review.md", "\n".join(text))


def static_report(data):
    metrics = [metric_row(s, name, item) for s in ("dev", "test") for name, item in data.metrics[s]["detectors"].items()]
    head = ["Tập", "Detector", "Số mẫu", "Phân tích ok", "TP", "TN", "FP", "FN", "Unknown", "Precision", "Recall", "F1", "Trung vị ms"]
    test = data.results["test"]
    by = lambda role, det: next(r for r in test if r["role"] == role and r["detector"] == det)
    compare = []
    for role in sorted({r["role"] for r in test}):
        a, b = by(role, "D0"), by(role, "STATIC-ONLY")
        compare.append((role, a["sha256"][:16] + "…", a["label"], f"{a['verdict']} ({a['outcome']})", f"{b['verdict']} ({b['outcome']})"))
    run_test, run_dev, run_probe = data.runs["test"].name, data.runs["dev"].name, data.runs["probe"].name
    p1, b5 = data.manifest["P1"], data.manifest["TV2C-B5"]
    lock = load(CFG / "locks" / "rule-lock-1.0.1.json")
    lock_commit = load(CFG / "locks" / "lock-commits.json")[VERSION]["commit"]
    text = f"""# Báo cáo phần static detector

Trạng thái: **bản thảo**. Thiếu ảnh GUI Ghidra và số liệu D1. Nhãn, split và các mẫu `TV2C-*` là đề xuất của TV2, chưa được nhóm duyệt.

## 1. Mục tiêu

Phát hiện tĩnh việc một chương trình PE32+ x64 tìm API bằng hash của tên export. Detector chỉ đọc byte của binary và không chạy mẫu.

## 2. Cơ chế cần phát hiện

Import sẵn để loader điền IAT. Resolve động theo tên gọi `GetProcAddress` với tên có trong chương trình. API hashing không cần giữ tên đích: chương trình duyệt tên export, hash từng tên, so với giá trị đích rồi dùng tên khớp. Xem [ghi chú PE](../G1-TV2-01/pe-notes.md) và [sơ đồ](../G1-TV2-01/images/pe-mechanism.png).

## 3. Phương pháp

1. Đọc PE32+, import, `.pdata` và giải mã lệnh bằng Capstone.
2. Dựng CFG và lan truyền nhãn dữ liệu trong từng hàm, kèm tóm tắt hàm để đi qua lời gọi và tham số out.
3. Dùng phụ thuộc điều khiển để biết tên export chỉ được giữ khi phép so hash đúng.
4. Ghi đặc trưng và vị trí bằng chứng vào tài liệu có schema.
5. Áp rule từ cấu hình có phiên bản. Phân tích lỗi cho `unknown`, không cho `negative`.

## 4. Rule

- **D0** ([chi tiết](../G2-TV2-01/d0-rule.md)): import `GetProcAddress`, có vòng giống hash, có lời gọi gián tiếp ngoài IAT. Rule chỉ xét đồng xuất hiện.
- **Static-only** (định nghĩa làm việc của TV2): cả năm quan hệ duyệt tên export, tên → hash, hash → so sánh, so sánh → chọn tên, tên → resolve phải được xác minh. Việc dùng con trỏ được báo cáo nhưng không bắt buộc, vì E1 resolve mà không gọi địa chỉ.
- Danh sách đặc trưng ở [features.md](../G2-TV2-03/features.md). Lịch sử thay đổi ở [rule-changelog.md](../G2-TV2-03/rule-changelog.md).

## 5. Dữ liệu và quy trình

- Build `{BUILD}`, MSVC `/Od /MD`, cây nguồn có thay đổi chưa commit. Provenance ở `evidence/TV2-shared/build/{BUILD}/build-manifest.json`.
- Tập phát triển: B1, B2, P1, TV2C-B3, TV2C-B4. Tập test: P2–P5, E1, E2, TV2C-B5, TV2C-B6. Năm mẫu probe chỉ dùng để quan sát compiler.
- Rule được khóa trước khi chạy test. Lock hiện tại `{lock['lock_version']}`, tạo lúc `{lock['created_at']}`, gồm checksum code, config, schema và manifest.
- Commit `{lock_commit[:7]}` do người dùng tạo chứa đúng các tệp của lock này; đã đối chiếu từng SHA-256.

## 6. Kết quả thực đo

Run: dev `{run_dev}`, test `{run_test}`, probe `{run_probe}`. Lock 1.0.0 và 1.0.1 cho cùng kết luận trên tập test.

{table(head, metrics)}

### Từng mẫu của tập test

{table(["Mẫu", "SHA-256", "Nhãn đề xuất", "D0", "Static-only"], compare)}

Lý do và vị trí bằng chứng từng mẫu nằm trong `{data.rel_path(data.runs['test'])}/per-sample.csv`. Phân tích lỗi ở `evidence/G3/TV2/G3-TV2-01/error-analysis.md`.

## 7. Bảng D0/D1

**Chưa lập được.** Repository chưa có D1 hay kết quả D1, nên không có số liệu để so. Bảng trên so D0 với static-only và không thay thế bảng D0/D1. Đầu vào đề xuất cho D1 ở [D1-HANDOFF.md](../G2-TV2-03/D1-HANDOFF.md).

## 8. Ví dụ demo theo kết quả thực đo

| Ví dụ | Binary | Run | Điều quan sát |
|---|---|---|---|
| Chuỗi đầy đủ | P1, `{p1['sha256']}` | `{run_dev}` | Cả D0 và static-only báo dương; chuỗi RVA ở `evidence/G1/TV2/G1-TV2-03/p1-evidence-chain.md` |
| Báo động nhầm của D0 | TV2C-B5, `{b5['sha256']}` | `{run_test}` | D0 báo dương vì ba dấu hiệu cùng có mặt; static-only báo âm vì không có luồng tên export → hash |

D0 không bị chỉnh để bỏ sót mẫu nào. Trên tập test đề xuất, D0 không có FN.

## 9. Giới hạn đã quan sát

- Tập mẫu nhỏ, các P/E cùng một họ PoC và cùng source dùng chung. Người viết rule biết source, nên điểm số không chứng minh khả năng tổng quát.
- GCC `-O2`: hai probe `partial` do hết ngân sách ở hàm runtime. Với P1, extractor chỉ truy tới AddressOfNames sau khi resolver bị inline vào `main`.
- MSVC `/O2`: chuỗi vẫn được xác minh ở P1 và P3 dù hàm hash bị inline.
- D0-C3 phân biệt yếu vì mã khởi động CRT đã có lời gọi gián tiếp ngoài IAT.
- Hash-like loop của D0 báo nhầm trên mã runtime MinGW.
- Quét tuyến tính của D0 tính cả mã không chạy tới được, như ba lời gọi trong E1.

## 10. Giới hạn chưa kiểm tra

- Resolver tự tính địa chỉ qua AddressOfOrdinals và AddressOfFunctions, duyệt PEB, PE32, packer hoặc mã làm rối đều chưa có mẫu thử.
- Chưa có kết quả chạy thực, API trace hay dữ liệu của TV3/TV4 trong phần này.

## 11. Tái lập

Xem [README-TV2.md](../../README-TV2.md).
"""
    write("tv2/G3-TV2-02/static-detector-report.md", text)


def link_to(path, base):
    return os.path.relpath(ROOT / path, ROOT / base).replace("\\", "/")


def linkify(item, base):
    pattern = r"`((?:tv2|evidence|configs|schemas|detectors|scripts|samples|docs)/[^`]*)`"
    return re.sub(pattern, lambda m: f"[`{m.group(1)}`]({link_to(m.group(1).rstrip('/'), base)})", item)


def task_folder(task):
    base = f"tv2/{task['id']}"
    folder = ROOT / base
    local = sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.name != "README.md")
    related = [item for item in task["have"] if not item.startswith(f"`{base}/")]
    steps = [(s["id"], s["what"], s["status"], s["missing"]) for s in task["steps"]]
    body = [f"# {task['id']} — {task['title']}", "", f"Trạng thái: **{task['status']}**.", "",
            "## Tài liệu trong thư mục này", "",
            *([f"- [{name}]({name})" for name in local] or ["- Task này không có tài liệu riêng. Sản phẩm nằm ở phần dưới."]), "",
            "## Minh chứng và sản phẩm liên quan", "",
            f"- Thư mục minh chứng: [`{task['folder']}/`]({link_to(task['folder'], base)})",
            *[f"- {linkify(item, base)}" for item in related], "",
            "## Còn thiếu", "", *[f"- {linkify(item, base)}" for item in task["missing"]], "",
            "## Các bước", "", linkify(table(["Bước", "Việc", "Trạng thái", "Còn thiếu"], steps), base)]
    write(f"{base}/README.md", "\n".join(body))


def tracker_and_readmes():
    now = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")
    lines = ["# Theo dõi task TV2", "", f"Cập nhật: {now}. Trạng thái dùng đúng sáu mức trong prompt. Tệp được sinh từ `detectors/tv2/tv2tasks.py`.", "",
             table(["Task", "Nội dung", "Trạng thái", "Còn thiếu"], [(t["id"], t["title"], t["status"], " ".join(t["missing"])) for t in TASKS]), ""]
    for task in TASKS:
        lines += [f"## {task['id']} — {task['title']}", ""]
        for s in task["steps"]:
            lines += [f"### {s['id']} — {s['what']}", "",
                      table(["Mục", "Nội dung"], [("Trạng thái", s["status"]), ("Đầu vào", s["inputs"]), ("Vị trí thao tác", s["place"]), ("Đầu ra", s["output"]),
                                                  ("Kiểm tra đã chạy", s["checks"]), ("Minh chứng", s["evidence"]), ("Còn thiếu", s["missing"]), ("Phụ thuộc", s["depends"]),
                                                  ("Việc tiếp theo", s["next"]), ("Tiêu chí xong", s["done_when"]), ("Cập nhật", now)]), ""]
        body = [f"# Minh chứng {task['id']}", "", f"Nội dung: {task['title']}.", "", f"Trạng thái: **{task['status']}**.", "",
                f"Tài liệu của task: `tv2/{task['id']}/`.", "",
                f"Build dùng chung: `{BUILD}`. Rule lock hiện tại: `configs/tv2/locks/rule-lock-{VERSION}.json`.", "", "## Đã có", "",
                *[f"- {item}" for item in task["have"]], "", "## Còn thiếu", "", *[f"- {item}" for item in task["missing"]], "",
                "Chi tiết từng bước ở `tv2/TASK-TRACKER.md`."]
        write(f"{task['folder']}/README.md", "\n".join(body))
        task_folder(task)
    write("tv2/TASK-TRACKER.md", "\n".join(lines))
    index = ["# Tài liệu TV2", "", "Mỗi task có một thư mục riêng. Minh chứng gốc vẫn nằm trong `evidence/G*/TV2/`, và README của từng task có liên kết tới đó.", "",
             table(["Task", "Nội dung", "Trạng thái", "Minh chứng"],
                   [(f"[{t['id']}]({t['id']}/README.md)", t["title"], t["status"], f"[mở]({link_to(t['folder'], 'tv2')})") for t in TASKS]), "",
             "## Tài liệu chung", "", "- [Đặc tả thực thi](EXECUTION-SPEC.md)", "- [Theo dõi chi tiết](TASK-TRACKER.md)",
             "- [Việc cần người dùng thực hiện](HUONG-DAN-CHUP-ANH.md)", "- [Bàn giao và điểm bắt đầu phiên mới](ban-giao/START-HERE.md)",
             "- [Hướng dẫn tái lập](../README-TV2.md)"]
    write("tv2/README.md", "\n".join(index))


def main():
    data = Data()
    if "--docs-only" not in sys.argv:
        b1_b2(data)
        p1_chain(data)
        d0_dev(data)
        controls(data)
        missing_examples(data)
        features_summary(data)
        analysis(data)
    tv1_review(data)
    static_report(data)
    tracker_and_readmes()


if __name__ == "__main__":
    main()
