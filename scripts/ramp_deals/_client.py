#!/usr/bin/env python3
"""Shared ``sf``-CLI transport for the ramp-deals scripts (read *and* mutate).

Mirrors ``scripts/expression_sets/_client.py``: auth is delegated entirely to the
``sf`` CLI — this module never handles access tokens. Every request goes through
``sf api request rest '<path>' -X <METHOD> [-b -] --target-org <alias>``, which
authenticates with the CLI's stored credentials. ``--target-org`` is always the
*SF CLI* alias/username (e.g. ``rlm-base__sdb39``), NEVER the CCI alias.

NOTE ON THE OPEN RESEARCH QUESTION: this transport is how *our* scripts reach the
org. It is unrelated to research briefing Q6 (how a Salesforce-side agent reaches a
custom MCP server). This layer is not blocked — an operator running these CLIs is
authenticated through the CLI exactly as the expression_sets toolkit is.

The ramp Connect ops are ``connect/rev/sales-transaction/actions/place`` and
``…/actions/clone`` (see ``_payload.PLACE_PATH`` / ``CLONE_PATH`` for the
version-pinned full paths). Bodies are piped on **stdin** via ``-b -`` — no temp
files, no shell-quoting. Pure body/graph logic lives in ``_payload``; this module
is transport only.

The :class:`Transport` class is the injectable seam the lifecycle engine and the
verb CLIs take, so both can be unit-tested with a fake transport (no org): any
object exposing ``connect`` / ``sobject`` / ``soql`` with these signatures works.
"""

import json
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

from . import API_VERSION  # "v68.0"

# Bare numeric form ("68.0") for building /services/data/v<version>/ paths.
DEFAULT_API_VERSION = API_VERSION.lstrip("v")

_REQUEST_TIMEOUT = 120  # seconds — reads
# A `place` that triggers pricing + tax + (large-deal) preprocessing can take
# minutes server-side; give mutations a generous ceiling.
_MUTATION_TIMEOUT = 600  # seconds

_SERVICES_PREFIX = "/services/data/"


class RampClientError(RuntimeError):
    """Raised when a CLI call fails in a way the caller should surface.

    Carries the parsed Salesforce ``error_codes`` (e.g. ``["FIELD_INTEGRITY_
    EXCEPTION"]``) and the raw response ``body`` so callers can branch on them.
    """

    def __init__(self, message: str, *, error_codes: Optional[List[str]] = None,
                 body: str = "", returncode: Optional[int] = None):
        super().__init__(message)
        self.error_codes = error_codes or []
        self.body = body
        self.returncode = returncode

    def has_error_code(self, code: str) -> bool:
        return code in self.error_codes


def eprint(*args, **kwargs):
    """Print to stderr (so --json stdout stays clean)."""
    print(*args, file=sys.stderr, **kwargs)


