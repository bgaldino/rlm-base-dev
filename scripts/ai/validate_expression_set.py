#!/usr/bin/env python3
"""Validate a BRE Expression Set definition or overlay JSON file.

Thin CLI wrapper around ``tasks/expression_set_schema.py`` for CI and manual
use (no org / CumulusCI needed). The same validator runs as a pre-flight inside
the ``apply_expression_set_overlay`` / ``import_expression_set`` CCI tasks.

Usage:
    python scripts/ai/validate_expression_set.py <file.json> [--overlay|--definition]
    python scripts/ai/validate_expression_set.py <file.json> --strict   # warnings fail too

Auto-detects shape when neither --overlay nor --definition is given: a file with
top-level overlay operation keys (addSteps/removeSteps/...) is treated as an
overlay; one with a ``versions`` array as a definition.

Exit codes: 0 = no errors (and no warnings under --strict), 1 = validation
failed, 2 = bad invocation / unreadable file.
"""
import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from tasks.expression_set_schema import (  # noqa: E402
    OVERLAY_OPS,
    validate_definition,
    validate_overlay,
)


def _detect_kind(data: dict) -> str:
    if isinstance(data, dict) and data.keys() & OVERLAY_OPS:
        return "overlay"
    if isinstance(data, dict) and "versions" in data:
        return "definition"
    # Default to overlay — it's the more common author-facing artifact.
    return "overlay"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Path to the JSON file to validate.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--overlay", action="store_true", help="Force overlay validation.")
    group.add_argument(
        "--definition", action="store_true", help="Force full-definition validation."
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures."
    )
    args = parser.parse_args(argv)

    try:
        data = json.loads(open(args.file, encoding="utf-8").read())
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {args.file}: {exc}", file=sys.stderr)
        return 2

    if args.definition:
        kind = "definition"
    elif args.overlay:
        kind = "overlay"
    else:
        kind = _detect_kind(data)

    result = validate_definition(data) if kind == "definition" else validate_overlay(data)

    print(f"Validating {args.file} as {kind}:")
    print(result.format_report())

    if result.errors:
        return 1
    if args.strict and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
