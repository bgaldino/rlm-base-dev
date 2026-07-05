#!/usr/bin/env python3
"""Serialize a live Context Definition back into repo **plan JSON** (read-only).

Fetches one definition (Connect GET), normalizes it through ``_model.py``, and
emits the additive **plan-JSON** format that ``manage_context_definition`` /
``ExtendStandardContext`` consume and ``validate_context_plan.py`` lints — the
inverse of applying a plan. Useful for snapshotting an org's configuration into a
source-controllable plan, or seeding a new plan from a hand-configured org.

NOT a Salesforce-native feature
-------------------------------
Like ``patch_context.py``, this is **repo tooling on top of standard platform
primitives**, not a platform export. Salesforce has no context *export* format;
this reconstructs our own plan-JSON from a standard Connect GET. A round-trip is
therefore only as faithful as our normalizer (``_model.py``) + serializer
(``model_to_plan``) — there is no platform guarantee. Reversals that a read alone
cannot fully recover are **flagged**, never fabricated:

* **CONTEXT-to-CONTEXT mappings** — the GET gives a ``mappedContextDefinitionId``
  (an ID); a plan wants ``sourceContextNode`` / ``sourceContextAttribute``
  (names). v1 emits the ID + a ``_todo`` marker and lists it under ``_caveats``;
  it does **not** invent source node/attribute names.
* **Multi-hop traversal hydration** — the GET flattens the hop chain; the final
  hop is reconstructed best-effort as ``childSObject`` / ``childSObjectField``
  and flagged.

``_caveats`` (and any other ``_``-prefixed key) is ignored by both the CCI task
and the validator, so the emitted plan stays directly consumable. By default the
whole definition is exported; ``--custom-only`` restricts output to the custom
(``__c``) layer a repo plan should own (dropping inherited standard artifacts).

Auth is delegated to the sf CLI (see _client.py) — no tokens handled here.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION  # noqa: E402
from scripts.context_service._model import model_to_plan  # noqa: E402
from scripts.context_service.definition.diff_context import _fetch_model  # noqa: E402


def _is_custom(name: str) -> bool:
    return bool(name) and name.endswith("__c")


def _custom_include(model: dict) -> dict:
    """Build a ``model_to_plan`` include-filter keeping only ``__c`` artifacts.

    Mirrors ``patch_context._filter_custom_keys`` but over a whole model: the
    repo plan should carry only the custom layer, not the inherited standard
    base. The relevant name is the last dotted/slashed segment of each key.
    """
    def tail(key: str, sep: str) -> str:
        return key.rsplit(sep, 1)[-1]

    return {
        "nodes": {n for n in (model.get("nodes") or {}) if _is_custom(n)},
        "attributes": {
            k for k in (model.get("attributes") or {}) if _is_custom(tail(k, "."))
        },
        "tags": {k for k in (model.get("tags") or {}) if _is_custom(tail(k, "."))},
        "mappings": {
            f"{m}/{node}/{attr}"
            for m, mapping in (model.get("mappings") or {}).items()
            for node, node_map in (mapping.get("nodes") or {}).items()
            for attr in (node_map.get("attributes") or {})
            if _is_custom(attr)
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Serialize a live Context Definition into repo plan JSON "
        "(read-only; never mutates an org).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (NOT the CCI alias).",
    )
    parser.add_argument(
        "--developer-name", required=True,
        help="Definition to export (e.g. RLM_SalesTransactionContext).",
    )
    parser.add_argument(
        "--custom-only", action="store_true",
        help="Emit only the custom (__c) layer; drop inherited standard artifacts. "
        "Use when seeding a repo plan that extends a standard base.",
    )
    parser.add_argument(
        "--out",
        help="Write the plan here. Default: stdout JSON.",
    )
    parser.add_argument(
        "--api-version", default=DEFAULT_API_VERSION,
        help=f"API version (default {DEFAULT_API_VERSION}).",
    )
    args = parser.parse_args(argv)

    try:
        model = _fetch_model(args.developer_name, args.target_org, args.api_version)
    except ContextClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if model is None:
        print(
            f"Error: no context definition '{args.developer_name}' in "
            f"{args.target_org}.",
            file=sys.stderr,
        )
        return 1

    include = _custom_include(model) if args.custom_only else None
    plan = model_to_plan(model, include=include)
    caveats = plan.pop("_caveats", [])

    text = json.dumps(plan, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote plan: {out_path}", file=sys.stderr)
    else:
        print(text)

    counts = (
        f"{len(plan.get('contextNodeDefinitions') or [])} nodes, "
        f"{len(plan.get('contextAttributesByName') or [])} attributes, "
        f"{len(plan.get('mappingRules') or [])} mappingRules, "
        f"{len(plan.get('contextTagsByName') or [])} tags"
    )
    print(f"\nExported {args.developer_name}: {counts}"
          f"{' (custom-only)' if args.custom_only else ''}.", file=sys.stderr)
    for cav in caveats:
        print(f"  ! caveat: {cav}", file=sys.stderr)
    print(
        "\nLint before use: "
        "`python scripts/context_service/validate_context_plan.py <file>`. "
        "This is repo tooling, not a Salesforce-native export — verify "
        "CONTEXT-to-CONTEXT / traversal reversals (flagged above).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