def _extract_error_codes(text: str) -> List[str]:
    """Pull Salesforce ``errorCode`` values from a CLI error payload."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return []
    if isinstance(data, list):
        return [d["errorCode"] for d in data if isinstance(d, dict) and d.get("errorCode")]
    if isinstance(data, dict) and data.get("errorCode"):
        return [data["errorCode"]]
    return []


def _run_sf(
    args: List[str], *, input_text: Optional[str] = None, timeout: int = _REQUEST_TIMEOUT
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["sf", *args],
            capture_output=True,
            text=True,
            input=input_text,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise RampClientError(
            "The 'sf' CLI was not found on PATH. Install the Salesforce CLI and "
            "authenticate to your org (`sf org login web --alias <alias>`)."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RampClientError(
            f"'sf {' '.join(args)}' timed out after {timeout}s."
        ) from exc


def _full_path(path: str, api_version: str) -> str:
    """Normalize a path to a versioned ``/services/data/v<version>/…`` absolute path.

    Accepts either an already-versioned absolute path (``_payload.PLACE_PATH``) or
    a version-relative Connect/REST path (``connect/rev/…``, ``query?q=…``). ``sf
    api request rest`` 404s on a bare ``connect/…`` path, so the prefix is always
    ensured.
    """
    if path.startswith(_SERVICES_PREFIX):
        return path
    return f"{_SERVICES_PREFIX}v{api_version}/{path.lstrip('/')}"


def connect_request(
    method: str,
    path: str,
    body: Any = None,
    *,
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
    dry_run: bool = False,
    logger: Callable[..., None] = None,
    timeout: Optional[int] = None,
) -> Any:
    """Make an authenticated Salesforce REST/Connect request via the sf CLI.

    ``path`` is either version-relative (``connect/rev/sales-transaction/actions/
    place``, ``query?q=…``) or an already-versioned absolute path. ``body`` (a
    dict/list) is JSON-serialized and piped on stdin via ``-b -``.

    When ``dry_run`` is set, **mutating** verbs (anything other than GET/HEAD) are
    logged and skipped (returning ``{}``); **reads always execute** so an
    orchestrator can still resolve ids and log the real mutation sequence.

    Returns parsed JSON (``{}`` for an empty/204 response). Raises
    :class:`RampClientError` on a non-zero CLI exit.
    """
    log = logger or eprint
    method = method.upper()
    full_path = _full_path(path, api_version)

    if dry_run and method not in ("GET", "HEAD"):
        raw = json.dumps(body) if body is not None else ""
        preview = raw if len(raw) <= 300 else f"<{len(raw)} bytes>"
        log(f"[dry-run] {method} {full_path} {preview}")
        return {}

    args = ["api", "request", "rest", full_path, "-X", method, "--target-org", target_org]
    input_text: Optional[str] = None
    if body is not None:
        args += ["-b", "-"]
        input_text = json.dumps(body)
    elif method not in ("GET", "HEAD"):
        # `sf api request rest` rejects a bodiless mutating verb; empty stdin satisfies it.
        args += ["-b", "-"]
        input_text = ""

    if timeout is None:
        timeout = _REQUEST_TIMEOUT if method in ("GET", "HEAD") else _MUTATION_TIMEOUT

    result = _run_sf(args, input_text=input_text, timeout=timeout)
    stdout = (result.stdout or "").strip()
    if result.returncode != 0:
        error_codes = _extract_error_codes(stdout)
        detail = stdout or (result.stderr or "").strip()
        code_note = f" [{', '.join(error_codes)}]" if error_codes else ""
        raise RampClientError(
            f"sf api request {method} '{path}' failed for org '{target_org}'"
            f"{code_note}:\n{detail}\n\n"
            f"Confirm the SF CLI alias is correct (this is the *sf* alias, e.g. "
            f"'rlm-base__sdb39', not the CCI alias) and that you are authenticated "
            f"(`sf org login web --alias {target_org}`).",
            error_codes=error_codes,
            body=stdout,
            returncode=result.returncode,
        )
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RampClientError(
            f"Could not parse JSON from 'sf api request rest {method} {path}': {exc}\n"
            f"Raw output (truncated): {stdout[:400]}"
        ) from exc


def soql_literal(value: Any) -> str:
    """Escape a value for safe interpolation inside a single-quoted SOQL literal."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def soql_query(
    soql: str, *, target_org: str, api_version: str = DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """Run a SOQL query and return its ``records`` list, following ``nextRecordsUrl``."""
    resp = connect_request(
        "GET", f"query?q={quote(soql)}", None,
        target_org=target_org, api_version=api_version,
    )
    records: List[Dict[str, Any]] = []
    if isinstance(resp, dict):
        records.extend(r for r in resp.get("records", []) if isinstance(r, dict))
        while not resp.get("done", True) and resp.get("nextRecordsUrl"):
            nurl = resp["nextRecordsUrl"]
            if nurl.startswith(_SERVICES_PREFIX):
                rel = nurl.split("/", 4)[-1]  # drop "/services/data/vXX.0/"
            else:
                rel = nurl.lstrip("/")
            resp = connect_request(
                "GET", rel, None, target_org=target_org, api_version=api_version
            )
            if isinstance(resp, dict):
                records.extend(r for r in resp.get("records", []) if isinstance(r, dict))
            else:
                break
    return records


class Transport:
    """Binds the CLI transport to one org / api-version / dry-run setting.

    A thin OO wrapper over the module functions above and the injectable seam the
    lifecycle engine (:class:`_lifecycle.RampLifecycle`) and the mutator CLIs take.
    Any object exposing ``connect`` / ``soql`` with these signatures — e.g. a
    ``FakeTransport`` in the tests — is a drop-in substitute (no org).

    ``dry_run`` short-circuits *mutating* verbs (everything but GET/HEAD): they are
    logged and skipped; reads always execute so a dry-run still resolves ids.
    """

    def __init__(self, target_org: str, api_version: str = DEFAULT_API_VERSION,
                 dry_run: bool = False, logger: Callable[..., None] = None):
        self.target_org = target_org
        self.api_version = api_version
        self.dry_run = dry_run
        self.logger = logger or eprint

    def connect(self, method: str, path: str, body: Any = None,
                *, dry_run: Optional[bool] = None, timeout: Optional[int] = None) -> Any:
        return connect_request(
            method, path, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger, timeout=timeout,
        )

    def soql(self, query: str) -> List[Dict[str, Any]]:
        # Reads always execute (non-mutating), even under dry_run.
        return soql_query(
            query, target_org=self.target_org, api_version=self.api_version
        )
