#!/usr/bin/env python3
"""Export a BRE Expression Set definition to a JSON file (read-only).

GETs the full Connect definition for one expression set
(``connect/business-rules/expression-set/{9QL}``) and writes it to a file (or
stdout). This is the read half of the round trip whose write half is
``import_expression_set.py``: export from a source org, then import into a
target.

By default the export is written **verbatim** (exactly what the Connect GET
returned, top-level ``id``/``error`` and all) so it is a faithful snapshot.
``--for-import`` instead shapes it for a downstream PATCH/replace — strips the
output-only top-level fields and HTML-unescapes the string leaves the GET
serializer escaped — so the file is import-ready without a second pass. (Version
``id`` rewrite to the *target* org still happens inside ``import``; a PATCH keeps
the version id, so it is left intact here.)

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens are handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Read-only.
Pinned to Release 262 / v67.0.

Usage
-----
    # faithful snapshot to a file
    python scripts/expression_sets/export_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure \
        --out /tmp/pricing.json

    # import-ready (stripped + HTML-unescaped) to stdout
    python scripts/expression_sets/export_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --for-import
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    CONNECT_BASE,
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    connect_get,
    eprint,
)
from scripts.expression_sets._payload import (  # noqa: E402
    normalize_html_entities,
    strip_readonly_fields,
)
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
)


def fetch_definition(es_id, target_org, api_version):
    """GET the full expression-set definition, normalizing list/dict responses."""
    resp = connect_get(f"{CONNECT_BASE}/{es_id}", target_org, api_version)
    if isinstance(resp, list):
        resp = resp[0] if resp and isinstance(resp[0], dict) else {}
    if not isinstance(resp, dict) or not resp:
        raise ExpressionSetClientError(
            f"Empty or unexpected Connect response for ExpressionSet {es_id}."
        )
    return resp


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a BRE Expression Set definition to JSON. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name",
                       help="ExpressionSetDefinition DeveloperName.")
    ident.add_argument("--expression-set-id",
                       help="Runtime ExpressionSet Id (prefix 9QL).")
    parser.add_argument("--out", help="Output file path (default: stdout).")
    parser.add_argument(
        "--for-import", action="store_true",
        help="Shape the export for a downstream replace/PATCH: strip output-only "
             "top-level fields and HTML-unescape string leaves. Default: verbatim "
             "snapshot.",
    )
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    args = parser.parse_args(argv)

    try:
        es_id = args.expression_set_id
        if not es_id:
            es_id = resolve_expression_set_id(
                args.developer_name,
                target_org=args.target_org, api_version=args.api_version,
            )
        definition = fetch_definition(es_id, args.target_org, args.api_version)
    except (ExpressionSetClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.for_import:
        definition = normalize_html_entities(strip_readonly_fields(definition))

    payload = json.dumps(definition, indent=2)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
        steps = 0
        versions = definition.get("versions") or []
        if versions and isinstance(versions[0], dict):
            steps = len(versions[0].get("steps") or [])
        eprint(f"Wrote {args.out} ({len(versions)} version(s), "
               f"{steps} top step(s) in v0).")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
