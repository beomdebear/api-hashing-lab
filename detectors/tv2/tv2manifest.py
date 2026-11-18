#!/usr/bin/env python3
"""Creates the PROVISIONAL TV2 manifest and the separate ground-truth file.

The official labels and split belong to the group (TV4). These files are a TV2
proposal so that the pipeline can run; they must not be presented as approved.
Only the runner reads the manifest and only the evaluator reads the ground truth.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLIT = {
    "B1": "dev", "B2": "dev", "P1": "dev", "TV2C-B3": "dev", "TV2C-B4": "dev",
    "P2": "test", "P3": "test", "P4": "test", "P5": "test", "E1": "test", "E2": "test",
    "TV2C-B5": "test", "TV2C-B6": "test",
    "VAR-P1-MSVC-O2": "probe", "VAR-P3-MSVC-O2": "probe", "VAR-B6-MSVC-O2": "probe",
    "VAR-P1-GCC-O2": "probe", "VAR-B6-GCC-O2": "probe",
}
LABEL_SOURCE = {
    "B": "TV1 guide: benign sample without API hashing",
    "P": "TV1 guide: API hashing PoC",
    "E": "TV1 guide section 6: E1/E2 still contain API hashing code",
    "C": "TV2 proposed control: source uses no hash to find an API",
}


def label_for(key):
    core = key.split("-")[1] if key.startswith("VAR-") else key
    if core.startswith("TV2C-") or core.startswith("B"):
        return "negative", LABEL_SOURCE["C" if key.startswith("TV2C-") or key.startswith("VAR-B") else "B"]
    return "positive", LABEL_SOURCE["E" if core.startswith("E") else "P"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-manifest", required=True)
    parser.add_argument("--out-dir", default=str(ROOT / "configs" / "tv2"))
    args = parser.parse_args()
    build = json.loads(Path(args.build_manifest).read_text(encoding="utf-8-sig"))
    manifest, truth = [], []
    for row in build["samples"]:
        key = row["build_key"]
        sample_id = f"S-{row['sha256'][:10]}"
        manifest.append({"sample_id": sample_id, "sha256": row["sha256"], "split": SPLIT[key],
                         "role": key, "group": row["group"], "build_id": build["build_id"],
                         "binary": row["binary"]})
        label, source = label_for(key)
        truth.append({"sample_id": sample_id, "sha256": row["sha256"], "label": label,
                      "label_status": "provisional_tv2_not_approved_by_tv4", "label_source": source})
    out = Path(args.out_dir)
    for name, rows in (("manifest-provisional.csv", manifest), ("ground-truth-provisional.csv", truth)):
        with open(out / name, "w", newline="\n", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(f"samples={len(manifest)} out={out}")


if __name__ == "__main__":
    main()
