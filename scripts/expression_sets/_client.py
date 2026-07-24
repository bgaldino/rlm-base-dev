#!/usr/bin/env python3
"""Shared ``sf``-CLI transport for the Expression Set scripts (read *and* mutate).

Auth is delegated entirely to the ``sf`` CLI — this module never handles access
tokens, matching the standalone-script pattern already used in this repo
(``scripts/context_service/_client.py``, ``scripts/erd/*``). Every request goes
through ``sf api request rest '<path>' -X <METHOD> [-b -] --target-org <alias>``,
which authenticates with the CLI's stored credentials.

``--target-org`` is always the *SF CLI* alias/username (e.g.
``rlm-base__beta``), NEVER the CCI alias — there is no token on any
command line and no CCI-vs-SF alias ambiguity.

The BRE Expression Set Connect resource is ``connect/business-rules/
expression-set/{9QL}`` where ``{9QL}`` is the runtime ``ExpressionSet`` record
Id. Mutation bodies are piped on **stdin** via ``-b -`` — no temp files, no
shell-quoting.

The pure payload/graph/overlay logic lives in ``_payload`` / ``_graph`` /
``_overlay``; this module is transport only.
"""

import json
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

DEFAULT_API_VERSION = "67.0"
_REQUEST_TIMEOUT = 120  # seconds — reads
# A Connect PATCH/POST that reactivates a large procedure can take minutes
# server-side; mirror the context-service mutation timeout.
_MUTATION_TIMEOUT = 600  # seconds

CONNECT_BASE = "connect/business-rules/expression-set"


