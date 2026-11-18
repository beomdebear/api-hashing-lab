#!/usr/bin/env python3
"""TV2 detector tests. Real binaries come only from the development split."""
from __future__ import annotations

import csv
import json
import re
import shutil
import struct
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "detectors" / "tv2"))
import jsonschema  # noqa: E402
import tv2analysis as ta  # noqa: E402
import tv2d1adapter  # noqa: E402
import tv2evaluate  # noqa: E402
import tv2features  # noqa: E402
import tv2freeze  # noqa: E402
import tv2rules  # noqa: E402
import tv2run  # noqa: E402

CONFIG = ROOT / "configs" / "tv2"
SCHEMA = ROOT / "schemas" / "tv2"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


EXTRACTOR, D0, STATIC = load(CONFIG / "extractor.json"), load(CONFIG / "d0.json"), load(CONFIG / "static-only.json")


def dev_rows():
    with open(CONFIG / "manifest-provisional.csv", newline="", encoding="utf-8") as handle:
        return {r["role"]: r for r in csv.DictReader(handle) if r["split"] == "dev"}


ROWS = dev_rows()
HAVE_BINARIES = all((ROOT / r["binary"]).is_file() for r in ROWS.values())


def extract(path):
    return tv2features.extract(path, EXTRACTOR)


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


class InvalidInputs(Temp):
    def assert_unknown(self, doc, status):
        self.assertEqual(doc["analysis"]["status"], status)
        for config in (D0, STATIC):
            self.assertEqual(tv2rules.evaluate(doc, config)["verdict"], "unknown")

    def test_missing_file(self):
        self.assert_unknown(extract(self.tmp / "missing.bin"), "error")

    def test_not_a_pe(self):
        path = self.tmp / "x.bin"
        path.write_bytes(b"this is not a PE file" * 8)
        self.assert_unknown(extract(path), "error")

    @unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
    def test_truncated_pe(self):
        path = self.tmp / "x.bin"
        path.write_bytes((ROOT / ROWS["P1"]["binary"]).read_bytes()[:0x180])
        self.assert_unknown(extract(path), "error")

    @unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
    def test_unsupported_machine(self):
        data = bytearray((ROOT / ROWS["P1"]["binary"]).read_bytes())
        nt = struct.unpack_from("<I", data, 0x3C)[0]
        struct.pack_into("<H", data, nt + 4, 0x14C)
        path = self.tmp / "x.bin"
        path.write_bytes(data)
        self.assert_unknown(extract(path), "unsupported")


@unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
class RealBinaries(Temp):
    def test_rename_and_move_do_not_change_content(self):
        source = ROOT / ROWS["P1"]["binary"]
        moved = self.tmp / "deep" / "benign_B1_label.exe"
        moved.parent.mkdir()
        shutil.copyfile(source, moved)
        first, second = extract(source), extract(moved)
        self.assertEqual(first["content_sha256"], second["content_sha256"])
        self.assertEqual(first["features"], second["features"])
        self.assertEqual(tv2rules.evaluate(first, STATIC)["verdict"], tv2rules.evaluate(second, STATIC)["verdict"])

    def test_negative_binary_named_like_positive_stays_negative(self):
        moved = self.tmp / "P1_djb2_api_hashing.exe"
        shutil.copyfile(ROOT / ROWS["B2"]["binary"], moved)
        doc = extract(moved)
        self.assertEqual(tv2rules.evaluate(doc, STATIC)["verdict"], "negative")
        self.assertEqual(tv2rules.evaluate(doc, D0)["verdict"], "negative")

    def test_repeat_is_stable(self):
        path = ROOT / ROWS["B1"]["binary"]
        self.assertEqual(extract(path)["content_sha256"], extract(path)["content_sha256"])

    def test_outputs_match_schemas(self):
        features = jsonschema.Draft202012Validator(load(SCHEMA / "static-features-1.0.schema.json"))
        prediction = jsonschema.Draft202012Validator(load(SCHEMA / "prediction-1.0.schema.json"))
        for row in ROWS.values():
            doc = extract(ROOT / row["binary"])
            features.validate(doc)
            prediction.validate(tv2rules.evaluate(doc, D0))
            prediction.validate(tv2rules.evaluate(doc, STATIC))

    def test_error_document_matches_schema(self):
        doc = extract(self.tmp / "missing.bin")
        jsonschema.Draft202012Validator(load(SCHEMA / "static-features-1.0.schema.json")).validate(doc)
        jsonschema.Draft202012Validator(load(SCHEMA / "prediction-1.0.schema.json")).validate(tv2rules.evaluate(doc, D0))

    def test_all_chain_evidence_is_in_one_binary(self):
        doc = extract(ROOT / ROWS["P1"]["binary"])
        size = doc["sample"]["size"]
        for name, feature in doc["features"].items():
            if name.startswith("rel."):
                self.assertEqual(feature["status"], "verified", name)
                for item in feature["evidence"]:
                    self.assertLess(item["file_offset"], size)
                    self.assertEqual(item["va"], doc["pe"]["image_base"] + item["rva"])

    def test_removing_the_compare_breaks_the_chain(self):
        """Synthetic fixture: patch P1's hash comparison into NOPs."""
        data = bytearray((ROOT / ROWS["P1"]["binary"]).read_bytes())
        doc = extract(ROOT / ROWS["P1"]["binary"])
        evidence = doc["features"]["rel.hash_to_compare"]["evidence"][0]
        offset = evidence["file_offset"]
        self.assertEqual(evidence["text"].split()[0], "cmp")
        data[offset:offset + 4] = b"\x90" * 4
        path = self.tmp / "patched.bin"
        path.write_bytes(data)
        patched = extract(path)
        self.assertEqual(patched["features"]["rel.export_name_to_hash"]["status"], "verified")
        self.assertNotEqual(patched["features"]["rel.hash_to_compare"]["status"], "verified")
        result = tv2rules.evaluate(patched, STATIC)
        self.assertEqual(result["verdict"], "negative")
        self.assertIn("SR-C3", result["failed_conditions"])


