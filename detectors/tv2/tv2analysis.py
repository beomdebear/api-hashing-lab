"""Static x86-64 analysis for the TV2 detector.

Two independent layers are produced from the binary bytes only:

* ``signals``: simple syntactic observations used by the D0 baseline.
* ``events``: data-flow / control-dependence facts for the relation chain
  export name -> hash -> compare -> name selection -> resolve -> pointer use.

The data-flow layer is a forward tag analysis over each function's CFG, with
function summaries so that values can cross calls and out-parameters.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from capstone import CS_ARCH_X86, CS_MODE_64, CS_OPT_SYNTAX_INTEL, Cs
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

from tv2pe import PeFile

EMPTY = frozenset()
ARG_REGS = ("rcx", "rdx", "r8", "r9")
VOLATILE = ("rax", "rcx", "rdx", "r8", "r9", "r10", "r11")
ARG_TAGS = ("A0", "A1", "A2", "A3")
MAX_TAGS = 48
ARRAY_WINDOW = 0x100
MAX_FUNCTION_INSNS = 20000
MAX_BLOCK_VISITS = 4000
MAX_FUNCTION_BLOCKS = 1500
MAX_SUMMARY_ROUNDS = 8
LOADER_APIS = ("LoadLibraryA", "LoadLibraryW", "LoadLibraryExA", "LoadLibraryExW",
               "GetModuleHandleA", "GetModuleHandleW", "GetModuleHandleExA", "GetModuleHandleExW")
MOV_LIKE = {"mov", "movzx", "movsx", "movsxd", "movabs", "movups", "movaps", "movdqu",
            "movdqa", "movq", "movd", "movss", "movsd"}
COMBINE_OPS = {"add", "xor", "or", "sub"}
MIX_OPS = {"add", "xor", "imul", "mul", "rol", "ror", "shl", "sal"}
ARITH_OPS = {"add", "sub", "and", "or", "xor", "imul", "mul", "shl", "sal", "shr", "sar",
             "rol", "ror", "adc", "sbb", "not", "neg", "inc", "dec", "bswap"}
FLAG_OPS = {"cmp", "test", "sub", "xor"}
RVA_PROMOTION = {"E_LFANEW": "NT", "EXP_RVA": "EXP_DIR", "NAMES_RVA": "NAMES_ARR", "NAME_RVA": "NAME_PTR"}
EXPORT_FIELDS = {0x18: "NUM_NAMES", 0x20: "NAMES_RVA"}
ROOT_RE = re.compile(r"^(H|B|API)\((.+)\)$")

_REG_CANON = {}
for _full, _names in {
    "rax": "eax ax al ah", "rbx": "ebx bx bl bh", "rcx": "ecx cx cl ch", "rdx": "edx dx dl dh",
    "rsi": "esi si sil", "rdi": "edi di dil", "rbp": "ebp bp bpl", "rsp": "esp sp spl",
}.items():
    _REG_CANON[_full] = _full
    for _name in _names.split():
        _REG_CANON[_name] = _full
for _n in range(8, 16):
    for _suffix in ("", "d", "w", "b"):
        _REG_CANON[f"r{_n}{_suffix}"] = f"r{_n}"


def canon(reg: str) -> str:
    return _REG_CANON.get(reg, reg)


@dataclass(frozen=True)
class Op:
    kind: str                # r, i, m
    reg: str = ""
    imm: int = 0
    base: str = ""
    index: str = ""
    scale: int = 1
    disp: int = 0
    size: int = 0


@dataclass
class Ins:
    addr: int
    size: int
    mn: str
    ops: tuple
    text: str

    @property
    def next(self) -> int:
        return self.addr + self.size


@dataclass
class Block:
    start: int
    insns: list = field(default_factory=list)
    succs: list = field(default_factory=list)
    preds: list = field(default_factory=list)


@dataclass
class Function:
    rva: int
    end: int
    insns: list
    blocks: dict = field(default_factory=dict)
    loop_blocks: set = field(default_factory=set)
    control_deps: dict = field(default_factory=dict)
    has_indirect_jump: bool = False
    truncated: bool = False


@dataclass
class Summary:
    ret: frozenset = EMPTY
    writes: dict = field(default_factory=dict)
    gpa_sinks: frozenset = EMPTY

    def key(self):
        return (self.ret, tuple(sorted((k, v) for k, v in self.writes.items())), self.gpa_sinks)


class Analyzer:
    def __init__(self, pe: PeFile):
        self.pe = pe
        self.events = {}
        self.incomplete = []
        self.functions = {}
        self.thunks = {}
        self.summaries = {}
        self.md = Cs(CS_ARCH_X86, CS_MODE_64)
        self.md.detail = True
        self.md.syntax = CS_OPT_SYNTAX_INTEL

    # ---- decoding and function discovery -------------------------------------------------
    def _decode(self, rva: int, end: int):
        code = self.pe.read_rva(rva, end - rva)
        out = []
        for raw in self.md.disasm(code, self.pe.va(rva)):
            ops = []
            for op in raw.operands:
                if op.type == X86_OP_REG:
                    ops.append(Op("r", reg=canon(raw.reg_name(op.reg)), size=op.size))
                elif op.type == X86_OP_IMM:
                    ops.append(Op("i", imm=op.imm, size=op.size))
                elif op.type == X86_OP_MEM:
                    base = raw.reg_name(op.mem.base) if op.mem.base else ""
                    index = raw.reg_name(op.mem.index) if op.mem.index else ""
                    ops.append(Op("m", base=canon(base or ""), index=canon(index or ""),
                                  scale=op.mem.scale, disp=op.mem.disp, size=op.size))
            out.append(Ins(raw.address - self.pe.image_base, raw.size, raw.mnemonic,
                           tuple(ops), f"{raw.mnemonic} {raw.op_str}".strip()))
            if len(out) >= MAX_FUNCTION_INSNS:
                self.incomplete.append({"function_rva": rva, "reason": "instruction_budget"})
                break
        return out

    def discover(self):
        ranges = dict(self.pe.runtime_functions)
        starts = sorted(ranges)
        pending = list(starts)
        if self.pe.section_of(self.pe.entry_rva) is not None and self.pe.entry_rva not in ranges:
            pending.append(self.pe.entry_rva)
        seen = set()
        while pending:
            rva = pending.pop()
            if rva in seen:
                continue
            seen.add(rva)
            section = self.pe.section_of(rva)
            if section is None or not section.executable:
                continue
            end = ranges.get(rva)
            limit = section.rva + section.mapped_size
            if end is None:
                later = [s for s in starts if s > rva]
                end = min(later[0] if later else limit, rva + 0x4000, limit)
            insns = self._decode(rva, end)
            if rva not in ranges:
                insns = _cut_at_terminator(insns)
                end = insns[-1].next if insns else rva
            self.functions[rva] = Function(rva, end, insns)
            for ins in insns:
                if ins.mn == "call" and ins.ops and ins.ops[0].kind == "i":
                    pending.append(ins.ops[0].imm - self.pe.image_base)
        for fn in self.functions.values():
            first = fn.insns[0] if fn.insns else None
            if first is not None and first.mn == "jmp":
                target = self._iat_target(first, first.ops[0]) if first.ops else None
                if target:
                    self.thunks[fn.rva] = target
            _build_cfg(fn, self.pe.image_base)
            if len(fn.blocks) > MAX_FUNCTION_BLOCKS:
                self.incomplete.append({"function_rva": fn.rva, "reason": "block_count_budget"})

    def _rip_rva(self, ins: Ins, op: Op) -> int:
        return ins.next + op.disp

    def _iat_target(self, ins: Ins, op: Op):
        if op.kind == "m" and op.base == "rip" and not op.index:
            entry = self.pe.iat.get(self._rip_rva(ins, op))
            return entry.name if entry else None
        return None

    # ---- events --------------------------------------------------------------------------
    def emit(self, kind: str, fn: Function, ins: Ins, note: str = "", via=None):
        key = (kind, ins.addr, note)
        if key in self.events:
            return
        offset = self.pe.rva_to_offset(ins.addr)
        item = {
            "kind": kind, "function_rva": fn.rva, "rva": ins.addr, "va": self.pe.va(ins.addr),
            "file_offset": offset, "text": ins.text, "note": note,
        }
        if via is not None:
            item["via_call_rva"] = via
        self.events[key] = item

    # ---- data-flow -----------------------------------------------------------------------
    def run(self):
        self.discover()
        for rva in self.functions:
            self.summaries[rva] = Summary()
        for _ in range(MAX_SUMMARY_ROUNDS):
            changed = False
            for rva in sorted(self.functions):
                fn = self.functions[rva]
                if rva in self.thunks or not fn.blocks:
                    continue
                new = FunctionFlow(self, fn).solve()
                if new.key() != self.summaries[rva].key():
                    self.summaries[rva] = new
                    changed = True
            if not changed:
                break
        else:
            self.incomplete.append({"function_rva": None, "reason": "summary_round_budget"})
        return self


class FunctionFlow:
    def __init__(self, az: Analyzer, fn: Function):
        self.az = az
        self.fn = fn
        self.ret = set()
        self.writes = defaultdict(set)
        self.gpa = set()
        self.compare_blocks = set()
        self.guarded = set()

    def solve(self) -> Summary:
        for _ in range(4):
            self._fixpoint()
            guarded = set()
            for block in self.compare_blocks:
                guarded |= self.fn.control_deps.get(block, set())
            if guarded <= self.guarded:
                break
            self.guarded |= guarded
        return Summary(_clean(self.ret), {k: _clean(v) for k, v in self.writes.items()},
                       frozenset(self.gpa))

    def _fixpoint(self):
        entry = {reg: frozenset({tag}) for reg, tag in zip(ARG_REGS, ARG_TAGS)}
        entry["rsp"] = frozenset({"SP:0"})
        inputs = {self.fn.rva: entry}
        work = [self.fn.rva]
        visits = 0
        while work:
            start = min(work)
            work.remove(start)
            visits += 1
            if visits > MAX_BLOCK_VISITS:
                self.az.incomplete.append({"function_rva": self.fn.rva, "reason": "block_visit_budget"})
                return
            block = self.fn.blocks[start]
            state = dict(inputs.get(start, {}))
            for ins in block.insns:
                self._step(ins, block, state)
            for succ in block.succs:
                merged, changed = _join(inputs.get(succ), state)
                if changed:
                    inputs[succ] = merged
                    if succ not in work:
                        work.append(succ)

    # ---- operand helpers -----------------------------------------------------------------
    def _reg(self, state, reg):
        return state.get(reg, EMPTY)

    def _address(self, state, ins, op):
        """Return (stack slots, array bases, pointer tags, effective displacement, dynamic)."""
        base = self._reg(state, op.base) if op.base and op.base != "rip" else EMPTY
        index = self._reg(state, op.index) if op.index else EMPTY
        constant = _const(index)
        disp = op.disp
        dynamic = bool(op.index)
        if op.index and constant is not None:
            disp += constant * op.scale
            dynamic = False
        slots, arrays = [], []
        for tag in base | (index if op.index and op.scale == 1 else EMPTY):
            if tag.startswith("SP:"):
                offset = int(tag[3:]) + disp
                (arrays if dynamic else slots).append(offset)
            elif tag.startswith("SPA:"):
                arrays.append(int(tag[4:]) + disp)
        pointer = _combine(base, index) if op.index and constant is None else base
        return slots, arrays, pointer, disp, dynamic

    def _read_slot(self, state, offset):
        value = set(state.get(f"S:{offset}", EMPTY))
        for key, tags in state.items():
            if key.startswith("SA:") and 0 <= offset - int(key[3:]) < ARRAY_WINDOW:
                value |= tags
        return frozenset(value)

    def _read_mem(self, state, ins, op):
        if op.base == "rip":
            entry = self.az.pe.iat.get(self.az._rip_rva(ins, op))
            return frozenset({f"IMP:{entry.name}"}) if entry else EMPTY
        slots, arrays, pointer, disp, dynamic = self._address(state, ins, op)
        result = set()
        for offset in slots:
            result |= self._read_slot(state, offset)
        for offset in arrays:
            result |= self._read_slot(state, offset)
            result |= state.get(f"SA:{offset}", EMPTY)
        if slots or arrays:
            return _cap(result)
        fn, emit = self.fn, self.az.emit
        if op.size == 4 and disp == 0x3C and op.base:
            result.add("E_LFANEW")
        if "NT" in pointer and disp == 0x88 and op.size in (4, 8):
            result.add("EXP_RVA")
            emit("export_directory_read", fn, ins, "read of NT headers +0x88 (PE32+ export directory RVA)")
        if "EXP_DIR" in pointer and disp in EXPORT_FIELDS and op.size == 4:
            result.add(EXPORT_FIELDS[disp])
            if disp == 0x20:
                emit("export_names_field_read", fn, ins, "read of export directory +0x20 (AddressOfNames)")
        if "NAMES_ARR" in pointer and op.index and op.size == 4:
            result.add("NAME_RVA")
            emit("export_name_rva_read", fn, ins, "indexed read from AddressOfNames")
        if op.size == 1:
            for tag in pointer:
                if tag in ARG_TAGS or tag in ("NAME_PTR", "SEL"):
                    result.add(f"B({'NAME_PTR' if tag == 'SEL' else tag})")
        if op.index:
            for tag in self._reg(state, op.index):
                if tag.startswith(("B(", "H(")):
                    result.add(tag)
        return _cap(result)

    def _value(self, state, ins, op):
        if op.kind == "r":
            return self._reg(state, op.reg)
        if op.kind == "i":
            return frozenset({f"C:{op.imm}"})
        return self._read_mem(state, ins, op)

    def _store(self, state, ins, op, value, block):
        value = self._guard(value, ins, block)
        if op.kind == "r":
            if value:
                state[op.reg] = _cap(value)
            else:
                state.pop(op.reg, None)
            return
        if op.kind != "m" or op.base == "rip":
            return
        slots, arrays, pointer, _, _ = self._address(state, ins, op)
        if len(slots) == 1 and not arrays:
            key = f"S:{slots[0]}"
            if value:
                state[key] = _cap(value)
            else:
                state.pop(key, None)
            return
        for offset in slots:
            state[f"S:{offset}"] = _cap(state.get(f"S:{offset}", EMPTY) | value)
        for offset in arrays:
            state[f"SA:{offset}"] = _cap(state.get(f"SA:{offset}", EMPTY) | value)
        if slots or arrays:
            return
        for tag in pointer:
            if tag in ARG_TAGS and value:
                self.writes[int(tag[1])] |= set(value)

    def _guard(self, value, ins, block):
        if "NAME_PTR" in value and block.start in self.guarded:
            self.az.emit("name_selected_by_hash", self.fn, ins,
                         "export-name pointer is assigned only when the hash comparison selects it")
            return value | {"SEL"}
        return value

    # ---- instruction transfer ------------------------------------------------------------
    def _step(self, ins, block, state):
        mn, ops = ins.mn, ins.ops
        if mn in MOV_LIKE or mn.startswith("cmov"):
            if len(ops) == 2:
                value = self._value(state, ins, ops[1])
                if mn.startswith("cmov"):
                    value |= self._value(state, ins, ops[0])
                self._store(state, ins, ops[0], value, block)
        elif mn == "lea":
            self._lea(ins, block, state)
        elif mn == "push":
            self._shift_sp(state, -8)
            if ops:
                self._store_slot_at_sp(state, self._value(state, ins, ops[0]))
        elif mn == "pop":
            value = self._read_slot(state, _sp(state)) if _sp(state) is not None else EMPTY
            if ops:
                self._store(state, ins, ops[0], value, block)
            self._shift_sp(state, 8)
        elif mn == "call":
            self._call(ins, block, state)
        elif mn == "jmp":
            self._jump(ins, block, state)
        elif mn == "ret":
            self.ret |= set(self._reg(state, "rax"))
        elif mn in ("cmp", "test"):
            self._compare(ins, block, state)
        elif mn in ARITH_OPS:
            self._arith(ins, block, state)
        elif ops and ops[0].kind == "r" and mn not in ("nop", "endbr64", "int3"):
            state.pop(ops[0].reg, None)

    def _lea(self, ins, block, state):
        dst, mem = ins.ops
        if mem.base == "rip":
            self._store(state, ins, dst, frozenset({f"G:{self.az._rip_rva(ins, mem)}"}), block)
            return
        base = self._reg(state, mem.base) if mem.base else EMPTY
        index = self._reg(state, mem.index) if mem.index else EMPTY
        constant = _const(index)
        disp = mem.disp + (constant * mem.scale if mem.index and constant is not None else 0)
        dynamic = bool(mem.index) and constant is None
        out = set()
        for tag in base:
            if tag.startswith("SP:"):
                out.add(f"{'SPA' if dynamic else 'SP'}:{int(tag[3:]) + disp}")
            elif tag.startswith("SPA:"):
                out.add(f"SPA:{int(tag[4:]) + disp}")
            elif tag.startswith("C:"):
                out.add(f"C:{int(tag[2:]) + disp}")
            else:
                out.add(tag)
        if dynamic:
            out |= _combine(frozenset(t for t in base if not t.startswith(("SP:", "SPA:"))), index)
        self._promotion_event(base, index, ins, bool(mem.index))
        self._store(state, ins, dst, frozenset(out), block)

    def _promotion_event(self, left, right, ins, both):
        if both and (("NAME_RVA" in left) or ("NAME_RVA" in right)):
            self.az.emit("export_name_pointer", self.fn, ins, "module base + name RVA gives an export-name pointer")

    def _arith(self, ins, block, state):
        mn, ops = ins.mn, ins.ops
        if not ops:
            return
        dst = ops[0]
        if mn in ("mul", "imul") and len(ops) == 1:
            ops = (Op("r", reg="rax", size=ops[0].size), ops[0])
            dst = ops[0]
        if mn == "xor" and len(ops) == 2 and ops[0] == ops[1]:
            self._store(state, ins, dst, frozenset({"C:0"}), block)
            return
        left = self._value(state, ins, dst)
        right = self._value(state, ins, ops[1]) if len(ops) > 1 else EMPTY
        third = ops[2] if len(ops) > 2 else None
        if mn == "imul" and third is not None:
            left, right = right, frozenset({f"C:{third.imm}"})
        if dst.kind == "r" and dst.reg == "rsp":
            step = {"sub": -1, "add": 1}.get(mn)
            amount = _const(right)
            if step and amount is not None:
                self._shift_sp(state, step * amount)
            return
        result = self._arith_value(mn, left, right, ops, ins, block)
        self._mix(mn, left, right, ops, ins, block, result)
        if mn in FLAG_OPS and len(ops) == 2:
            self._compare_values(ins, block, left, right, ops)
        self._store(state, ins, dst, _cap(result), block)

    def _arith_value(self, mn, left, right, ops, ins, block):
        lconst, rconst = _const(left), _const(right)
        if lconst is not None and rconst is not None:
            value = _fold_constant(mn, lconst, rconst)
            if value is not None:
                return {f"C:{value}"}
        if mn == "add":
            if ops[1].kind == "i" or rconst is not None:
                return {_adjust(t, rconst) for t in left}
            self._promotion_event(left, right, ins, True)
            return set(_combine(left, right))
        if mn in ("inc", "dec"):
            return {_adjust(t, 1 if mn == "inc" else -1) for t in left}
        if mn == "sub" and rconst is not None:
            return {_adjust(t, -rconst) for t in left}
        keep = lambda tag: tag in ARG_TAGS or tag.startswith(("B(", "H("))
        return {t for t in left | right if keep(t)}

    def _mix(self, mn, left, right, ops, ins, block, result):
        if block.start not in self.fn.loop_blocks or mn not in MIX_OPS:
            return
        has_immediate = len(ops) > 1 and ops[-1].kind == "i"
        if mn in COMBINE_OPS and has_immediate:
            return
        if mn in ("shl", "sal", "rol", "ror") and not any(t.startswith("H(") for t in left):
            return
        for tag in left | right:
            match = ROOT_RE.match(tag)
            if match and match.group(1) in ("B", "H"):
                created = f"H({match.group(2)})"
                result.add(created)
                if created == "H(NAME_PTR)":
                    self.az.emit("export_name_hashed", self.fn, ins, "inline mixing of export-name bytes in a loop")

    def _compare(self, ins, block, state):
        if len(ins.ops) == 2:
            self._compare_values(ins, block, self._value(state, ins, ins.ops[0]),
                                 self._value(state, ins, ins.ops[1]), ins.ops)

    def _compare_values(self, ins, block, left, right, ops):
        if ins is not _last_flag_setter(block):
            return
        terminator = block.insns[-1]
        if not terminator.mn.startswith("j") or terminator.mn == "jmp":
            return
        if ops[0] == ops[1]:
            return
        for mine, other, other_op in ((left, right, ops[1]), (right, left, ops[0])):
            if "H(NAME_PTR)" in mine:
                kind = _operand_kind(other, other_op)
                self.az.emit("hash_compared", self.fn, ins, f"hash of export name compared with {kind}")
                self.compare_blocks.add(block.start)
            elif any(t.startswith("H(") for t in mine):
                self.az.emit("other_hash_compared", self.fn, ins, "hash-like value of non-export data is compared")

    # ---- calls ---------------------------------------------------------------------------
    def _jump(self, ins, block, state):
        if not ins.ops:
            return
        op = ins.ops[0]
        if op.kind == "i":
            target = op.imm - self.az.pe.image_base
            if target not in self.fn.blocks:
                self._apply_call(ins, block, state, target)
                self.ret |= set(self._reg(state, "rax"))
            return
        target_name = self.az._iat_target(ins, op)
        if target_name:
            self._apply_import(target_name, ins, state)
            self.ret |= set(self._reg(state, "rax"))
        else:
            self._indirect(ins, self._value(state, ins, op))

    def _call(self, ins, block, state):
        if not ins.ops:
            return
        op = ins.ops[0]
        if op.kind == "i":
            self._apply_call(ins, block, state, op.imm - self.az.pe.image_base)
            return
        target_name = self.az._iat_target(ins, op)
        tags = self._value(state, ins, op)
        if target_name is None:
            names = [t[4:] for t in tags if t.startswith("IMP:")]
            target_name = names[0] if names else None
        if target_name:
            self._apply_import(target_name, ins, state)
        else:
            self._indirect(ins, tags)
            _clobber(state)

    def _indirect(self, ins, tags):
        for tag in sorted(tags):
            if tag.startswith("API("):
                self.az.emit("resolved_pointer_called", self.fn, ins, f"call target is {tag}")

    def _apply_call(self, ins, block, state, target):
        if target in self.az.thunks:
            self._apply_import(self.az.thunks[target], ins, state)
            return
        summary = self.az.summaries.get(target)
        if summary is None:
            _clobber(state)
            return
        args = [self._reg(state, reg) for reg in ARG_REGS]
        ret = self._substitute(summary.ret, args)
        if "H(NAME_PTR)" in ret and any("NAME_PTR" in a or "SEL" in a for a in args):
            self.az.emit("export_name_hashed", self.fn, ins, f"export-name pointer passed to hash-like function at RVA {target:#x}")
        for index, tags in summary.writes.items():
            if index >= len(args):
                continue
            value = self._substitute(tags, args)
            for tag in args[index]:
                if tag.startswith("SP:"):
                    key = f"S:{tag[3:]}"
                    state[key] = _cap(state.get(key, EMPTY) | value)
                elif tag.startswith("SPA:"):
                    key = f"SA:{tag[4:]}"
                    state[key] = _cap(state.get(key, EMPTY) | value)
                elif tag in ARG_TAGS:
                    self.writes[int(tag[1])] |= set(value)
        for sink in summary.gpa_sinks:
            incoming = args[int(sink[1])]
            if "SEL" in incoming:
                self.az.emit("selected_name_resolved", self.fn, ins, "selected export name reaches GetProcAddress through a call")
            for tag in incoming:
                if tag in ARG_TAGS:
                    self.gpa.add(tag)
        _clobber(state)
        if ret:
            state["rax"] = _cap(ret)

    def _substitute(self, tags, args):
        out = set()
        for tag in tags:
            if tag in ARG_TAGS:
                out |= set(args[int(tag[1])])
                continue
            match = ROOT_RE.match(tag)
            if match and match.group(2) in ARG_TAGS:
                kind = match.group(1)
                actual = args[int(match.group(2)[1])]
                classes = {_root_class(kind, item) for item in actual} - {None}
                out |= {f"{kind}({item})" for item in (classes or {"?"})}
            else:
                out.add(tag)
        return frozenset(out)

    def _apply_import(self, name, ins, state):
        result = EMPTY
        if name == "GetProcAddress":
            result = self._gpa(ins, self._reg(state, "rdx"))
        elif name in LOADER_APIS:
            result = frozenset({"MOD"})
        _clobber(state)
        if result:
            state["rax"] = result

    def _gpa(self, ins, name_tags):
        classes = set()
        if "SEL" in name_tags:
            classes.add("SEL")
            self.az.emit("selected_name_resolved", self.fn, ins, "hash-selected export name is passed to GetProcAddress")
        if "NAME_PTR" in name_tags:
            classes.add("NAME")
            self.az.emit("export_name_resolved", self.fn, ins, "export-name pointer is passed to GetProcAddress")
        for tag in sorted(name_tags):
            if tag in ARG_TAGS:
                classes.add(tag)
                self.gpa.add(tag)
            elif tag.startswith("G:"):
                classes.add("CONST")
                text = self.az.pe.cstring(int(tag[2:]), 128)
                self.az.emit("constant_name_resolved", self.fn, ins, f"constant name {text!r}" if text else "constant name")
        if not classes:
            classes.add("?")
            self.az.emit("unknown_name_resolved", self.fn, ins, "GetProcAddress name argument was not traced")
        return frozenset(f"API({item})" for item in classes)

    # ---- stack pointer -------------------------------------------------------------------
    def _shift_sp(self, state, delta):
        state["rsp"] = frozenset(_adjust(t, delta) for t in state.get("rsp", EMPTY))

    def _store_slot_at_sp(self, state, value):
        offset = _sp(state)
        if offset is not None:
            if value:
                state[f"S:{offset}"] = _cap(value)
            else:
                state.pop(f"S:{offset}", None)


# ---- pure helpers --------------------------------------------------------------------------
def _root_class(kind, item):
    if kind in ("H", "B"):
        if item in ("NAME_PTR", "SEL"):
            return "NAME_PTR"
        return item if item in ARG_TAGS else None
    if item in ("SEL",) or item in ARG_TAGS:
        return item
    if item == "NAME_PTR":
        return "NAME"
    if item.startswith("G:"):
        return "CONST"
    return None


def _operand_kind(tags, op):
    if op.kind == "i" or _const(tags) is not None:
        return "an immediate constant"
    if any(t in ARG_TAGS for t in tags):
        return "a function argument"
    if any(t.startswith("H(") for t in tags):
        return "another hash value"
    return "a stored value"


def _fold_constant(mn, left, right):
    """64-bit constant folding; x86 masks the shift count to its low six bits."""
    if mn == "add":
        value = left + right
    elif mn == "sub":
        value = left - right
    elif mn == "imul":
        value = left * right
    elif mn in ("shl", "sal"):
        value = left << (right & 63)
    else:
        return None
    value &= (1 << 64) - 1
    return value - (1 << 64) if value >> 63 else value


def _sp(state):
    return next((int(t[3:]) for t in state.get("rsp", EMPTY) if t.startswith("SP:")), None)


def _const(tags):
    values = [t for t in tags if t.startswith("C:")]
    return int(values[0][2:]) if len(values) == 1 and len(tags) == 1 else None


def _adjust(tag, delta):
    if delta is None:
        return tag
    for prefix in ("SP:", "SPA:", "C:"):
        if tag.startswith(prefix):
            return f"{prefix}{int(tag[len(prefix):]) + delta}"
    return tag


def _combine(left, right):
    out = {t for t in left | right if not t.startswith("C:") and t not in RVA_PROMOTION}
    for one, other in ((left, right), (right, left)):
        if _const(other) is None:
            out |= {RVA_PROMOTION[t] for t in one if t in RVA_PROMOTION}
    return frozenset(out)


def _cap(tags):
    tags = frozenset(tags)
    return frozenset(sorted(tags)[:MAX_TAGS]) if len(tags) > MAX_TAGS else tags


def _clean(tags):
    return frozenset(t for t in tags if not t.startswith(("SP:", "SPA:", "C:")))


def _clobber(state):
    for reg in VOLATILE:
        state.pop(reg, None)


def _join(old, new):
    if old is None:
        return dict(new), True
    merged = dict(old)
    changed = False
    for key, value in new.items():
        current = merged.get(key, EMPTY)
        union = current | value
        if union != current:
            merged[key] = _cap(union)
            changed = changed or merged[key] != current
    return merged, changed


def _last_flag_setter(block):
    for ins in reversed(block.insns):
        if ins.mn in FLAG_OPS:
            return ins
    return None


def _cut_at_terminator(insns):
    out = []
    for ins in insns:
        out.append(ins)
        if ins.mn in ("ret", "int3"):
            break
    return out


def _is_jcc(ins):
    return ins.mn.startswith("j") and ins.mn != "jmp"


def _build_cfg(fn: Function, image_base: int):
    if not fn.insns:
        return
    addrs = {i.addr for i in fn.insns}
    leaders = {fn.insns[0].addr}
    for ins in fn.insns:
        if ins.mn == "jmp" or _is_jcc(ins):
            if ins.ops and ins.ops[0].kind == "i":
                target = ins.ops[0].imm - image_base
                if target in addrs:
                    leaders.add(target)
            if ins.next in addrs:
                leaders.add(ins.next)
        elif ins.mn == "ret" and ins.next in addrs:
            leaders.add(ins.next)
    current = None
    for ins in fn.insns:
        if ins.addr in leaders:
            current = Block(ins.addr)
            fn.blocks[ins.addr] = current
        current.insns.append(ins)
    ordered = sorted(fn.blocks)
    for position, start in enumerate(ordered):
        block = fn.blocks[start]
        last = block.insns[-1]
        following = ordered[position + 1] if position + 1 < len(ordered) else None
        if last.mn == "jmp" or _is_jcc(last):
            if last.ops and last.ops[0].kind == "i":
                target = last.ops[0].imm - image_base
                if target in fn.blocks:
                    block.succs.append(target)
            elif last.mn == "jmp":
                fn.has_indirect_jump = True
            if _is_jcc(last) and following is not None:
                block.succs.append(following)
        elif last.mn not in ("ret", "int3") and following is not None:
            block.succs.append(following)
    for start, block in fn.blocks.items():
        for succ in block.succs:
            fn.blocks[succ].preds.append(start)
    fn.loop_blocks = _loops(fn)
    if len(fn.blocks) <= MAX_FUNCTION_BLOCKS:
        fn.control_deps = _control_dependence(fn)


def _loops(fn):
    body = set()
    for start, block in fn.blocks.items():
        for succ in block.succs:
            if succ <= start:
                seen = {succ, start}
                stack = [start]
                while stack:
                    for pred in fn.blocks[stack.pop()].preds:
                        if pred not in seen:
                            seen.add(pred)
                            stack.append(pred)
                body |= seen
    return body


def _control_dependence(fn):
    """Ferrante-style control dependence from immediate post-dominators."""
    nodes = sorted(fn.blocks)
    exit_node = -1
    succs = {n: (fn.blocks[n].succs or [exit_node]) for n in nodes}
    everything = set(nodes) | {exit_node}
    postdom = {n: set(everything) for n in nodes}
    postdom[exit_node] = {exit_node}
    changed = True
    while changed:
        changed = False
        for n in reversed(nodes):
            sets = [postdom[s] for s in succs[n]]
            new = {n} | (set.intersection(*sets) if sets else set())
            if new != postdom[n]:
                postdom[n] = new
                changed = True
    ipdom = {}
    for n in nodes:
        strict = postdom[n] - {n}
        ipdom[n] = next((c for c in strict if all(c in postdom[o] for o in strict)), exit_node)
    deps = defaultdict(set)
    for n in nodes:
        if len(succs[n]) < 2:
            continue
        for succ in succs[n]:
            runner = succ
            guard = 0
            while runner != exit_node and runner != ipdom[n] and guard < len(nodes) + 2:
                deps[n].add(runner)
                runner = ipdom.get(runner, exit_node)
                guard += 1
    return deps


# ---- syntactic D0 signals ------------------------------------------------------------------
def _evidence(pe, fn, ins, note):
    return {"function_rva": fn.rva, "rva": ins.addr, "va": pe.va(ins.addr),
            "file_offset": pe.rva_to_offset(ins.addr), "text": ins.text, "note": note}


def syntactic_loops(az, params):
    strong, combine = set(params["mix_strong"]), set(params["mix_combine"])
    found = []
    for rva in sorted(az.functions):
        fn = az.functions[rva]
        if rva in az.thunks:
            continue
        for ins in fn.insns:
            if not (ins.mn == "jmp" or _is_jcc(ins)) or not ins.ops or ins.ops[0].kind != "i":
                continue
            target = ins.ops[0].imm - az.pe.image_base
            if not rva <= target <= ins.addr:
                continue
            body = [i for i in fn.insns if target <= i.addr <= ins.addr]
            load = next((i for i in body if i.mn in ("movzx", "movsx") and len(i.ops) == 2
                         and i.ops[1].kind == "m" and i.ops[1].size == 1), None)
            mix = next((i for i in body if i.mn in strong), None)
            join = next((i for i in body if i.mn in combine
                         and not (len(i.ops) == 2 and i.ops[0] == i.ops[1])
                         and not (len(i.ops) == 2 and i.ops[1].kind == "i")), None)
            if load and mix and join:
                found.append({"function_rva": rva, "loop_start_rva": target, "back_edge_rva": ins.addr,
                              "evidence": [_evidence(az.pe, fn, load, "byte load inside loop"),
                                           _evidence(az.pe, fn, mix, "mixing instruction inside loop"),
                                           _evidence(az.pe, fn, join, "combining instruction inside loop"),
                                           _evidence(az.pe, fn, ins, "loop back edge")]})
    return found


def non_import_indirect_calls(az):
    found = []
    for rva in sorted(az.functions):
        fn = az.functions[rva]
        if rva in az.thunks:
            continue
        for ins in fn.insns:
            if ins.mn == "call" and ins.ops and ins.ops[0].kind != "i" and not az._iat_target(ins, ins.ops[0]):
                found.append(_evidence(az.pe, fn, ins, "indirect call whose target is not an import slot"))
    return found


def import_references(az, name):
    found = []
    for rva in sorted(az.functions):
        fn = az.functions[rva]
        for ins in fn.insns:
            if ins.mn in ("call", "jmp") and ins.ops and az._iat_target(ins, ins.ops[0]) == name and rva not in az.thunks:
                found.append(_evidence(az.pe, fn, ins, f"call through the import slot of {name}"))
            elif ins.mn == "call" and ins.ops and ins.ops[0].kind == "i":
                if az.thunks.get(ins.ops[0].imm - az.pe.image_base) == name:
                    found.append(_evidence(az.pe, fn, ins, f"call through a thunk of {name}"))
    return found


def analyze(pe: PeFile) -> Analyzer:
    return Analyzer(pe).run()
