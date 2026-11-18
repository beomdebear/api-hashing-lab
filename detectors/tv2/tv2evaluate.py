#!/usr/bin/env python3
"""Joins predictions with the separate ground truth and reports per-sample results.

``unknown`` is never turned into benign. Headline metrics use decided samples;
the ``worst_case`` block counts each unknown as an error. A zero denominator is
reported as null (N/A).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTCOME = {("positive", "positive"): "TP", ("negative", "negative"): "TN",
           ("negative", "positive"): "FP", ("positive", "negative"): "FN"}


def ratio(top, bottom):
    return round(top / bottom, 4) if bottom else None


def metrics(counts):
    tp, fp, fn = counts["TP"], counts["FP"], counts["FN"]
    precision, recall = ratio(tp, tp + fp), ratio(tp, tp + fn)
    f1 = ratio(2 * precision * recall, precision + recall) if precision is not None and recall is not None else None
    return {"precision": precision, "recall": recall, "f1": f1}


def summarize(rows):
    counts = {k: sum(r["outcome"] == k for r in rows) for k in ("TP", "TN", "FP", "FN", "UNKNOWN")}
    worst = dict(counts)
    worst["FN"] += sum(r["outcome"] == "UNKNOWN" and r["label"] == "positive" for r in rows)
    worst["FP"] += sum(r["outcome"] == "UNKNOWN" and r["label"] == "negative" for r in rows)
    times = sorted(r["analysis_ms"] for r in rows if r["analysis_ms"] is not None)
    return {"samples_total": len(rows),
            "analysis_succeeded": sum(r["analysis_status"] == "ok" for r in rows),
            "counts": counts, **metrics(counts), "worst_case": metrics(worst),
            "analysis_ms": {"median": times[len(times) // 2] if times else None,
                            "max": times[-1] if times else None}}


def reason_for(pred, outcome):
    if outcome == "UNKNOWN":
        return f"analysis_status={pred['analysis_status']}; {pred['analysis_detail']}".strip("; ")
    if pred["verdict"] == "positive":
        return "all conditions passed: " + ", ".join(c["id"] for c in pred["conditions"])
    return "failed conditions: " + ", ".join(pred["failed_conditions"])


def first_evidence(pred):
    for cond in reversed(pred["conditions"]):
        for item in cond["evidence"]:
            return f"{cond['id']} RVA 0x{item['rva']:X}: {item['text']}"
    return ""


def evaluate(run_dir, truth_path, manifest_path):
    with open(truth_path, newline="", encoding="utf-8") as handle:
        truth = {r["sample_id"]: r for r in csv.DictReader(handle)}
    with open(manifest_path, newline="", encoding="utf-8") as handle:
        roles = {r["sample_id"]: r["role"] for r in csv.DictReader(handle)}
    run_doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    report, all_rows = {"run_id": run_doc["run_id"], "split": run_doc["split"],
                        "ground_truth_sha256": hashlib.sha256(Path(truth_path).read_bytes()).hexdigest().upper(),
                        "label_status": "provisional, proposed by TV2, not approved by TV4",
                        "detectors": {}}, []
    for folder in sorted((run_dir / "predictions").iterdir()):
        rows = []
        for path in sorted(folder.glob("*.json")):
            pred = json.loads(path.read_text(encoding="utf-8"))
            sample_id = pred["sample"]["sample_id"]
            item = truth[sample_id]
            if item["sha256"].upper() != pred["sample"]["sha256"]:
                raise SystemExit(f"SHA-256 mismatch between prediction and ground truth: {sample_id}")
            outcome = OUTCOME.get((item["label"], pred["verdict"]), "UNKNOWN")
            rows.append({"run_id": run_doc["run_id"], "detector": pred["detector"]["name"],
                         "detector_version": pred["detector"]["version"], "sample_id": sample_id,
                         "role": roles.get(sample_id, ""), "sha256": pred["sample"]["sha256"],
                         "label": item["label"], "verdict": pred["verdict"], "outcome": outcome,
                         "analysis_status": pred["analysis_status"],
                         "analysis_ms": pred["run"]["feature_extraction_ms"],
                         "reason": reason_for(pred, outcome), "evidence": first_evidence(pred)})
        report["detectors"][folder.name] = summarize(rows)
        all_rows.extend(rows)
    return report, all_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--truth", default=str(ROOT / "configs/tv2/ground-truth-provisional.csv"))
    parser.add_argument("--manifest", default=str(ROOT / "configs/tv2/manifest-provisional.csv"))
    parser.add_argument("--out-dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    report, rows = evaluate(run_dir, args.truth, args.manifest)
    out = Path(args.out_dir) if args.out_dir else run_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    with open(out / "per-sample.csv", "w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