class AnalyzerRobustness(Temp):
    def test_negative_shift_count_is_masked(self):
        self.assertEqual(ta._fold_constant("shl", 1, -1), -(1 << 63))
        self.assertEqual(ta._fold_constant("shl", 1, 65), 2)
        self.assertIsNone(ta._fold_constant("shr", 8, 1))

    @unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
    def test_internal_failure_is_an_error_not_benign(self):
        original = ta.analyze
        def broken(_pe):
            raise ValueError("simulated analyzer defect")
        ta.analyze = broken
        self.addCleanup(setattr, ta, "analyze", original)
        doc = extract(ROOT / ROWS["B1"]["binary"])
        self.assertEqual(doc["analysis"]["status"], "error")
        self.assertIn("simulated analyzer defect", doc["analysis"]["detail"])
        self.assertEqual(tv2rules.evaluate(doc, STATIC)["verdict"], "unknown")


class Rules(unittest.TestCase):
    def doc(self, status="ok", value=True, feature_status="present"):
        features = {c["feature"]: {"status": feature_status, "value": value, "evidence": []} for c in D0["conditions"]}
        return {"features": features, "analysis": {"status": status, "detail": ""}, "sample": {"sha256": "A" * 64},
                "content_sha256": "B" * 64, "extractor": {}, "run": {"analysis_id": "x", "duration_ms": 1.0}}

    def test_all_conditions_true(self):
        self.assertEqual(tv2rules.evaluate(self.doc(), D0)["verdict"], "positive")

    def test_one_condition_false(self):
        doc = self.doc()
        doc["features"]["f.code.hash_like_loops"]["value"] = 0
        self.assertEqual(tv2rules.evaluate(doc, D0)["verdict"], "negative")

    def test_unknown_feature_is_not_benign(self):
        self.assertEqual(tv2rules.evaluate(self.doc(feature_status="unknown", value=None), D0)["verdict"], "unknown")

    def test_partial_analysis_cannot_give_negative(self):
        doc = self.doc(status="partial")
        doc["features"]["f.code.hash_like_loops"]["value"] = 0
        self.assertEqual(tv2rules.evaluate(doc, D0)["verdict"], "unknown")


