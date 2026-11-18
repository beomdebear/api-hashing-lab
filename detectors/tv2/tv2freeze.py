#!/usr/bin/env python3
"""Creates or verifies a rule lock: checksums of everything that defines a result.

A lock is not a git commit. ``git_commit_lock`` states whether one exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCKED = (
    "detectors/tv2/tv2pe.py", "detectors/tv2/tv2analysis.py", "detectors/tv2/tv2features.py",
    "detectors/tv2/tv2rules.py", "configs/tv2/extractor.json", "configs/tv2/d0.json",
    "configs/tv2/static-only.json", "configs/tv2/manifest-provisional.csv",
    "schemas/tv2/static-features-1.0.schema.json", "schemas/tv2/prediction-1.0.schema.json",
)
# Checked only by this command line and never by the detector runner.
LABEL_FILES = ("configs/tv2/ground-truth-provisional.csv",)


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout


def current_files(include_labels=False):
    names = LOCKED + (LABEL_FILES if include_labels else ())
    return {name: file_digest(ROOT / name) for name in names}


def create(path: Path, version: str, note: str):
    if path.exists():
        raise SystemExit(f"lock already exists, refusing to overwrite: {path}")
    unmerged = [line for line in git("diff", "--name-only", "--diff-filter=U").splitlines() if line]
    now = datetime.now(timezone(timedelta(hours=7)))
    lock = {
        "schema": "tv2-rule-lock/1", "lock_version": version, "created_at": now.isoformat(timespec="seconds"),
        "note": note, "git_head": git("rev-parse", "HEAD").strip(),
        "git_branch": git("branch", "--show-current").strip(),
        "git_status_entries": len(git("status", "--porcelain=v1").splitlines()),
        "git_commit_lock": {"created": False,
                            "reason": "the index has unmerged paths" if unmerged else "no commit was requested",
                            "unmerged_paths": unmerged},
        "files_sha256": current_files(include_labels=True),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"created {path}")


def verify(path: Path, include_labels=False) -> list:
    lock = json.loads(path.read_text(encoding="utf-8"))
    now = current_files(include_labels)
    return [name for name, digest in lock["files_sha256"].items() if name in now and now[name] != digest]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("create", "verify"))
    parser.add_argument("lock")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    if args.action == "create":
        create(Path(args.lock), args.version, args.note)
        return 0
    changed = verify(Path(args.lock), include_labels=True)
    print("lock OK" if not changed else "lock MISMATCH: " + ", ".join(changed))
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
