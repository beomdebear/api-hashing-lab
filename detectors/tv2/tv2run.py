#!/usr/bin/env python3
"""Runs the detectors over one manifest split.

Every binary is copied to a neutral name first, so the detector cannot see a
role, label or build directory. The runner has no access to any label file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tv2features  # noqa: E402
import tv2freeze  # noqa: E402
import tv2rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = {"d0": "d0.json", "static-only": "static-only.json"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(value, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run(args):
    config_dir = ROOT / "configs" / "tv2"
    rows = [r for r in read_manifest(args.manifest) if args.split == "all" or r["split"] == args.split]
    if not rows:
        raise SystemExit(f"no samples for split {args.split}")
    if args.split in ("test", "all") and not args.lock:
        raise SystemExit("the test split requires --lock")
    if args.lock:
        changed = tv2freeze.verify(Path(args.lock))
        if changed:
            raise SystemExit("rule lock mismatch: " + ", ".join(changed))
    extractor = load_json(config_dir / "extractor.json")
    configs = {name: load_json(config_dir / CONFIGS[name]) for name in args.detectors.split(",")}
    now = datetime.now(timezone.utc)
    run_id = f"R-{now:%Y%m%dT%H%M%SZ}-{args.split}-{extractor['version']}"
    out = Path(args.out_root) / run_id
    records = []
    for row in rows:
        sample_id = row["sample_id"]
        source = ROOT / row["binary"]
        staged = out / "input" / f"{sample_id}.bin"
        staged.parent.mkdir(parents=True, exist_ok=True)
        integrity = "ok"
        if source.is_file():
            shutil.copyfile(source, staged)
            if hashlib.sha256(staged.read_bytes()).hexdigest().upper() != row["sha256"].upper():
                integrity = "sha256_mismatch"
        else:
            integrity = "binary_missing"
        doc = tv2features.extract(staged, extractor)
        doc["run"]["input_path"] = f"input/{sample_id}.bin"
        doc["run"]["run_id"] = run_id
        if integrity != "ok":
            doc["analysis"]["status"] = "error"
            doc["analysis"]["detail"] = integrity
        dump(doc, out / "features" / f"{sample_id}.json")
        for name, config in configs.items():
            prediction = tv2rules.evaluate(doc, config)
            prediction["sample"]["sample_id"] = sample_id
            prediction["run"]["run_id"] = run_id
            dump(prediction, out / "predictions" / name / f"{sample_id}.json")
        records.append({"sample_id": sample_id, "sha256": row["sha256"], "integrity": integrity,
                        "analysis_status": doc["analysis"]["status"],
                        "analysis_ms": doc["run"]["duration_ms"]})
        if staged.exists() and not args.keep_input:
            staged.unlink()
    if not args.keep_input and (out / "input").is_dir():
        (out / "input").rmdir()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dump({"schema": "tv2-run/1", "run_id": run_id, "split": args.split, "started_at": now.isoformat(timespec="seconds"),
          "git_head": head, "lock": Path(args.lock).as_posix() if args.lock else None,
          "extractor": {"version": extractor["version"], "config_sha256": tv2features.canonical_digest(extractor),
                        "code_sha256": tv2features.code_digest()},
          "detectors": {n: {"version": c["version"], "config_sha256": tv2features.canonical_digest(c)}
                        for n, c in configs.items()},
          "manifest_sha256": tv2freeze.file_digest(Path(args.manifest)), "samples": records}, out / "run.json")
    print(out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", required=True, choices=("dev", "test", "probe", "all"))
    parser.add_argument("--manifest", default=str(ROOT / "configs/tv2/manifest-provisional.csv"))
    parser.add_argument("--detectors", default="d0,static-only")
    parser.add_argument("--out-root", default=str(ROOT / "artifacts/runs/tv2"))
    parser.add_argument("--lock")
    parser.add_argument("--keep-input", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
