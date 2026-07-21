#!/usr/bin/env python3
"""Run a full runtime Context Service lifecycle in one process (EXPERIMENTAL).

**Primary CLI entry point** for exercising the runtime half of Context Service.
It sequences the lifecycle from one Python process:

    create (or reuse --context-id)
      → update-attributes  (--update-attr, repeatable)
      → write-through-tags (--write-tag, repeatable)
      → query-record       (--query)
      → persist-records    (--persist)
      → delete/evict        (unless --keep or reusing --context-id)

⚠️  This does **not** work around contextId scoping. Each step above is a
separate ``sf api request``, so a runtime ``contextId`` created with the default
REQUEST scope will not survive to the query/persist steps. To chain create →
use → persist across those calls you must pass ``--context-scope SESSION``
(pilot-gated; needs the org's "Runtime Context Instance Reuse" setting, within
contextTtl) or reuse an existing instance via ``--context-id``. For a GA
single-request lifecycle, drive it from Apex (``Context.IndustriesContext``) or a
single Flow instead.

⚠️  **EXPERIMENTAL / verify-live (262 / v67.0).** Not build-critical, not wired
into any CCI flow. Auth is delegated to the ``sf`` CLI — no access token is
handled. ``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), never the
CCI alias.

Dry-run contract: mutations (create/update/write/persist/delete) only log; the
read step (query-record) still executes when it has a real ``contextId``. Under
``--dry-run`` create is not performed, so there is no ``contextId`` and the
dependent steps are skipped with a log line (unless you pass ``--context-id``).

NODEPATH arguments (``--update-attr`` / ``--write-tag``) are a dot-joined path
of **record IDs** from root to target (e.g. ``0Q0...quoteId`` for a root record,
``0Q0...quoteId.0QL...lineId`` for a child). Use ``-`` or ``""`` for the root
node when no specific record targeting is needed (silently returns success but
does not mutate the value — node-name paths behave identically).

Usage:
    # SESSION scope on a pilot org: full multi-call lifecycle
    python scripts/context_service/instance/context_session.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --context-scope SESSION \
        --data-file /tmp/records.json --query --persist \
        --target-mapping-name QuoteEntitiesMapping

    # hydrate from a file, query the result, persist to the same mapping.
    # --context-scope SESSION is REQUIRED whenever query/persist follow create:
    # each step is a separate `sf api request`, and a REQUEST-scoped contextId
    # (the default) does not survive across CLI calls (see the note above), so
    # the downstream query/persist would fail without it.
    python scripts/context_service/instance/context_session.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --data-file /tmp/records.json \
        --context-scope SESSION --query --persist --target-mapping-name QuoteEntitiesMapping

    # operate on an existing (reuse-enabled) instance: set an attr, then query
    python scripts/context_service/instance/context_session.py --target-org rlm-base__beta \
        --context-id <uuid> --update-attr SalesTransactionItem RampMode__c RAMP --query
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._resolve import fetch_detail, resolve_definition_id  # noqa: E402
from scripts.context_service._runtime import RuntimeContextClient, RuntimeSession  # noqa: E402
from scripts.context_service._runtime_cli import (  # noqa: E402
    CONTEXT_ID_SCOPE_NOTE,
    EXPERIMENTAL_BANNER,
    add_data_args,
    add_mapping_source_args,
    load_records,
    print_persist_outcome,
    resolve_mapping_id,
)


def _parse_data_path(nodepath: str):
    """A dot-joined NODEPATH → a dataPath list ('' or '-' → root, i.e. [])."""
    if nodepath in ("", "-"):
        return []
    return nodepath.split(".")


def _group_by_path(triples, value_keys):
    """Group repeatable (nodepath, name, value) triples into per-dataPath entries.

    ``value_keys`` = ("attributeName", "attributeValue") for attrs, or
    ("tagName", "tagValue") for tags; the list key is chosen by the caller.
    """
    grouped = {}
    order = []
    for nodepath, name, value in triples or []:
        key = nodepath
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append({value_keys[0]: name, value_keys[1]: value})
    return order, grouped


def _build_attribute_updates(update_attrs):
    order, grouped = _group_by_path(update_attrs, ("attributeName", "attributeValue"))
    return [{"dataPath": _parse_data_path(p), "attributes": grouped[p]} for p in order]


def _build_tag_writes(write_tags):
    order, grouped = _group_by_path(write_tags, ("tagName", "tagValue"))
    return [{"dataPath": _parse_data_path(p), "tagValues": grouped[p]} for p in order]


def _fetch_shared_detail(args):
    """Resolve the definition id and GET its detail **once**, for reuse across
    both the source (hydrate) and target (persist) mapping resolution.

    Fetching here and passing the result to both ``resolve_mapping_id`` calls
    collapses up to four GETs (a resolve + fetch per call) into one and
    guarantees source and target resolve against the **same** definition
    snapshot. Returns ``None`` when no definition source was supplied — the
    direct ``--mapping-id`` path needs no detail, and any genuinely missing
    source is reported by ``resolve_mapping_id`` with its actionable message.
    Raises ``ValueError`` on an unresolvable definition (→ exit 2);
    ``ContextClientError`` bubbles (→ exit 1).
    """
    context_definition_id = args.context_definition_id
    if not context_definition_id:
        if not args.developer_name:
            return None
        context_definition_id = resolve_definition_id(
            args.developer_name, target_org=args.target_org, api_version=args.api_version
        )
        if not context_definition_id:
            raise ValueError(
                f"No context definition found with developerName '{args.developer_name}' "
                f"in org '{args.target_org}'."
            )
    detail = fetch_detail(
        context_definition_id, target_org=args.target_org, api_version=args.api_version
    )
    if not detail:
        raise ValueError(
            f"Empty detail for context definition '{context_definition_id}'."
        )
    return detail


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a full runtime Context Service lifecycle in one process "
                    "(EXPERIMENTAL)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    # Create source (mapping + records) OR reuse an existing instance.
    add_mapping_source_args(parser)
    add_data_args(parser)
    parser.add_argument("--tagged-data", choices=["true", "false"],
                        help="Set metadata.taggedData on create (omitted when unset).")
    parser.add_argument("--context-scope", choices=["REQUEST", "SESSION"],
                        help="Set metadata.contextScope on create. SESSION lets "
                             "the contextId survive "
                             "across separate CLI calls (subject to contextTtl). "
                             "Requires the ContextServicePilot permission. Default "
                             "(omitted) is REQUEST (request-local, ~15 s).")
    parser.add_argument("--context-id",
                        help="Operate on an existing instance (skip create; also skips "
                             "the auto-delete at the end).")
    # Mutations during the session.
    parser.add_argument("--update-attr", nargs=3, action="append",
                        metavar=("NODEPATH", "NAME", "VALUE"),
                        help="Set an attribute (repeatable). NODEPATH is dot-joined "
                             "record IDs ('-' for root). Only record-ID paths "
                             "actually mutate values; node names silently no-op.")
    parser.add_argument("--write-tag", nargs=3, action="append",
                        metavar=("NODEPATH", "TAG", "VALUE"),
                        help="Write a tag value (repeatable). NODEPATH is dot-joined "
                             "('-' for root).")
    # Reads / persist.
    parser.add_argument("--query", action="store_true",
                        help="query-record the instance and include it in the summary.")
    parser.add_argument("--no-children", action="store_true",
                        help="query-record with children=false.")
    parser.add_argument("--persist", action="store_true",
                        help="persist-records to a target mapping (needs --target-mapping-id "
                             "or --target-mapping-name).")
    parser.add_argument("--target-mapping-id",
                        help="Target ContextMapping id for --persist (prefix 11j).")
    parser.add_argument("--target-mapping-name",
                        help="Target mapping name for --persist (resolved against the "
                             "definition; default mapping if omitted).")
    parser.add_argument("--no-confirm-persist", action="store_true",
                        help="Skip the AsyncOperationTracker poll after --persist "
                             "(report only the referenceId; do not wait for the "
                             "async outcome).")
    parser.add_argument("--persist-poll-seconds", type=float, default=30.0,
                        help="Max seconds to poll AsyncOperationTracker for the "
                             "persist outcome (default 30).")
    parser.add_argument("--keep", action="store_true",
                        help="Do not evict the created instance at the end.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log intended mutations; run only reads (per the dry-run contract).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the full session summary as JSON.")
    args = parser.parse_args(argv)

    eprint(EXPERIMENTAL_BANNER)
    eprint(CONTEXT_ID_SCOPE_NOTE)

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=args.dry_run, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)
    session = RuntimeSession(client, logger=eprint)

    # Fetch the definition detail ONCE and reuse it for both the source (hydrate)
    # and target (persist) mapping resolution — otherwise each resolve_mapping_id
    # call re-resolves the id and re-GETs the detail (up to 4 GETs on
    # --developer-name --persist), and source/target could resolve against
    # different snapshots. Only needed when at least one side resolves by
    # name/default (a direct --mapping-id / --target-mapping-id needs no detail);
    # None otherwise leaves resolve_mapping_id to fetch as before.
    shared_detail = None
    need_source = (not args.context_id) and not args.mapping_id
    need_target = args.persist and not args.target_mapping_id
    if need_source or need_target:
        try:
            shared_detail = _fetch_shared_detail(args)
        except ValueError as exc:
            eprint(f"Error: {exc}")
            return 2
        except ContextClientError as exc:
            eprint(f"Error: {exc}")
            return 1

    # Build the create spec unless reusing an existing instance.
    create_spec = None
    if not args.context_id:
        try:
            records = load_records(args)
        except ValueError as exc:
            eprint(f"Error: {exc}")
            return 2
        if records is None:
            eprint("Error: no records supplied and no --context-id. Pass "
                   "--data-file / --data, or --context-id to reuse an instance.")
            return 2
        try:
            _def_id, mapping_id = resolve_mapping_id(
                args, target_org=args.target_org, api_version=args.api_version,
                detail=shared_detail,
            )
            context_definition_id = args.context_definition_id or _def_id
            if not context_definition_id:
                eprint("Error: --mapping-id also requires --context-definition-id "
                       "(or --developer-name) for the create body.")
                return 2
        except ValueError as exc:
            eprint(f"Error: {exc}")
            return 2
        except ContextClientError as exc:
            eprint(f"Error: {exc}")
            return 1
        tagged_data = None if args.tagged_data is None else (args.tagged_data == "true")
        create_spec = {
            "context_definition_id": context_definition_id,
            "mapping_id": mapping_id,
            "data": records,
            "tagged_data": tagged_data,
            "context_scope": args.context_scope,
        }

    # Resolve the persist target mapping up front (so a bad name fails before create).
    persist_target_mapping_id = None
    if args.persist:
        try:
            _def_id, persist_target_mapping_id = resolve_mapping_id(
                args, target_org=args.target_org, api_version=args.api_version,
                target=True, detail=shared_detail,
            )
        except ValueError as exc:
            eprint(f"Error: {exc}")
            return 2
        except ContextClientError as exc:
            eprint(f"Error: {exc}")
            return 1

    query_spec = {"children": not args.no_children} if args.query else None

    try:
        summary = session.run(
            create_spec=create_spec,
            existing_context_id=args.context_id,
            attribute_updates=_build_attribute_updates(args.update_attr),
            tag_writes=_build_tag_writes(args.write_tag),
            do_query=args.query,
            query_spec=query_spec,
            persist_target_mapping_id=persist_target_mapping_id,
            confirm_persist=not args.no_confirm_persist,
            persist_poll_seconds=args.persist_poll_seconds,
            keep_instance=args.keep,
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    else:
        eprint(
            f"Session: created={summary.get('created')} "
            f"context_id={summary.get('context_id')} "
            f"deleted={summary.get('deleted')}"
            + (" [dry-run]" if summary.get("dry_run") else "")
        )
        if summary.get("query") is not None:
            print(json.dumps(summary["query"], indent=2))
        if summary.get("persist") is not None:
            persist = summary["persist"] or {}
            ref = persist.get("referenceId") if isinstance(persist, dict) else None
            eprint(f"persist referenceId: {ref}" if ref else f"persist: {persist}")
            outcome = summary.get("persist_outcome")
            if isinstance(outcome, dict):
                print_persist_outcome(outcome)
    # A confirmed persist failure is a non-zero exit — the tool exists to catch
    # exactly this, so it must not report success on a dirty persist.
    outcome = summary.get("persist_outcome")
    if isinstance(outcome, dict) and outcome.get("is_failure"):
        return 1
    if summary.get("create_failed"):
        return 1
    # Any semantic (isSuccess:false) failure on update/tag/query/persist, or a
    # live persist that returned no referenceId, is a non-zero exit (F4).
    failures = summary.get("semantic_failures")
    if failures:
        for f in failures:
            eprint(f"Semantic failure in {f.get('step')}: {f.get('message')}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
