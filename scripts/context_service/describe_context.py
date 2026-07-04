#!/usr/bin/env python3
"""Describe one Context Definition in detail (read-only) — the "understand mapping" tool.

GETs a definition via the Connect API and pretty-prints the version-centric
structure: definition -> active version -> nodes -> attributes -> mappings ->
node mappings -> hydration.

Auth is delegated to the sf CLI (see _client.py) — no tokens are handled here.

Usage:
    python scripts/context_service/describe_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext
    python scripts/context_service/describe_context.py --target-org rlm-base__beta \
        --id 0tc... --json

Note: the exact GET response shape is pinned to Release 262 / API v67.0 and
should be re-verified against a live org — this is a "verify-live" tool for its
GET behavior. The parsing mirrors tasks/rlm_context_service.py, which reads the
same endpoint.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _client import (  # noqa: E402
    ContextClientError,
    active_version,
    connect_get,
    definition_developer_name,
    eprint,
    iter_nodes,
    node_attributes,
    normalize_definition_list,
)


def _resolve_id(developer_name: str, target_org: str, api_version: str):
    """Resolve a definition id from a developerName via the list endpoint.

    Uses includeInactive=true so an inactive definition is still resolvable, and
    the shared normalizer/name reader so this matches what list_contexts.py can
    see (response-shape variants + developerName/DeveloperName casing).
    """
    response = connect_get(
        "connect/context-definitions?includeInactive=true",
        target_org,
        api_version,
    )
    for item in normalize_definition_list(response):
        if definition_developer_name(item) == developer_name:
            return item.get("contextDefinitionId")
    return None


def _print_human(defn: dict):
    version = active_version(defn)
    is_active = defn.get("isActive")
    if is_active is None:
        is_active = version.get("isActive")
    print(f"Context Definition: {definition_developer_name(defn) or defn.get('name') or '?'}")
    print(f"  id:        {defn.get('contextDefinitionId')}")
    print(f"  isActive:  {is_active if is_active is not None else '(unknown)'}")
    print(f"  versions:  {len(defn.get('contextDefinitionVersionList') or [])}")
    if defn.get("isUpgradeAvailable") is not None:
        print(f"  upgrade:   {defn.get('isUpgradeAvailable')}")

    # Nodes + attributes.
    print("\nNodes / attributes:")
    nodes = version.get("contextNodes") or []
    if not nodes:
        print("  (none)")
    for node, depth in iter_nodes(nodes):
        indent = "  " + "  " * depth
        print(f"{indent}- {node.get('name')} (id={node.get('contextNodeId')})")
        for attr in node_attributes(node):
            if not isinstance(attr, dict):
                continue
            print(
                f"{indent}    * {attr.get('name')} "
                f"[{attr.get('dataType')}/{attr.get('fieldType')}]"
                + (" transient" if attr.get("isTransient") else "")
            )

    # Mappings -> node mappings -> hydration.
    print("\nMappings:")
    mappings = version.get("contextMappings") or []
    if not mappings:
        print("  (none)")
    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        default = " [default]" if mapping.get("isDefault") in (True, "true") else ""
        print(f"  - {mapping.get('name')}{default} (id={mapping.get('contextMappingId')})")
        for node_map in mapping.get("contextNodeMappings") or []:
            if not isinstance(node_map, dict):
                continue
            sobj = node_map.get("sObjectName")
            print(
                f"      node={node_map.get('contextNodeName')}"
                + (f" -> {sobj}" if sobj else "")
            )
            for attr_map in node_map.get("attributeMappings") or []:
                if not isinstance(attr_map, dict):
                    continue
                hydration = attr_map.get("contextAttrHydrationDetailList") or []
                hy = ""
                if hydration:
                    parts = []
                    for h in hydration:
                        if not isinstance(h, dict):
                            continue
                        # Simple mappings omit objectName (it is the node's sObject);
                        # traversal mappings carry an explicit objectName per hop.
                        obj = h.get("objectName") or sobj or "?"
                        parts.append(f"{obj}.{h.get('queryAttribute')}")
                    hy = f"  <= {', '.join(parts)}"
                print(
                    f"          {attr_map.get('contextAttributeName')} "
                    f"(in={attr_map.get('contextInputAttributeName')}){hy}"
                )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Describe a Context Definition.")
    parser.add_argument(
        "--target-org",
        required=True,
        help="SF CLI alias or username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--developer-name", help="DeveloperName of the definition.")
    group.add_argument("--id", dest="context_id", help="ContextDefinitionId.")
    parser.add_argument(
        "--api-version", default="67.0", help="Salesforce API version (default 67.0)."
    )
    parser.add_argument("--json", action="store_true", help="Emit raw normalized JSON.")
    args = parser.parse_args(argv)

    try:
        context_id = args.context_id
        if not context_id:
            context_id = _resolve_id(
                args.developer_name, args.target_org, args.api_version
            )
            if not context_id:
                eprint(
                    f"Error: no context definition found with developerName "
                    f"'{args.developer_name}' in org '{args.target_org}'."
                )
                return 1
        defn = connect_get(
            f"connect/context-definitions/{context_id}", args.target_org, args.api_version
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if isinstance(defn, list):
        defn = defn[0] if defn and isinstance(defn[0], dict) else {}
    if not isinstance(defn, dict) or not defn:
        eprint("Error: empty or unexpected response for the context definition.")
        return 1

    if args.json:
        print(json.dumps(defn, indent=2))
        return 0

    _print_human(defn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
