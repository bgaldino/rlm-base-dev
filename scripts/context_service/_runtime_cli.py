#!/usr/bin/env python3
"""Shared argparse / IO helpers for the runtime Context Service CLI scripts.

Keeps ``create_context_instance.py``, ``query_context_instance.py``,
``persist_context_instance.py``, ``delete_context_instance.py`` and ``context_session.py``
consistent on the parts that must not drift: the request-scoped ``contextId``
warning, ``--data`` parsing (fail-fast → exit 2), and mapping resolution
(``--mapping-id`` direct, else ``--developer-name``/``--context-definition-id``
[+ ``--mapping-name``] → ``_resolve.resolve_mapping``).

Import-only; auth is delegated to the ``sf`` CLI via the modules it calls — no
access token is handled here.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ._client import eprint
from ._resolve import fetch_detail, resolve_definition_id, resolve_mapping

# One-line note printed by the standalone (non-session) scripts. A runtime
# contextId is a request-scoped cache handle and may not survive across separate
# `sf` invocations unless the org's Instance-Reuse setting is on.
CONTEXT_ID_SCOPE_NOTE = (
    "Note: a runtime contextId is request-scoped — per Salesforce docs it may not "
    "survive across separate CLI invocations unless the org's \"Runtime Context "
    "Instance Reuse to Improve Response Times\" setting is on (and within "
    "contextTtl). If a call fails not-found, use context_session.py, which does "
    "create→use→persist→delete in one process."
)

EXPERIMENTAL_BANNER = (
    "⚠️  EXPERIMENTAL / verify-live (262 / v67.0): runtime Context Service tooling "
    "is not build-critical and is not wired into any CCI flow."
)


def print_persist_outcome(outcome: dict) -> None:
    """Report an AsyncOperationTracker-confirmed persist outcome to stderr.

    Shared by ``context_session.py`` and ``persist_context_instance.py`` so both
    describe a persist result the same way. ``outcome`` is the dict returned by
    ``_runtime.summarize_persist_tracker``.
    """
    if not isinstance(outcome, dict):
        return
    if not outcome.get("found"):
        if outcome.get("timed_out"):
            eprint("persist outcome: tracker row not found within poll window "
                   "(confirm AsyncOperationTracker manually).")
        else:
            eprint("persist outcome: no tracker row (outcome unconfirmed).")
        return
    status = outcome.get("status")
    if outcome.get("is_failure"):
        eprint(f"persist outcome: FAILED (status={status})")
        errors = outcome.get("errors")
        if errors:
            eprint(f"  errorNodes: {json.dumps(errors, default=str)}")
        raw = outcome.get("raw_response")
        if not errors and isinstance(raw, str):
            eprint(f"  response: {raw}")
    elif outcome.get("timed_out"):
        eprint(f"persist outcome: still running (status={status}) — not confirmed.")
    else:
        saved = outcome.get("saved") or {}
        skipped = outcome.get("skipped") or []
        n_saved = len(saved) if hasattr(saved, "__len__") else saved
        n_skipped = len(skipped) if hasattr(skipped, "__len__") else skipped
        eprint(f"persist outcome: OK (status={status}, "
               f"savedNodes={n_saved}, skippedNodes={n_skipped}).")


def add_data_args(parser) -> None:
    """Add the mutually-exclusive record-payload input flags (create/session)."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--data-file", help="Path to a JSON records file (the "
                       "hydration payload; see build_hydration_data.py).")
    group.add_argument("--data", help="Inline JSON records, or '-' to read stdin.")


def add_mapping_source_args(parser, *, target_mapping: bool = False) -> None:
    """Add the flags that resolve a context mapping id.

    Direct id (``--mapping-id`` / ``--target-mapping-id``) wins; otherwise a
    definition source (``--developer-name`` / ``--context-definition-id``) plus an
    optional ``--mapping-name`` (default mapping when omitted).
    """
    if target_mapping:
        parser.add_argument("--target-mapping-id",
                            help="ContextMapping id to persist into (prefix 11j). "
                            "Direct — skips definition/name resolution.")
        parser.add_argument("--target-mapping-name",
                            help="Persist into the mapping with this name (resolved "
                            "against the definition; default mapping if omitted).")
    else:
        parser.add_argument("--mapping-id",
                            help="ContextMapping id to hydrate with (prefix 11j). "
                            "Direct — skips definition/name resolution.")
        parser.add_argument("--mapping-name",
                            help="Hydrate with the mapping of this name (resolved "
                            "against the definition; default mapping if omitted).")
    parser.add_argument("--developer-name",
                        help="DeveloperName of the definition (mapping/def source).")
    parser.add_argument("--context-definition-id",
                        help="ContextDefinitionId (prefix 11O; mapping/def source).")