class ExpressionSetClientError(RuntimeError):
    """Raised when a CLI call fails in a way the caller should surface.

    Carries the parsed Salesforce ``error_codes`` (e.g. ``["INVALID_FIELD"]``)
    and the raw response ``body`` so callers can branch on them.
    """

    def __init__(self, message: str, *, error_codes: Optional[List[str]] = None,
                 body: str = "", returncode: Optional[int] = None):
        super().__init__(message)
        self.error_codes = error_codes or []
        self.body = body
        self.returncode = returncode

    def has_error_code(self, code: str) -> bool:
        return code in self.error_codes


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
        raise ExpressionSetClientError(
            "The 'sf' CLI was not found on PATH. Install the Salesforce CLI and "
            "authenticate to your org (`sf org login web --alias <alias>`)."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ExpressionSetClientError(
            f"'sf {' '.join(args)}' timed out after {timeout}s."
        ) from exc


def _summarize_body(body: Any) -> str:
    """A compact one-line shape summary of a mutation body for dry-run logs.

    A full expression-set definition PATCH body is 100+ KB; logging it verbatim
    buries the preview. Summarize instead: top-level keys, and per-version step /
    variable counts when present. Small bodies (e.g. ``{"IsActive": false}``) are
    shown verbatim since they are already legible.
    """
    if body is None:
        return ""
    raw = json.dumps(body)
    if len(raw) <= 200:
        return raw
    if isinstance(body, dict):
        parts = [f"keys={sorted(body.keys())}"]
        versions = body.get("versions")
        if isinstance(versions, list):
            for i, v in enumerate(versions):
                if isinstance(v, dict):
                    parts.append(
                        f"versions[{i}]: {len(v.get('steps') or [])} step(s), "
                        f"{len(v.get('variables') or [])} variable(s)"
                    )
        return f"<{len(raw)} bytes> {'; '.join(parts)}"
    if isinstance(body, list):
        return f"<{len(raw)} bytes, list of {len(body)}>"
    return f"<{len(raw)} bytes>"


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

    ``path`` is relative to ``/services/data/vXX.0/`` (e.g.
    ``connect/business-rules/expression-set/<9QL>`` or ``query?q=...``); the
    versioned prefix is prepended automatically because ``sf api request rest``
    404s on a bare ``connect/...`` path.

    ``body`` (a dict/list) is JSON-serialized and piped on stdin via ``-b -``.
    When ``dry_run`` is set, **mutating** verbs (anything other than GET/HEAD)
    are logged and skipped (returning ``{}``); **reads always execute** so the
    orchestrator can still resolve ids and log the real mutation sequence.

    Returns parsed JSON (``{}`` for an empty/204 response). Raises
    :class:`ExpressionSetClientError` on a non-zero CLI exit.
    """
    log = logger or eprint
    method = method.upper()
    full_path = f"/services/data/v{api_version}/{path.lstrip('/')}"

    if dry_run and method not in ("GET", "HEAD"):
        # Summarize the body rather than dumping it — a full expression-set PATCH
        # body is 100+ KB and drowns the preview. Show the shape (top-level keys,
        # step/variable counts) so the plan is legible; the exact payload is
        # deterministic from the inputs anyway.
        log(f"[dry-run] {method} {full_path} {_summarize_body(body)}")
        return {}

    args = ["api", "request", "rest", full_path, "-X", method, "--target-org", target_org]
    input_text: Optional[str] = None
    if body is not None:
        args += ["-b", "-"]
        input_text = json.dumps(body)
    elif method not in ("GET", "HEAD"):
        # `sf api request rest` rejects a bodiless mutating verb (notably DELETE)
        # with "No 'mode' found in 'body' entry"; an empty stdin body satisfies it.
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
        raise ExpressionSetClientError(
            f"sf api request {method} '{path}' failed for org '{target_org}'"
            f"{code_note}:\n{detail}\n\n"
            f"Confirm the SF CLI alias is correct (this is the *sf* alias, e.g. "
            f"'rlm-base__beta', not the CCI alias) and that you are "
            f"authenticated (`sf org login web --alias {target_org}`).",
            error_codes=error_codes,
            body=stdout,
            returncode=result.returncode,
        )
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ExpressionSetClientError(
            f"Could not parse JSON from 'sf api request rest {method} {path}': {exc}\n"
            f"Raw output (truncated): {stdout[:400]}"
        ) from exc


def connect_get(path: str, target_org: str, api_version: str = DEFAULT_API_VERSION) -> Any:
    """GET a Salesforce REST/Connect resource via the sf CLI and return parsed JSON."""
    return connect_request("GET", path, None, target_org=target_org, api_version=api_version)


def sobjects_request(
    method: str,
    sobject: str,
    record_id: Optional[str] = None,
    body: Any = None,
    *,
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
    dry_run: bool = False,
    logger: Callable[..., None] = None,
) -> Any:
    """SObject REST request (``sobjects/{sobject}[/{id}]``).

    Used for the version-state PATCHes (``ExpressionSetVersion.IsActive``,
    ``ProcedurePlanDefinitionVersion.IsActive``,
    ``ExpressionSet.ResourceInitializationType``) the Connect resource cannot do.
    """
    path = f"sobjects/{sobject}"
    if record_id:
        path = f"{path}/{record_id}"
    return connect_request(
        method, path, body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


def soql_literal(value: Any) -> str:
    """Escape a value for safe interpolation inside a single-quoted SOQL literal."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def soql_query(
    soql: str, *, target_org: str, api_version: str = DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """Run a SOQL query and return its ``records`` list, following ``nextRecordsUrl``.

    Reads always execute (non-mutating), even under dry-run. Pagination mirrors
    the CCI task's ``_soql_query`` so a >2000-row procedure export is complete.
    """
    resp = connect_request(
        "GET", f"query?q={quote(soql)}", None,
        target_org=target_org, api_version=api_version,
    )
    records: List[Dict[str, Any]] = []
    if isinstance(resp, dict):
        records.extend(r for r in resp.get("records", []) if isinstance(r, dict))
        while not resp.get("done", True) and resp.get("nextRecordsUrl"):
            # nextRecordsUrl is an already-versioned absolute path
            # (/services/data/vXX.0/query/01g...); strip the prefix connect_request re-adds.
            nurl = resp["nextRecordsUrl"]
            marker = "/services/data/"
            if nurl.startswith(marker):
                # Drop "/services/data/vXX.0/" so connect_request rebuilds it.
                rel = nurl.split("/", 4)[-1]
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


def eprint(*args, **kwargs):
    """Print to stderr (so --json stdout stays clean)."""
    print(*args, file=sys.stderr, **kwargs)


class Transport:
    """Binds the CLI transport to one org / api-version / dry-run setting.

    A thin OO wrapper over the ``connect_request`` / ``sobjects_request`` /
    ``soql_query`` / ``connect_get`` module functions above. It is the injectable
    seam the lifecycle engine (``_lifecycle.LifecycleEngine``) and the mutator
    CLIs take, so both can be unit-tested with a fake transport (no org): any
    object exposing ``connect`` / ``sobject`` / ``soql`` / ``get`` with these
    signatures works.

    ``dry_run`` on the bound transport short-circuits *mutating* verbs
    (everything but GET/HEAD) in ``connect_request`` — they are logged and
    skipped; reads always execute so a dry-run can still resolve ids and log the
    real mutation sequence.
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

    def get(self, path: str) -> Any:
        """GET a resource (reads always execute, even under dry_run)."""
        return connect_get(path, self.target_org, self.api_version)

    def sobject(self, method: str, sobject: str, record_id: Optional[str] = None,
                body: Any = None, *, dry_run: Optional[bool] = None) -> Any:
        return sobjects_request(
            method, sobject, record_id, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
        )

    def soql(self, query: str) -> List[Dict[str, Any]]:
        # Reads always execute (non-mutating), even under dry_run.
        return soql_query(
            query, target_org=self.target_org, api_version=self.api_version
        )