class Evaluator(Temp):
    def write_run(self, cases):
        run = self.tmp / "run"
        folder = run / "predictions" / "d0"
        folder.mkdir(parents=True)
        (run / "run.json").write_text(json.dumps({"run_id": "R-test", "split": "fixture"}), encoding="utf-8")
        truth, manifest = [], []
        for index, (label, verdict) in enumerate(cases):
            sha = f"{index:064X}"
            sample = f"S-{index}"
            truth.append({"sample_id": sample, "sha256": sha, "label": label})
            manifest.append({"sample_id": sample, "role": f"role{index}"})
            (folder / f"{sample}.json").write_text(json.dumps({
                "sample": {"sample_id": sample, "sha256": sha}, "detector": {"name": "D0", "version": "t"},
                "verdict": verdict, "analysis_status": "error" if verdict == "unknown" else "ok", "analysis_detail": "",
                "failed_conditions": ["C"] if verdict == "negative" else [],
                "conditions": [{"id": "C", "evidence": []}], "run": {"feature_extraction_ms": 1.0}}), encoding="utf-8")
        for name, rows in (("truth.csv", truth), ("manifest.csv", manifest)):
            with open(self.tmp / name, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        return tv2evaluate.evaluate(run, self.tmp / "truth.csv", self.tmp / "manifest.csv")

    def test_known_confusion_matrix(self):
        report, _ = self.write_run([("positive", "positive"), ("positive", "positive"), ("positive", "negative"),
                                    ("negative", "negative"), ("negative", "positive"), ("positive", "unknown")])
        result = report["detectors"]["d0"]
        self.assertEqual(result["counts"], {"TP": 2, "TN": 1, "FP": 1, "FN": 1, "UNKNOWN": 1})
        self.assertEqual((result["precision"], result["recall"]), (0.6667, 0.6667))
        self.assertEqual(result["worst_case"]["recall"], 0.5)
        self.assertEqual(result["analysis_succeeded"], 5)

    def test_zero_denominator_is_null(self):
        report, _ = self.write_run([("negative", "negative")])
        result = report["detectors"]["d0"]
        self.assertIsNone(result["precision"])
        self.assertIsNone(result["recall"])
        self.assertIsNone(result["f1"])

    def test_unknown_is_not_counted_as_benign(self):
        report, rows = self.write_run([("negative", "unknown")])
        self.assertEqual(report["detectors"]["d0"]["counts"]["TN"], 0)
        self.assertEqual(rows[0]["outcome"], "UNKNOWN")


class Pipeline(Temp):
    def manifest(self, rows):
        path = self.tmp / "manifest.csv"
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return path

    @unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
    def test_sha_mismatch_is_reported_and_not_benign(self):
        row = dict(ROWS["B1"], sha256="0" * 64)
        args = Namespace(manifest=str(self.manifest([row])), split="dev", detectors="d0,static-only",
                         out_root=str(self.tmp / "out"), lock=None, keep_input=False)
        out = tv2run.run(args)
        prediction = load(out / "predictions" / "d0" / f"{row['sample_id']}.json")
        self.assertEqual(prediction["analysis_status"], "error")
        self.assertEqual(prediction["analysis_detail"], "sha256_mismatch")
        self.assertEqual(prediction["verdict"], "unknown")

    def test_test_split_requires_lock(self):
        args = Namespace(manifest=str(CONFIG / "manifest-provisional.csv"), split="test", detectors="d0",
                         out_root=str(self.tmp / "out"), lock=None, keep_input=False)
        with self.assertRaises(SystemExit):
            tv2run.run(args)

    def test_lock_detects_a_changed_file(self):
        lock = self.tmp / "lock.json"
        files = tv2freeze.current_files()
        first = next(iter(files))
        files[first] = "0" * 64
        lock.write_text(json.dumps({"files_sha256": files}), encoding="utf-8")
        self.assertEqual(tv2freeze.verify(lock), [first])


class D1Contract(Temp):
    """Contract test with mock documents; this is not a D1 integration."""

    def schema(self):
        return jsonschema.Draft202012Validator(load(SCHEMA / "d1-static-input-1.0.schema.json"))

    def test_failed_analysis_maps_to_null_and_missing(self):
        record = tv2d1adapter.adapt(extract(self.tmp / "missing.bin"))
        self.schema().validate(dict(record, sha256=None))
        self.assertIsNone(record["values"]["hash_to_compare"])
        self.assertIn("hash_to_compare", record["missing"])

    @unittest.skipUnless(HAVE_BINARIES, "development binaries are not built")
    def test_verified_chain_maps_to_one(self):
        record = tv2d1adapter.adapt(extract(ROOT / ROWS["P1"]["binary"]))
        self.schema().validate(record)
        self.assertEqual(record["values"]["selection_to_resolve"], 1.0)
        self.assertEqual(record["missing"], [])


class Leakage(unittest.TestCase):
    FORBIDDEN = re.compile(r"ground-truth|tv1-hash-values|manifest-provisional|samples[/\\]|tv1_|audit", re.I)

    def test_detector_code_reads_no_oracle(self):
        for name in ("tv2pe.py", "tv2analysis.py", "tv2features.py", "tv2rules.py"):
            text = (ROOT / "detectors" / "tv2" / name).read_text(encoding="utf-8")
            self.assertIsNone(self.FORBIDDEN.search(text), name)

    def test_runner_does_not_read_ground_truth(self):
        self.assertNotIn("ground-truth", (ROOT / "detectors" / "tv2" / "tv2run.py").read_text(encoding="utf-8"))

    def test_rule_configs_use_only_features(self):
        for config in (D0, STATIC):
            for condition in config["conditions"]:
                self.assertRegex(condition["feature"], r"^(f|rel)\.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
