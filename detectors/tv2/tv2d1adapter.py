#!/usr/bin/env python3
"""Proposed adapter from TV2 static features to a flat input record for D1.

D1 and its interface are not defined in this repository yet. This is a TV2 proposal;
producing this record does not mean that D1 has been integrated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "tv2-d1-static-input/1.0"
RELATION_SCORE = {"verified": 1.0, "heuristic": 0.5, "absent": 0.0}
OBSERVATION_FIELDS = {
    "imports_get_proc_address": "f.imports.get_proc_address",
    "hash_like_loops": "f.code.hash_like_loops",
    "non_import_indirect_calls": "f.code.non_import_indirect_calls",
    "get_proc_address_calls": "f.code.get_proc_address_calls",
    "dynamic_name_calls": "f.resolve.dynamic_name_calls",
}
RELATION_FIELDS = {
    "export_names_enumerated": "rel.export_names_enumerated",
    "export_name_to_hash": "rel.export_name_to_hash",
    "hash_to_compare": "rel.hash_to_compare",
    "compare_to_name_selection": "rel.compare_to_name_selection",
    "selection_to_resolve": "rel.selection_to_resolve",
    "resolve_to_pointer_use": "rel.resolve_to_pointer_use",
}


def adapt(doc):
    features = doc["features"]
    values, missing = {}, []
    for name, key in OBSERVATION_FIELDS.items():
        item = features[key]
        if item["status"] in ("present", "absent"):
            values[name] = int(item["value"])
        else:
            values[name] = None
            missing.append(name)
    for name, key in RELATION_FIELDS.items():
        score = RELATION_SCORE.get(features[key]["status"])
        values[name] = score
        if score is None:
            missing.append(name)
    return {"schema": SCHEMA, "sha256": doc["sample"]["sha256"], "analysis_id": doc["run"]["analysis_id"],
            "features_content_sha256": doc["content_sha256"], "analysis_status": doc["analysis"]["status"],
            "values": values, "missing": missing}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features", nargs="+")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in args.features:
        doc = json.loads(Path(name).read_text(encoding="utf-8"))
        (out / Path(name).name).write_text(json.dumps(adapt(doc), indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"records={len(args.features)} out={out}")


if __name__ == "__main__":
    main()
