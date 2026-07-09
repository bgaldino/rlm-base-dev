#!/usr/bin/env python3
"""Build a hydration-payload skeleton for a Context Definition (read-only).

Constructs the nested ``data`` JSON payload that ``POST /connect/contexts``
(create) — and therefore ``create_context_instance.py`` / ``context_session.py``
— feed to hydrate a runtime context **instance**. Each array is keyed by the
**context node** name; each record carries ``id``, ``businessObjectType``
(the node's **mapped SObject** name, e.g. ``Quote`` — not the node name), its
attributes, and any child nodes as nested arrays::

    {"SalesTransaction": [{"id": "0Q0...", "businessObjectType": "Quote",
                           "SalesTransactionName": "...",
                           "SalesTransactionItem": [
                               {"id": "0QL...", "businessObjectType": "QuoteLineItem", ...}]}]}

That shape is easy to get wrong by hand — the array key is the node name, but
``businessObjectType`` must be the **mapped SObject name** (a node-name
``businessObjectType`` hydrates zero records, live-verified), and child arrays
are named by node. This tool fetches the definition (one Connect GET), resolves
the mapping's node→SObject lookup, walks the node tree, and emits a
correctly-shaped **skeleton** with typed placeholders. Fill in real ids/values,
then pipe it to ``create_context_instance.py`` / ``context_session.py`` via
``--data-file``.

Two modes:

* **skeleton** (default) — every attribute as a fillable placeholder and each
  child node as a nested array, for hand-authoring a payload (including what-if
  attribute *overrides*).
* **``--from-record <rootId>``** — the minimal **id-only** payload
  ``{nodeName: [{"id": <rootId>, "businessObjectType": <mapped SObject>}]}`` for a
  real record. Ready to run as-is: an id-only record hydrates the mapped SObject
  **and its child nodes** server-side (the runtime walks the mapping tree and
  queries children itself — live-verified), so no attribute placeholders or child
  arrays are emitted. Pick the root node with ``--node`` when the definition has
  more than one top-level node.

Read-only: this only GETs the definition; it never mutates the org. Auth is
delegated to the ``sf`` CLI (see ``_client``) — no access token is handled.
``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), not the CCI alias.

Pinned to Release 262 / v67.0 — the node-tree walk mirrors ``describe_context.py``.

Usage:
    # skeleton for the whole definition -> stdout
    python scripts/context_service/build_hydration_data.py \
        --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext

    # restrict to one subtree and write a file to fill in
    python scripts/context_service/build_hydration_data.py \
        --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext \
        --node SalesTransactionItem --out /tmp/records.json

    # id-only payload for a real record, ready to hydrate (parent + children)
    python scripts/context_service/build_hydration_data.py \
        --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext \
        --from-record 0Q0O9000005sX7NKAU --out /tmp/records.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._client import (  # noqa: E402
    ContextClientError,
    DEFAULT_API_VERSION,
    eprint,
)
from scripts.context_service._resolve import (  # noqa: E402
    fetch_detail,
    iter_context_mappings,
    resolve_definition_id,
    resolve_mapping,
)
from scripts.context_service._runtime import (  # noqa: E402
    build_from_record_skeleton,
    build_hydration_skeleton,
)


def _select_mapping(detail, mapping_name):
    """Pick the context mapping dict to shape ``businessObjectType`` against.

    Delegates SELECTION to ``_resolve.resolve_mapping`` (the same helper the
    runtime create/persist path uses) so build-time and runtime pick the same
    mapping and fail identically: with ``mapping_name`` set it matches by name,
    else it selects the ``isDefault`` mapping. On no default / unknown name it
    raises ``ValueError`` with the "Available mappings: …" text — there is **no**
    silent node-name fallback, since a node-name ``businessObjectType`` hydrates
    zero records (live-verified). Returns the resolved mapping **dict** (the
    caller needs it for the node→SObject lookup).
    """
    _, mapping_id = resolve_mapping(detail, mapping_name)
    for mapping in iter_context_mappings(detail):
        if (mapping.get("contextMappingId") or mapping.get("id")) == mapping_id:
            return mapping
    # resolve_mapping returned an id off this detail's active version, so the
    # lookup above always matches; guard defensively rather than return None.
    raise ValueError(
        f"Resolved context mapping id '{mapping_id}' is not on the active version."
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a hydration-payload skeleton for a Context Definition."
    )
    parser.add_argument(
        "--target-org",
        required=True,
        help="SF CLI alias or username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--developer-name", help="DeveloperName of the definition.")
    source.add_argument(
        "--context-definition-id", help="ContextDefinitionId (prefix 11O)."
    )
    parser.add_argument(
        "--node",
        action="append",
        dest="nodes",
        metavar="NAME",
        help="Restrict output to this node's subtree (repeatable). "
        "Default: every top-level node. With --from-record, names the single "
        "top-level node the record id belongs to (only needed when the definition "
        "has more than one).",
    )
    parser.add_argument(
        "--from-record",
        metavar="ROOT_ID",
        help="Emit a minimal id-only payload for this real root record instead of "
        "a placeholder skeleton. Ready to hydrate as-is — the runtime queries the "
        "record and its children server-side.",
    )
    parser.add_argument(
        "--mapping-name",
        metavar="NAME",
        help="Context mapping to shape 'businessObjectType' against (its node→SObject "
        "map). Default: the definition's default mapping. The right mapping matters — "
        "hydration keys on the mapped SObject name, not the node name.",
    )
    parser.add_argument(
        "--api-version", default=DEFAULT_API_VERSION,
        help=f"Salesforce API version (default {DEFAULT_API_VERSION})."
    )
    parser.add_argument("--out", help="Write the skeleton here. Default: stdout.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Suppress the stderr commentary (stdout is JSON either way).",
    )
    args = parser.parse_args(argv)

    try:
        context_definition_id = args.context_definition_id
        if not context_definition_id:
            context_definition_id = resolve_definition_id(
                args.developer_name,
                target_org=args.target_org,
                api_version=args.api_version,
            )
            if not context_definition_id:
                eprint(
                    f"Error: no context definition found with developerName "
                    f"'{args.developer_name}' in org '{args.target_org}'."
                )
                return 1
        detail = fetch_detail(
            context_definition_id,
            target_org=args.target_org,
            api_version=args.api_version,
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if not detail:
        eprint("Error: empty or unexpected response for the context definition.")
        return 1

    try:
        mapping = _select_mapping(detail, args.mapping_name)
    except ValueError as exc:
        # No default mapping / unknown mapping name — fail fast (exit 2) exactly
        # as the runtime create/persist path does, rather than emit a skeleton
        # whose 'businessObjectType' falls back to node names and hydrates zero
        # records silently.
        eprint(f"Error: {exc}")
        return 2

    if args.from_record:
        if args.nodes and len(args.nodes) > 1:
            eprint(
                "Error: --from-record takes a single root node; pass at most one "
                f"--node (got {args.nodes})."
            )
            return 2
        node_name = args.nodes[0] if args.nodes else None
        skeleton, err = build_from_record_skeleton(
            detail, root_id=args.from_record, node_name=node_name, mapping=mapping
        )
        if err:
            eprint(f"Error: {err}")
            return 1
    else:
        skeleton = build_hydration_skeleton(
            detail, node_filter=args.nodes, mapping=mapping
        )
        if not skeleton:
            eprint(
                "Error: no nodes matched"
                + (f" {args.nodes}" if args.nodes else "")
                + " on the active version — nothing to build."
            )
            return 1

    text = json.dumps(skeleton, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(text + "\n", encoding="utf-8")
        eprint(f"Wrote hydration payload: {out_path}")
    else:
        print(text)

    if not args.json:
        map_note = (
            f" ('{mapping.get('name')}')" if mapping and mapping.get("name") else ""
        )
        if args.from_record:
            eprint(
                "\nid-only payload: ready to hydrate as-is — feed it to "
                "create_context_instance.py / context_session.py via --data-file. "
                "The runtime queries this record and its child nodes server-side, "
                "so no attributes or child arrays are needed. 'businessObjectType' "
                f"is the MAPPED SObject name from the mapping{map_note} (e.g. "
                "'Quote'), NOT the context node name that keys the array "
                "(live-verified). Add inline attribute values only to OVERRIDE the "
                "org-queried ones (use the default skeleton mode for that)."
            )
        else:
            eprint(
                "\nSkeleton note: fill in each record's 'id' (the source SObject "
                "record id) and attribute values, then feed it to "
                "create_context_instance.py / context_session.py via --data-file. "
                "'businessObjectType' and the child-node array names are required — "
                "leave them as emitted. 'businessObjectType' is the MAPPED SObject "
                f"name from the mapping{map_note} (e.g. 'Quote'), NOT the context "
                "node name that keys the array — an id-only record hydrates from the "
                "org when its 'businessObjectType' matches the mapping "
                "(live-verified). Or use --from-record <id> for a ready-to-run "
                "id-only payload."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