def load_records(args) -> Any:
    """Parse ``--data-file`` / ``--data`` / ``--data -`` into a Python object.

    Fail-fast: a missing file or invalid JSON raises ``ValueError`` so the caller
    can ``eprint`` and return exit code 2 (config error). Returns ``None`` when no
    data flag was supplied (caller decides whether that is an error).
    """
    raw: Optional[str] = None
    if getattr(args, "data_file", None):
        path = Path(args.data_file)
        if not path.is_file():
            raise ValueError(f"--data-file not found: {path}")
        raw = path.read_text(encoding="utf-8")
    elif getattr(args, "data", None) is not None:
        raw = sys.stdin.read() if args.data == "-" else args.data
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"--data is not valid JSON: {exc}") from exc


def resolve_mapping_id(
    args,
    *,
    target_org: str,
    api_version: str,
    target: bool = False,
    detail: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve ``(context_definition_id, mapping_id)`` from the CLI mapping flags.

    With a direct ``--mapping-id``/``--target-mapping-id`` the mapping is taken
    verbatim; the definition id is still resolved from ``--context-definition-id``
    or ``--developer-name`` when either is supplied (so create/session get a
    ``contextDefinitionId`` for the create body), and is ``None`` only when no
    definition source was given at all. Without a direct id, resolves the
    definition and selects the mapping (named or default). Raises ``ValueError``
    (→ exit 2) when the definition/mapping can't be resolved; ``ContextClientError``
    bubbles for the caller to turn into exit 1.

    ``detail`` — a pre-fetched definition detail (from ``_resolve.fetch_detail``).
    When supplied, the named/default resolution path skips the internal
    ``resolve_definition_id`` + ``fetch_detail`` round-trips and selects the
    mapping straight off it. ``context_session.py`` uses this to fetch the detail
    once and reuse it for both the source (hydrate) and target (persist) mapping
    so the two never resolve against different snapshots. Ignored on the direct
    ``--mapping-id`` path (no detail is needed there).
    """
    context_definition_id = getattr(args, "context_definition_id", None)
    developer_name = getattr(args, "developer_name", None)

    direct = getattr(args, "target_mapping_id" if target else "mapping_id", None)
    if direct:
        # A direct mapping id skips mapping resolution, but a definition source
        # may still be supplied (create/session need a contextDefinitionId in the
        # create body). Resolve it when present so callers don't reject a valid
        # `--mapping-id 11j... --developer-name Foo` invocation; return None only
        # when no definition source was given at all.
        if context_definition_id:
            return context_definition_id, direct
        if developer_name:
            resolved = resolve_definition_id(
                developer_name, target_org=target_org, api_version=api_version
            )
            if not resolved:
                raise ValueError(
                    f"No context definition found with developerName '{developer_name}' "
                    f"in org '{target_org}'."
                )
            return resolved, direct
        return None, direct

    mapping_name = getattr(args, "target_mapping_name" if target else "mapping_name", None)

    # A caller-supplied detail short-circuits the resolve+fetch (see docstring):
    # select the mapping straight off the shared snapshot. resolve_mapping reads
    # the contextDefinitionId back out of the detail.
    if detail is not None:
        if not detail:
            raise ValueError("Supplied definition detail is empty.")
        return resolve_mapping(detail, mapping_name)

    if not context_definition_id:
        if not developer_name:
            raise ValueError(
                "Provide a mapping id directly, or a --developer-name / "
                "--context-definition-id (with an optional mapping name) to resolve one."
            )
        context_definition_id = resolve_definition_id(
            developer_name, target_org=target_org, api_version=api_version
        )
        if not context_definition_id:
            raise ValueError(
                f"No context definition found with developerName '{developer_name}' "
                f"in org '{target_org}'."
            )

    detail = fetch_detail(
        context_definition_id, target_org=target_org, api_version=api_version
    )
    if not detail:
        raise ValueError(
            f"Empty detail for context definition '{context_definition_id}'."
        )
    return resolve_mapping(detail, mapping_name)
