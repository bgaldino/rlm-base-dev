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
from typing import Any, Optional, Tuple

from _resolve import fetch_detail, resolve_definition_id, resolve_mapping

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
    args, *, target_org: str, api_version: str, target: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve ``(context_definition_id, mapping_id)`` from the CLI mapping flags.

    Returns the direct id (with a ``None`` definition id) when
    ``--mapping-id``/``--target-mapping-id`` is given; otherwise resolves the
    definition and selects the mapping (named or default). Raises ``ValueError``
    (→ exit 2) when the mapping can't be resolved; ``ContextClientError`` bubbles
    for the caller to turn into exit 1.
    """
    direct = getattr(args, "target_mapping_id" if target else "mapping_id", None)
    if direct:
        return None, direct

    mapping_name = getattr(args, "target_mapping_name" if target else "mapping_name", None)
    context_definition_id = getattr(args, "context_definition_id", None)
    developer_name = getattr(args, "developer_name", None)

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
