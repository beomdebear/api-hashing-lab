"""Evaluates a versioned rule configuration against one feature document.

A rule sees only the feature document. Conditions are three-valued, so missing
evidence caused by a failed analysis gives ``unknown`` and never ``negative``.
"""
from __future__ import annotations

from datetime import datetime, timezone

from tv2features import canonical_digest

SCHEMA = "tv2-prediction/1.0"
UNAVAILABLE = {"unknown", "analysis_error"}


def _condition(cond, features):
    feature = features.get(cond["feature"])
    if feature is None or feature["status"] in UNAVAILABLE:
        return None, feature
    op = cond["op"]
    if op == "is_true":
        return bool(feature["value"]), feature
    if op == "gte":
        return (feature["value"] or 0) >= cond["value"], feature
    if op == "relation_verified":
        return feature["status"] == "verified", feature
    raise ValueError(f"unknown rule operator: {op}")


def evaluate(doc, config):
    results = []
    for cond in config["conditions"]:
        passed, feature = _condition(cond, doc["features"])
        results.append({
            "id": cond["id"], "feature": cond["feature"], "op": cond["op"],
            "expected": cond.get("value"), "passed": passed,
            "observed_status": feature["status"] if feature else "missing_feature",
            "observed_value": feature["value"] if feature else None,
            "evidence": feature["evidence"][:4] if feature and passed else [],
        })
    outcomes = [r["passed"] for r in results]
    status = doc["analysis"]["status"]
    if status in ("error", "unsupported"):
        verdict = "unknown"
    elif False in outcomes:
        verdict = "negative"
    elif None in outcomes:
        verdict = "unknown"
    else:
        verdict = "positive"
    if verdict == "negative" and status == "partial" and config.get("partial_negative_is_unknown", True):
        verdict = "unknown"
    fired = [config["rule_id"]] if verdict == "positive" else []
    failed = [r["id"] for r in results if r["passed"] is False]
    return {
        "schema": SCHEMA,
        "detector": {"name": config["detector"], "version": config["version"],
                     "config_sha256": canonical_digest(config)},
        "sample": {"sha256": doc["sample"]["sha256"]},
        "features_content_sha256": doc["content_sha256"],
        "extractor": doc["extractor"],
        "analysis_status": status,
        "analysis_detail": doc["analysis"]["detail"],
        "verdict": verdict,
        "rules_fired": fired,
        "failed_conditions": failed,
        "conditions": results,
        "run": {"analysis_id": doc["run"]["analysis_id"],
                "predicted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "feature_extraction_ms": doc["run"]["duration_ms"]},
    }
