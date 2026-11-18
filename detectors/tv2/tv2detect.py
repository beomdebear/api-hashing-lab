#!/usr/bin/env python3
"""Command-line entry point of the TV2 static detector."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tv2features  # noqa: E402
import tv2rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXTRACTOR = ROOT / "configs" / "tv2" / "extractor.json"


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_json(value, path):
    text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)


def features_for(input_path, extractor_config):
    if str(input_path).lower().endswith(".json"):
        return load_json(input_path)
    return tv2features.extract(input_path, load_json(extractor_config))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract", help="write static features for one binary")
    extract.add_argument("binary")
    extract.add_argument("-o", "--output")
    extract.add_argument("--extractor-config", default=DEFAULT_EXTRACTOR)
    detect = sub.add_parser("detect", help="apply a rule configuration")
    detect.add_argument("input", help="binary, or a features .json file")
    detect.add_argument("--config", required=True)
    detect.add_argument("-o", "--output")
    detect.add_argument("--extractor-config", default=DEFAULT_EXTRACTOR)
    validate = sub.add_parser("validate", help="validate JSON files against a schema")
    validate.add_argument("schema")
    validate.add_argument("files", nargs="+")
    args = parser.parse_args(argv)

    if args.command == "extract":
        doc = tv2features.extract(args.binary, load_json(args.extractor_config))
        write_json(doc, args.output)
        return 0 if doc["analysis"]["status"] in ("ok", "partial") else 2
    if args.command == "detect":
        doc = features_for(args.input, args.extractor_config)
        prediction = tv2rules.evaluate(doc, load_json(args.config))
        write_json(prediction, args.output)
        return 0 if prediction["verdict"] != "unknown" else 2
    import jsonschema
    schema = load_json(args.schema)
    validator = jsonschema.Draft202012Validator(schema)
    failures = 0
    for name in args.files:
        errors = sorted(validator.iter_errors(load_json(name)), key=lambda e: list(e.path))
        for error in errors:
            print(f"{name}: {list(error.path)}: {error.message}")
        failures += bool(errors)
    print(f"validated={len(args.files)} failed={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
