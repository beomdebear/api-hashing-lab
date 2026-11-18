"""Turns binary observations into the versioned TV2 static feature document.

Input is only the bytes of one file. File names, directories, labels, sample
sources, hash tables and PoC logs are never read here.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import capstone

import tv2analysis as ta
from tv2pe import PeError, PeFile, PeUnsupported

SCHEMA = "tv2-static-features/1.0"
HERE = Path(__file__).resolve().parent
CODE_FILES = ("tv2pe.py", "tv2analysis.py", "tv2features.py")
MAX_EVIDENCE = 8

OBSERVATIONS = (
    "f.imports.get_proc_address", "f.imports.loader_apis", "f.code.hash_like_loops",
    "f.code.non_import_indirect_calls", "f.code.get_proc_address_calls",
    "f.resolve.constant_names", "f.resolve.dynamic_name_calls",
)
RELATIONS = (
    "rel.export_names_enumerated", "rel.export_name_to_hash", "rel.hash_to_compare",
    "rel.compare_to_name_selection", "rel.selection_to_resolve", "rel.resolve_to_pointer_use",
)


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def code_digest() -> str:
    digest = hashlib.sha256()
    for name in CODE_FILES:
        digest.update(name.encode())
        digest.update((HERE / name).read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest().upper()


def canonical_digest(value) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("ascii")).hexdigest().upper()


def _observation(value, evidence=()):
    present = bool(value)
    return {"kind": "observation", "status": "present" if present else "absent",
            "value": value, "evidence": list(evidence)[:MAX_EVIDENCE]}


def _relation(state, evidence=(), detail=""):
    return {"kind": "relation", "status": state, "value": state == "verified",
            "detail": detail, "evidence": list(evidence)[:MAX_EVIDENCE]}


def _unavailable(status):
    out = {}
    for name in OBSERVATIONS:
        out[name] = {"kind": "observation", "status": status, "value": None, "evidence": []}
    for name in RELATIONS:
        out[name] = {"kind": "relation", "status": status, "value": None, "detail": "", "evidence": []}
    return out


def _by_kind(az):
    groups = {}
    for key in sorted(az.events, key=lambda k: (k[1], k[0], k[2])):
        groups.setdefault(key[0], []).append(az.events[key])
    return groups


def _relations(ev, loops, indirect, incomplete):
    missing = "unknown" if incomplete else "absent"
    names = ev.get("export_name_pointer", [])
    walk = ev.get("export_directory_read", []) + ev.get("export_names_field_read", []) + \
        ev.get("export_name_rva_read", [])
    out = {}
    if names and walk:
        out["rel.export_names_enumerated"] = _relation("verified", walk + names,
            "export directory -> AddressOfNames -> module base + name RVA")
    elif walk:
        out["rel.export_names_enumerated"] = _relation("heuristic", walk, "export fields are read, but no name pointer was traced")
    else:
        out["rel.export_names_enumerated"] = _relation(missing)

    hashed = ev.get("export_name_hashed", [])
    if hashed and names:
        out["rel.export_name_to_hash"] = _relation("verified", hashed, "export-name bytes reach a mixing loop")
    elif names and loops:
        out["rel.export_name_to_hash"] = _relation("heuristic", [e for l in loops[:2] for e in l["evidence"][:1]],
            "export names and a hash-like loop coexist; no data flow between them was found")
    else:
        out["rel.export_name_to_hash"] = _relation(missing)

    compared = ev.get("hash_compared", [])
    other = ev.get("other_hash_compared", [])
    if compared and hashed:
        out["rel.hash_to_compare"] = _relation("verified", compared, compared[0]["note"])
    elif hashed and other:
        out["rel.hash_to_compare"] = _relation("heuristic", other, "another hash-like value is compared")
    else:
        out["rel.hash_to_compare"] = _relation(missing)

    selected = ev.get("name_selected_by_hash", [])
    if selected and compared:
        out["rel.compare_to_name_selection"] = _relation("verified", selected,
            "the name pointer is assigned in a block control-dependent on the hash comparison")
    elif compared:
        out["rel.compare_to_name_selection"] = _relation("heuristic", compared, "hash is compared, but no selected name was traced")
    else:
        out["rel.compare_to_name_selection"] = _relation(missing)

    resolved = ev.get("selected_name_resolved", [])
    dynamic = ev.get("export_name_resolved", []) + ev.get("unknown_name_resolved", [])
    if resolved and selected:
        out["rel.selection_to_resolve"] = _relation("verified", resolved, "the selected name is the GetProcAddress name argument")
    elif selected and dynamic:
        out["rel.selection_to_resolve"] = _relation("heuristic", dynamic, "GetProcAddress uses a non-constant name; the link was not proven")
    else:
        out["rel.selection_to_resolve"] = _relation(missing)

    used = [e for e in ev.get("resolved_pointer_called", []) if "API(SEL)" in e["note"]]
    if used and resolved:
        out["rel.resolve_to_pointer_use"] = _relation("verified", used, "the resolved address is the target of an indirect call")
    elif resolved and indirect:
        out["rel.resolve_to_pointer_use"] = _relation("heuristic", indirect, "indirect calls exist; none was linked to the resolved address")
    else:
        out["rel.resolve_to_pointer_use"] = _relation(missing)
    return out


def _features(pe, az, params):
    loops = ta.syntactic_loops(az, params)
    indirect = ta.non_import_indirect_calls(az)
    gpa_calls = ta.import_references(az, "GetProcAddress")
    gpa_slots = [i for i in pe.imports if i.name == "GetProcAddress"]
    loaders = sorted({i.name for i in pe.imports if i.name in ta.LOADER_APIS})
    ev = _by_kind(az)
    constant = ev.get("constant_name_resolved", [])
    dynamic = ev.get("selected_name_resolved", []) + ev.get("export_name_resolved", []) + \
        ev.get("unknown_name_resolved", [])
    slot_evidence = [{"function_rva": None, "rva": i.iat_rva, "va": pe.va(i.iat_rva),
                      "file_offset": pe.rva_to_offset(i.iat_rva), "text": f"{i.dll}!{i.name}",
                      "note": "import address table slot"} for i in gpa_slots]
    out = {
        "f.imports.get_proc_address": _observation(bool(gpa_slots), slot_evidence),
        "f.imports.loader_apis": _observation(loaders),
        "f.code.hash_like_loops": _observation(len(loops), [e for l in loops for e in l["evidence"]]),
        "f.code.non_import_indirect_calls": _observation(len(indirect), indirect),
        "f.code.get_proc_address_calls": _observation(len(gpa_calls), gpa_calls),
        "f.resolve.constant_names": _observation(sorted({e["note"] for e in constant}), constant),
        "f.resolve.dynamic_name_calls": _observation(len({e["rva"] for e in dynamic}), dynamic),
    }
    out.update(_relations(ev, loops, indirect, bool(az.incomplete)))
    return out


def extract(path, config):
    started = time.perf_counter()
    raw = Path(path).read_bytes() if Path(path).is_file() else None
    doc = {
        "schema": SCHEMA,
        "extractor": {"name": config["name"], "version": config["version"],
                      "config_sha256": canonical_digest(config), "code_sha256": code_digest(),
                      "capstone": capstone.__version__},
        "sample": {"sha256": hashlib.sha256(raw).hexdigest().upper() if raw is not None else None,
                   "size": len(raw) if raw is not None else None},
    }
    if raw is None:
        doc.update(analysis={"status": "error", "detail": "input file not found", "functions": 0, "incomplete": []},
                   pe=None, features=_unavailable("analysis_error"))
    else:
        try:
            pe = PeFile(raw)
            az = ta.analyze(pe)
            incomplete = sorted({(i["function_rva"] or 0, i["reason"]) for i in az.incomplete})
            status = "partial" if incomplete else "ok"
            detail = "" if az.functions else "no functions were recovered"
            if not az.functions:
                status = "partial"
            doc.update(
                analysis={"status": status, "detail": detail, "functions": len(az.functions),
                          "incomplete": [{"function_rva": a, "reason": b} for a, b in incomplete]},
                pe={"machine": pe.machine, "image_base": pe.image_base, "entry_rva": pe.entry_rva,
                    "sections": [{"name": s.name, "rva": s.rva, "virtual_size": s.virtual_size,
                                  "raw_offset": s.raw_offset, "raw_size": s.raw_size,
                                  "executable": s.executable} for s in pe.sections],
                    "imports": sorted(f"{i.dll}!{i.name}" for i in pe.imports)},
                features=_features(pe, az, config["signal_params"]))
        except PeUnsupported as exc:
            doc.update(analysis={"status": "unsupported", "detail": str(exc), "functions": 0, "incomplete": []},
                       pe=None, features=_unavailable("unknown"))
        except PeError as exc:
            doc.update(analysis={"status": "error", "detail": str(exc), "functions": 0, "incomplete": []},
                       pe=None, features=_unavailable("analysis_error"))
        except Exception as exc:  # an analyzer defect must never look like a benign result
            doc.update(analysis={"status": "error", "detail": f"internal analysis failure: {type(exc).__name__}: {exc}",
                                 "functions": 0, "incomplete": []},
                       pe=None, features=_unavailable("analysis_error"))
    doc["content_sha256"] = canonical_digest(doc)
    now = datetime.now(timezone.utc)
    digest = (doc["sample"]["sha256"] or "MISSING")[:8]
    doc["run"] = {"analysis_id": f"A-{now:%Y%m%dT%H%M%S%f}Z-{digest}",
                  "generated_at": now.isoformat(timespec="seconds"),
                  "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                  "input_path": str(path)}
    return doc
