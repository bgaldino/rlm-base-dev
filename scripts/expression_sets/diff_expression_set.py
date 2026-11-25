#!/usr/bin/env python3
"""Diff two BRE Expression Set definitions: steps + variables (read-only).

Compares a *left* and *right* definition and reports added / removed / changed
steps and variables. Each side is either a live org (``--developer-name`` +
``--target-org`` / ``--right-org``) or a JSON file (``--left-file`` /
``--right-file`` — the shape ``export_expression_set.py`` writes). Typical uses:

* **org vs org** — did the migration land? (source org left, target org right)
* **org vs file** — has the live procedure drifted from the exported snapshot?
* **file vs file** — what changed between two exports?

Each side is one version: an org side's ``--left-version`` / ``--right-version``,
else the version that executes (never the GET's first); a file side's named
version, else its only version (a file with several versions needs the option).

Steps are keyed by ``name`` and compared field-by-field after HTML-unescaping
both sides (so a GET-escaped left vs a clean right does not show phantom
changes). ``sequenceNumber`` differences are reported (order changes) but flagged
distinctly from content changes.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` / ``--right-org`` are *SF CLI* aliases, never CCI aliases.
Read-only. Pinned to Release 262 / v67.0.

Usage
-----
    # org vs org (same developer name in two orgs)
    python scripts/expression_sets/diff_expression_set.py \
        --developer-name RLM_DefaultPricingProcedure \
        --target-org rlm-base__A --right-org rlm-base__B

    # live org vs an exported snapshot
    python scripts/expression_sets/diff_expression_set.py \
        --developer-name RLM_DefaultPricingProcedure \
        --target-org rlm-base__beta --right-file /tmp/pricing.json

    # two files
    python scripts/expression_sets/diff_expression_set.py \
        --left-file /tmp/before.json --right-file /tmp/after.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    eprint,
)
from scripts.expression_sets._guards import select_version  # noqa: E402
from scripts.expression_sets._payload import unescape_value  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
    resolve_target_row,
)
from scripts.expression_sets.export_expression_set import fetch_definition  # noqa: E402

# Step fields whose change is noise, not signal.
_IGNORE_STEP_FIELDS = {"id"}


def _load_side(name: str, *, dev_name, org, file, api_version, version=None) -> dict:
    """Return the (unescaped) version block one side of the diff compares.

    An org side uses ``version``, else the executing version (never the GET's
    first), matched in the GET by VersionNumber. A file side uses ``version``; a
    file with one version gives that version; a file with several and no
    ``version`` is refused.
    """
    flag = f"--{name.lower()}-version"
    if file:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
        if isinstance(data, list):
            data = data[0] if data else {}
        versions = (data.get("versions") or []) if isinstance(data, dict) else []
        block = select_version(versions, version)
        if block is None:
            raise ExpressionSetClientError(
                f"{name} file {file} has no version '{version}'." if version else
                f"{name} file {file} has {len(versions)} versions; name one with {flag}.")
        return unescape_value(block)
    if not dev_name:
        raise ExpressionSetClientError(
            f"{name} side needs either a --*-file or a --developer-name + org."
        )
    es_id = resolve_expression_set_id(dev_name, target_org=org, api_version=api_version)
    definition = fetch_definition(es_id, org, api_version)
    row = resolve_target_row(es_id, version, target_org=org, api_version=api_version,
                             logger=eprint)
    block = select_version(definition.get("versions") or [], row.get("ApiName"),
                           row.get("VersionNumber"))
    if block is None:
        raise ExpressionSetClientError(
            f"{name} side: version '{row.get('ApiName')}' (v{row.get('VersionNumber')}) "
            "not found in the definition.")
    return unescape_value(block)


def _steps_by_name(version: dict) -> Dict[str, dict]:
    return {s.get("name"): s for s in (version.get("steps") or []) if isinstance(s, dict)}


def _vars_by_name(version: dict) -> Dict[str, dict]:
    return {v.get("name"): v for v in (version.get("variables") or []) if isinstance(v, dict)}


def _changed_fields(left: dict, right: dict) -> List[str]:
    fields = (set(left) | set(right)) - _IGNORE_STEP_FIELDS
    changed = []
    for f in sorted(fields):
        if left.get(f) != right.get(f):
            changed.append(f)
    return changed


def diff_versions(lv: dict, rv: dict) -> dict:
    """Diff two version blocks (steps and variables)."""
    lsteps, rsteps = _steps_by_name(lv), _steps_by_name(rv)
    lvars, rvars = _vars_by_name(lv), _vars_by_name(rv)

    added_steps = sorted(set(rsteps) - set(lsteps))
    removed_steps = sorted(set(lsteps) - set(rsteps))
    changed_steps = []
    reordered_steps = []
    for name in sorted(set(lsteps) & set(rsteps)):
        fields = _changed_fields(lsteps[name], rsteps[name])
        seq_only = fields == ["sequenceNumber"]
        if seq_only:
            reordered_steps.append({
                "name": name,
                "from": lsteps[name].get("sequenceNumber"),
                "to": rsteps[name].get("sequenceNumber"),
            })
        elif fields:
            changed_steps.append({"name": name, "changedFields": fields})

    return {
        "addedSteps": added_steps,
        "removedSteps": removed_steps,
        "changedSteps": changed_steps,
        "reorderedSteps": reordered_steps,
        "addedVariables": sorted(set(rvars) - set(lvars)),
        "removedVariables": sorted(set(lvars) - set(rvars)),
        "changedVariables": [
            n for n in sorted(set(lvars) & set(rvars)) if lvars[n] != rvars[n]
        ],
    }


def _print_diff(d: dict, left_label: str, right_label: str):
    print(f"Diff  {left_label}  →  {right_label}\n")
    total = (len(d["addedSteps"]) + len(d["removedSteps"]) + len(d["changedSteps"])
             + len(d["reorderedSteps"]) + len(d["addedVariables"])
             + len(d["removedVariables"]) + len(d["changedVariables"]))
    if total == 0:
        print("  identical (no step or variable differences).")
        return

    def section(title, items, render):
        if items:
            print(f"  {title} ({len(items)}):")
            for it in items:
                print(f"    {render(it)}")
            print()

    section("+ added steps", d["addedSteps"], lambda n: f"+ {n}")
    section("- removed steps", d["removedSteps"], lambda n: f"- {n}")
    section("~ changed steps", d["changedSteps"],
            lambda c: f"~ {c['name']}  ({', '.join(c['changedFields'])})")
    section("↕ reordered steps", d["reorderedSteps"],
            lambda r: f"↕ {r['name']}  seq {r['from']} → {r['to']}")
    section("+ added variables", d["addedVariables"], lambda n: f"+ {n}")
    section("- removed variables", d["removedVariables"], lambda n: f"- {n}")
    section("~ changed variables", d["changedVariables"], lambda n: f"~ {n}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Diff two BRE Expression Set definitions (steps + variables). "
                    "Read-only.",
    )
    parser.add_argument("--developer-name",
                        help="ExpressionSetDefinition DeveloperName (used for org sides).")
    parser.add_argument("--target-org",
                        help="LEFT-side SF CLI alias (with --developer-name).")
    parser.add_argument("--right-org",
                        help="RIGHT-side SF CLI alias (defaults to --target-org).")
    parser.add_argument("--left-file", help="LEFT side from a JSON export file instead of an org.")
    parser.add_argument("--right-file", help="RIGHT side from a JSON export file instead of an org.")
    parser.add_argument("--left-version",
                        help="LEFT version apiName (org default: the executing version; "
                             "required for a file with several versions).")
    parser.add_argument("--right-version",
                        help="RIGHT version apiName (org default: the executing version; "
                             "required for a file with several versions).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the diff as JSON.")
    args = parser.parse_args(argv)

    if not args.left_file and not (args.developer_name and args.target_org):
        eprint("Error: LEFT side needs --left-file, or --developer-name + --target-org.")
        return 2
    if not args.right_file and not (args.developer_name and (args.right_org or args.target_org)):
        eprint("Error: RIGHT side needs --right-file, or --developer-name + "
               "--right-org/--target-org.")
        return 2

    try:
        left = _load_side("LEFT", dev_name=args.developer_name, org=args.target_org,
                          file=args.left_file, api_version=args.api_version,
                          version=args.left_version)
        right = _load_side("RIGHT", dev_name=args.developer_name,
                           org=args.right_org or args.target_org,
                           file=args.right_file, api_version=args.api_version,
                           version=args.right_version)
    except (ExpressionSetClientError, ResolveError, ValueError, OSError) as exc:
        eprint(f"Error: {exc}")
        return 1

    result = diff_versions(left, right)
    left_label = args.left_file or f"{args.developer_name}@{args.target_org}"
    right_label = args.right_file or f"{args.developer_name}@{args.right_org or args.target_org}"

    if args.json:
        print(json.dumps({"left": left_label, "right": right_label, "diff": result}, indent=2))
        return 0

    _print_diff(result, left_label, right_label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
