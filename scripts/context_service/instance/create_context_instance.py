#!/usr/bin/env python3
"""Create (hydrate) a runtime Context Service instance (EXPERIMENTAL).

``POST /connect/contexts`` — hydrate a context **instance** from a records
payload and a context mapping, returning the runtime **Context Info**
(``contextId``, ``contextDefinitionId``, ``contextMappingId``,
``childBusinessObjectTypes``, ``isSuccess``).

⚠️  **EXPERIMENTAL / verify-live (262 / v67.0).** Not build-critical, not wired
into any CCI flow. Auth is delegated to the ``sf`` CLI — no access token is
handled. ``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), never
the CCI alias.

The returned ``contextId`` is a request-scoped cache handle and may not survive
across separate CLI invocations (see the note this prints). For an end-to-end
round trip in one process, prefer ``context_session.py``.

Data payload: the nested ``data`` object keyed by node / ``businessObjectType``
name (build it with ``build_hydration_data.py``). Supplied via ``--data-file`` /
``--data '<json>'`` / ``--data -`` (stdin) — parsed and validated before the call.

Mapping: ``--mapping-id`` directly, else ``--developer-name`` /
``--context-definition-id`` [+ ``--mapping-name``] resolves the default (or named)
mapping.

Usage:
    # resolve the default mapping by name, hydrate from a file, capture the id
    CID=$(python scripts/context_service/create_context_instance.py \
        --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext \
        --data-file /tmp/records.json --id-only)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._runtime import RuntimeContextClient  # noqa: E402
from scripts.context_service._runtime_cli import (  # noqa: E402
    CONTEXT_ID_SCOPE_NOTE,
    EXPERIMENTAL_BANNER,
    add_data_args,
    add_mapping_source_args,
    load_records,
    resolve_mapping_id,
)


def _print_human(info: dict) -> None:
    print("Context Info:")
    print(f"  contextId:            {info.get('contextId')}")
    print(f"  contextDefinitionId:  {info.get('contextDefinitionId')}")
    print(f"  contextMappingId:     {info.get('contextMappingId')}")
    print(f"  isSuccess:            {info.get('isSuccess')}")
    children = info.get("childBusinessObjectTypes")
    if children:
        print(f"  childBusinessObjectTypes: {', '.join(children)}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create (hydrate) a runtime Context Service instance (EXPERIMENTAL)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    add_mapping_source_args(parser)
    add_data_args(parser)
    parser.add_argument("--tagged-data", choices=["true", "false"],
                        help="Set the metadata.taggedData flag (omitted when unset; verify live).")
    parser.add_argument("--context-scope", choices=["REQUEST", "SESSION"],
                        help="Set metadata.contextScope on create. SESSION lets "
                             "the contextId survive "
                             "across separate CLI calls (subject to contextTtl). "
                             "Requires the ContextServicePilot permission. Default "
                             "(omitted) is REQUEST (request-local, ~15 s).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log the intended create call without mutating the org.")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true",
                        help="Emit the full Context Info dict as JSON (stdout).")
    output.add_argument("--id-only", action="store_true",
                        help="Emit just the bare contextId (stdout), for $(...) capture.")
    args = parser.parse_args(argv)

    eprint(EXPERIMENTAL_BANNER)

    # 1. Parse the records payload (fail fast → exit 2).
    try:
        records = load_records(args)
    except ValueError as exc:
        eprint(f"Error: {exc}")
        return 2
    if records is None:
        eprint("Error: no records supplied. Pass --data-file, --data '<json>', or --data -.")
        return 2

    # 2. Resolve the source mapping.
    try:
        _def_id, mapping_id = resolve_mapping_id(
            args, target_org=args.target_org, api_version=args.api_version
        )
        context_definition_id = args.context_definition_id or _def_id
        if not context_definition_id:
            # Direct --mapping-id given without a definition id: the create body
            # needs a contextDefinitionId, so require the def source too.
            eprint("Error: --mapping-id also requires --context-definition-id "
                   "(or --developer-name) so the create body can carry a "
                   "contextDefinitionId.")
            return 2
    except ValueError as exc:
        eprint(f"Error: {exc}")
        return 2
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    tagged_data = None
    if args.tagged_data is not None:
        tagged_data = args.tagged_data == "true"

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=args.dry_run, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)

    try:
        info = client.create_instance(
            context_definition_id=context_definition_id,
            mapping_id=mapping_id,
            data=records,
            tagged_data=tagged_data,
            context_scope=getattr(args, "context_scope", None),
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    eprint(CONTEXT_ID_SCOPE_NOTE)

    if args.dry_run:
        eprint("[dry-run] create only logged — no contextId minted.")
        return 0

    info = info if isinstance(info, dict) else {}
    # A create can return isSuccess:false (or hydrate zero records with a
    # contextId) — surface it and exit non-zero rather than emit a contextId that
    # points at a failed/empty instance.
    create_failed = info.get("isSuccess") is False
    if create_failed:
        eprint("Error: create returned isSuccess:false — the instance was not "
               f"hydrated. Response: {json.dumps(info)}")
    if args.id_only:
        context_id = info.get("contextId") or info.get("id") or ""
        if create_failed:
            return 1
        print(context_id)
        return 0 if context_id else 1
    if args.json:
        print(json.dumps(info, indent=2))
        return 1 if create_failed else 0
    _print_human(info)
    return 1 if create_failed else 0


if __name__ == "__main__":
    sys.exit(main())
