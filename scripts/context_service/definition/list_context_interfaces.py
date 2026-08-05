#!/usr/bin/env python3
"""List Context Definition Interfaces in an org (read-only).

``GET /connect/context-definition-interfaces`` lists the definition interfaces
(the abstract contracts that context definitions can implement, used by engines
to discover a compatible definition); ``--interface NAME`` GETs one by name.
Interfaces are not tied to a specific definition, so no ``--developer-name`` is
required — that is why this is a separate script from ``describe_context.py``
(which requires a definition selector).

Read-only. Auth is delegated to the ``sf`` CLI — no access token is handled.
``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), never the CCI
alias. Pinned to Release 262 / v67.0 (resource added in 62.0) — verify-live.

Usage:
    python scripts/context_service/definition/list_context_interfaces.py --target-org rlm-base__beta
    python scripts/context_service/definition/list_context_interfaces.py --target-org rlm-base__beta \
        --interface <name> --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._runtime import RuntimeContextClient  # noqa: E402


def _rows(response):
    """Normalize the list response into a list of interface dicts.

    The live v67.0 list shape is a wrapper dict keyed
    ``contextDefinitionInterfaceMetadataList`` (each row carrying
    ``interfaceName``/``developerName``); older/alternate keys are tolerated.
    The by-name GET wraps the row under the singular
    ``contextDefinitionInterfaceMetadata`` (alongside a node-tag tree).
    """
    if isinstance(response, list):
        return [r for r in response if isinstance(r, dict)]
    if isinstance(response, dict):
        for key in (
            "contextDefinitionInterfaceMetadataList",
            "contextDefinitionInterfaces",
            "interfaces",
            "records",
        ):
            value = response.get(key)
            if isinstance(value, list):
                return [r for r in value if isinstance(r, dict)]
        # Single-interface GET: the row is nested under the singular key.
        single = response.get("contextDefinitionInterfaceMetadata")
        if isinstance(single, dict):
            return [single]
        # A bare single-interface row — wrap it, but only if it looks like an
        # interface row (has a name), not a list-wrapper envelope whose list key
        # we simply didn't recognize (avoids emitting a bogus "?" row).
        if any(k in response for k in ("interfaceName", "developerName", "name")):
            return [response]
    return []


def _count_interface_tags(response):
    """(node_tag_count, attr_tag_count) from a by-name interface's node-tag tree.

    Returns ``None`` when the response carries no node-tag list (e.g. the list
    endpoint). Recursively walks ``childNodeTags`` so nested nodes are counted.
    """
    if not isinstance(response, dict):
        return None
    tree = response.get("contextDefinitionInterfaceNodeTagList")
    if not isinstance(tree, list):
        return None
    nodes = attrs = 0

    def walk(node_tags):
        nonlocal nodes, attrs
        for nt in node_tags or []:
            if not isinstance(nt, dict):
                continue
            nodes += 1
            attrs += len([a for a in (nt.get("attributeTags") or [])
                          if isinstance(a, dict)])
            walk(nt.get("childNodeTags"))

    walk(tree)
    return nodes, attrs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="List Context Definition Interfaces in an org (read-only)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    parser.add_argument("--interface", metavar="NAME",
                        help="GET one interface by name (else list all).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the raw response as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=False, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)

    try:
        if args.interface:
            response = client.get_definition_interface(args.interface)
        else:
            response = client.list_definition_interfaces()
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(response, indent=2))
        return 0

    rows = _rows(response)
    if not rows:
        print("No context definition interfaces returned.")
        return 0
    for row in rows:
        name = (row.get("developerName") or row.get("interfaceName")
                or row.get("name") or "?")
        label = (row.get("masterLabel") or row.get("label")
                 or row.get("description"))
        version = row.get("version")
        suffix = ""
        if label:
            suffix += f"  ({label})"
        if version:
            suffix += f"  [v{version}]"
        print(f"- {name}{suffix}")

    # A by-name GET also carries the interface's node/attribute tag contract.
    tag_counts = _count_interface_tags(response)
    if tag_counts is not None:
        nodes, attrs = tag_counts
        print(f"    node tags: {nodes}, attribute tags: {attrs} "
              f"(use --json for the full tag tree)")

    print(f"\n{len(rows)} interface(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
