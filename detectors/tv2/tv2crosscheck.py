#!/usr/bin/env python3
"""Compares the TV2 extractor with Ghidra's independent headless export.

This is an analyst check. Its output is never an input of the detector.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASM_LINE = re.compile(r"^RVA_([0-9A-F]{8})\s+(\S+)")
RELATIONS = ("rel.export_names_enumerated", "rel.export_name_to_hash", "rel.hash_to_compare",
             "rel.compare_to_name_selection", "rel.selection_to_resolve", "rel.resolve_to_pointer_use")


def rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def hex_set(items):
    return {int(item, 16) for item in items}


def describe(extra):
    return " ".join(f"0x{v:X}" if isinstance(v, int) else str(v) for v in sorted(extra)) or "-"


def compare_sets(name, ours, theirs, complete=True):
    only_ours, only_ghidra = ours - theirs, theirs - ours
    passed = not only_ghidra and not only_ours if complete else not only_ours
    return {"check": name, "result": "match" if passed else "difference", "extractor": len(ours), "ghidra": len(theirs),
            "only_extractor": describe(only_ours), "only_ghidra": describe(only_ghidra)}


def check_sample(role, row, feature_doc, export):
    results = []
    summary = json.loads((export / "summary.json").read_text(encoding="utf-8"))
    same = summary["sha256"] == row["sha256"] == feature_doc["sample"]["sha256"]
    results.append({"check": "sha256_same_binary", "result": "match" if same else "difference", "extractor": 1, "ghidra": 1,
                    "only_extractor": "-", "only_ghidra": "-"})
    ours = {item.split("!", 1)[1] for item in feature_doc["pe"]["imports"]}
    theirs = {r["symbol"] for r in rows(export / "imports.csv")}
    results.append(compare_sets("import_names", ours, theirs, complete=False))
    features = feature_doc["features"]
    calls = rows(export / "api-calls.csv")
    gpa = features["f.code.get_proc_address_calls"]
    ghidra_gpa = hex_set(r["call_rva"] for r in calls if r["target_api"] == "GetProcAddress")
    results.append(compare_sets("getprocaddress_call_sites", {e["rva"] for e in gpa["evidence"]}, ghidra_gpa,
                                complete=gpa["value"] <= len(gpa["evidence"])))
    indirect = features["f.code.non_import_indirect_calls"]
    ghidra_indirect = hex_set(r["call_rva"] for r in rows(export / "indirect-calls.csv"))
    results.append(compare_sets("non_import_indirect_calls", {e["rva"] for e in indirect["evidence"]}, ghidra_indirect,
                                complete=indirect["value"] <= len(indirect["evidence"])))
    listing = {}
    for path in (export / "disasm").glob("*.asm"):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = ASM_LINE.match(line)
            if match:
                listing[int(match.group(1), 16)] = match.group(2).lower()
    # Heuristic items are hints, not chain proof, and may lie outside the exported functions.
    wanted = {(e["rva"], e["text"].split()[0].lower()) for name in RELATIONS
              if features[name]["status"] == "verified" for e in features[name]["evidence"]}
    missing = {f"0x{rva:X}:{mnemonic}" for rva, mnemonic in wanted if listing.get(rva) != mnemonic}
    results.append({"check": "relation_evidence_instructions", "result": "match" if not missing else "difference",
                    "extractor": len(wanted), "ghidra": len(wanted) - len(missing),
                    "only_extractor": " ".join(sorted(missing)) or "-", "only_ghidra": "-"})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", default=str(ROOT / "artifacts/ghidra/20261118-094956/export"))
    parser.add_argument("--runs", nargs="+", required=True, help="run directories that contain features/")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = {r["sample_id"]: r for r in rows(ROOT / "configs/tv2/manifest-provisional.csv")}
    output = []
    for run in args.runs:
        run_id = Path(run).name
        for path in sorted((Path(run) / "features").glob("*.json")):
            row = manifest[path.stem]
            export = Path(args.export) / row["role"]
            if not (export / "summary.json").is_file():
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            for item in check_sample(row["role"], row, doc, export):
                output.append({"run_id": run_id, "role": row["role"], "sha256": row["sha256"], **item})
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    different = [r for r in output if r["result"] != "match"]
    print(f"checks={len(output)} differences={len(different)}")
    for item in different:
        print(item["role"], item["check"], "extractor-only:", item["only_extractor"], "ghidra-only:", item["only_ghidra"])


if __name__ == "__main__":
    main()
