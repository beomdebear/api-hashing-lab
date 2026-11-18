#!/usr/bin/env python3
"""Final TV2 consistency check: links, referenced files, versions and run identity."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "detectors" / "tv2"))
import tv2features  # noqa: E402
import tv2freeze  # noqa: E402

VERSION = "1.0.1"
LOCK = ROOT / f"configs/tv2/locks/rule-lock-{VERSION}.json"
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
CODE = re.compile(r"`([^`\n]+)`")
PREFIXES = ("docs/", "evidence/", "configs/", "schemas/", "detectors/", "scripts/", "tests/", "samples/", "ban-giao/", "prompt-claude/")
# These images are produced by the user-run capture step and are tracked as missing.
PENDING_IMAGE = re.compile(r"evidence/G\d/TV2/G\d-TV2-\d\d/images/?")
RELATIVE_EVIDENCE = re.compile(r"^(ghidra-headless|runs|d1-input-dev)/?$")


def documents():
    names = [ROOT / "README-TV2.md", ROOT / "CLAUDE.md"]
    names += sorted((ROOT / "docs/tv2").glob("*.md")) + sorted((ROOT / "ban-giao").glob("*.md"))
    for group in ("G1", "G2", "G3"):
        for path in sorted((ROOT / "evidence" / group / "TV2").rglob("*.md")):
            if "ghidra-headless" not in path.parts:
                names.append(path)
    return names


def check_links():
    problems, links, paths = [], 0, 0
    docs = documents()
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            links += 1
            if not (doc.parent / unquote(target.split("#")[0])).exists():
                problems.append(f"{doc.relative_to(ROOT).as_posix()}: broken link {target}")
        for value in CODE.findall(text):
            value = value.strip().rstrip("/")
            value = re.sub(r":\d+$", "", value)
            if not value.startswith(PREFIXES) or re.search(r"[<>*…\s]|DD-MM", value) or PENDING_IMAGE.match(value):
                continue
            paths += 1
            if not (ROOT / value).exists():
                problems.append(f"{doc.relative_to(ROOT).as_posix()}: missing path {value}")
    return len(docs), links, paths, problems


def check_versions():
    problems, runs = [], []
    changed = tv2freeze.verify(LOCK, include_labels=True)
    if changed:
        problems.append("lock mismatch: " + ", ".join(changed))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    extractor = json.loads((ROOT / "configs/tv2/extractor.json").read_text(encoding="utf-8"))
    if extractor["version"] != VERSION or lock["lock_version"] != VERSION:
        problems.append("extractor version and lock version differ")
    configs = {"d0": "d0.json", "static-only": "static-only.json"}
    digests = {k: tv2features.canonical_digest(json.loads((ROOT / "configs/tv2" / v).read_text(encoding="utf-8"))) for k, v in configs.items()}
    code = tv2features.code_digest()
    report = (ROOT / "docs/tv2/static-detector-report.md").read_text(encoding="utf-8")
    # The report cites the newest run of each split; older runs stay as history.
    latest = [sorted((ROOT / base).glob(f"R-*-{split}-{VERSION}"))[-1] for base, split in (
        ("evidence/G2/TV2/G2-TV2-01/runs", "dev"), ("evidence/G3/TV2/G3-TV2-01/runs", "test"),
        ("evidence/G3/TV2/G3-TV2-01/runs", "probe"))]
    for run in latest:
        meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
        runs.append(run.name)
        if meta["extractor"]["code_sha256"] != code:
            problems.append(f"{run.name}: extractor code differs from the current code")
        if run.name not in report:
            problems.append(f"{run.name}: not cited by the static report")
        for name, digest in digests.items():
            if meta["detectors"][name]["config_sha256"] != digest:
                problems.append(f"{run.name}: {name} configuration differs")
        count = len(meta["samples"])
        for name in digests:
            found = len(list((run / "predictions" / name).glob("*.json")))
            if found != count:
                problems.append(f"{run.name}: {name} has {found} predictions for {count} samples")
    return runs, problems, lock


def pending_images():
    source = (ROOT / "docs/tv2/HUONG-DAN-CHUP-ANH.md").read_text(encoding="utf-8")
    missing, present = [], []
    for folder, cell in re.findall(r"\| `(evidence/[^`]+/images/)` \| ([^|]+) \|", source):
        for name in re.findall(r"`([^`]+\.png)`", cell):
            (present if (ROOT / folder / name).is_file() else missing).append(folder + name)
    return present, missing


def main():
    docs, links, paths, link_problems = check_links()
    runs, version_problems, lock = check_versions()
    present, missing = pending_images()
    problems = link_problems + version_problems
    now = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")
    commit = "có" if lock["git_commit_lock"]["created"] else f"chưa có ({lock['git_commit_lock']['reason']})"
    rows = [("Tài liệu đã quét", docs), ("Liên kết nội bộ đã kiểm", links), ("Đường dẫn trong mã đã kiểm", paths),
            ("Run phiên bản hiện tại", ", ".join(f"`{r}`" for r in runs)), ("Lock hiện tại", f"`{LOCK.relative_to(ROOT).as_posix()}`"),
            ("Commit khóa", commit), ("Ảnh GUI đã có", len(present)), ("Ảnh GUI còn thiếu", len(missing)), ("Lỗi liên kết hoặc phiên bản", len(problems))]
    text = ["# Kiểm tra cuối phần TV2", "", f"Thời điểm: {now}. Sinh bởi `detectors/tv2/tv2linkcheck.py`.", "",
            "| Mục | Kết quả |", "|---|---|", *[f"| {a} | {b} |" for a, b in rows], "",
            "## Checklist", "",
            f"- [{'x' if not version_problems else ' '}] Code, config, schema, manifest và nhãn đề xuất khớp lock {VERSION}.",
            f"- [{'x' if not version_problems else ' '}] Mọi run hiện tại dùng đúng code, config và được báo cáo nêu.",
            f"- [{'x' if not link_problems else ' '}] Liên kết và đường dẫn trong tài liệu TV2 tồn tại.",
            f"- [{'x' if not missing else ' '}] Đủ ảnh GUI theo danh sách chụp.",
            f"- [{'x' if lock['git_commit_lock']['created'] else ' '}] Có commit khóa.",
            "- [ ] TV1 phản hồi review.", "- [ ] TV4 xác nhận mẫu đối chứng, nhãn và split.", "- [ ] Có bảng D0/D1 thực đo.", "",
            "## Lỗi đã sửa trong phiên", "",
            "- Extractor 1.0.0 dừng vì số dịch âm; sửa ở 1.0.1 và thêm test.",
            "- Lỗi nội bộ của extractor từng có thể dừng cả lượt chạy; nay trả `analysis_error`.",
            "- Bảng B1/B2 ban đầu chưa phân biệt chuỗi của bảng import với chuỗi được mã tham chiếu; đã sửa.",
            "- Kết luận về GCC và `/O2` ban đầu chưa đủ căn cứ; đã kiểm bằng symbol và sự kiện phân tích.",
            "- Script Ghidra ban đầu dùng API chuỗi cũ, xem `INT3` là lời gọi gián tiếp và không nhập lại được sau lần lỗi; đã sửa.", "",
            "## Còn tồn đọng", "", "- Hai probe GCC vượt ngân sách phân tích; chưa sửa để giữ nguyên phiên bản đã đánh giá.",
            "- Script chụp GUI chưa được chạy với giao diện thật.", ""]
    if problems:
        text += ["## Lỗi phát hiện", "", *[f"- {p}" for p in problems], ""]
    if missing:
        text += ["## Ảnh còn thiếu", "", *[f"- {name}" for name in missing], ""]
    target = ROOT / "evidence/G3/TV2/G3-TV2-03/final-check.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(text).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"docs={docs} links={links} paths={paths} runs={len(runs)} problems={len(problems)} images_missing={len(missing)}")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
