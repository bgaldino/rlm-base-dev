#!/usr/bin/env python3
"""Persist a runtime Context Service instance back to SObjects (EXPERIMENTAL).

``POST /connect/contexts/persist-records`` — write the (possibly updated)
attribute values of a hydrated context **instance** back to the SObjects of a
**target** context mapping. Returns a ``referenceId`` (maps to a
``ContextPersistenceEvent``).

⚠️  **EXPERIMENTAL / verify-live (262 / v67.0).** Not build-critical, not wired
into any CCI flow. Auth is delegated to the ``sf`` CLI — no access token is
handled. ``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), never the
CCI alias.

⚠️  **FK caveat.** Per the persistence reference, reference/lookup foreign-key
changes are **not reliably saved** by persist — scalar field updates are the
supported path. This is emitted to stderr on every run.

The ``contextId`` is request-scoped (see the note this prints) — persisting an id
minted by a separate call only works with the org's Instance-Reuse setting on and
within contextTtl; otherwise use ``context_session.py``.

Target mapping: ``--target-mapping-id`` directly, else ``--developer-name`` /
``--context-definition-id`` [+ ``--target-mapping-name``] resolves it (default
mapping when the name is omitted).

Usage:
    python scripts/context_service/persist_context_instance.py --target-org rlm-base__beta \
        --context-id <uuid> --target-mapping-id 11j...
    python scripts/context_service/persist_context_instance.py --target-org rlm-base__beta \
        --context-id <uuid> --developer-name RLM_SalesTransactionContext \
        --target-mapping-name QuoteEntitiesMapping
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
    add_mapping_source_args,
    print_persist_outcome,
    resolve_mapping_id,
)

FK_CAVEAT = (
    "Persist caveat: reference/lookup foreign-key changes are not reliably saved "
    "by persist-records — only scalar field updates are the supported path. "
    "Confirm FK writes directly on the target SObject."
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Persist a runtime Context Service instance to SObjects (EXPERIMENTAL)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    parser.add_argument("--context-id", required=True,
                        help="Runtime contextId (opaque request-scoped handle).")
    add_mapping_source_args(parser, target_mapping=True)
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log the intended persist call without mutating the org.")
    parser.add_argument("--json", action="store_true",
                        help="Emit the raw persist response as JSON.")
    parser.add_argument("--no-confirm", action="store_true",
                        help="Skip the AsyncOperationTracker poll (do not wait for "
                             "the async persist outcome; report only the referenceId).")
    parser.add_argument("--poll-seconds", type=float, default=30.0,
                        help="Max seconds to poll AsyncOperationTracker for the "
                             "persist outcome (default 30).")
    args = parser.parse_args(argv)

    eprint(EXPERIMENTAL_BANNER)
    eprint(CONTEXT_ID_SCOPE_NOTE)
    eprint(FK_CAVEAT)

    try:
        _def_id, target_mapping_id = resolve_mapping_id(
            args, target_org=args.target_org, api_version=args.api_version, target=True
        )
    except ValueError as exc:
        eprint(f"Error: {exc}")
        return 2
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=args.dry_run, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)

    try:
        result = client.persist_records(
            context_id=args.context_id, target_mapping_id=target_mapping_id
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.dry_run:
        eprint("[dry-run] persist only logged — nothing written.")
        return 0

    result = result if isinstance(result, dict) else {}
    reference_id = result.get("referenceId") or result.get("id")

    # persist-records is async: the referenceId is an AsyncOperationTracker Id,
    # not a success signal. Poll it for the real outcome unless --no-confirm.
    outcome = None
    if reference_id and not args.no_confirm:
        try:
            outcome = client.confirm_persist(
                reference_id, poll_seconds=args.poll_seconds
            )
        except ContextClientError as exc:
            eprint(f"Warning: could not confirm persist outcome: {exc}")

    if args.json:
        payload = {"persist": result}
        if outcome is not None:
            payload["persist_outcome"] = outcome
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(f"referenceId: {reference_id}" if reference_id
              else json.dumps(result, indent=2))
        if outcome is not None:
            print_persist_outcome(outcome)
        elif reference_id and args.no_confirm:
            eprint("persist outcome: not confirmed (--no-confirm); check "
                   f"AsyncOperationTracker Id={reference_id}.")

    if isinstance(outcome, dict) and outcome.get("is_failure"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
