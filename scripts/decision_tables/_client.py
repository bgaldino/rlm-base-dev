#!/usr/bin/env python3
"""Shared ``sf``-CLI transport for the Decision Table scripts (read *and* mutate).

Auth is delegated entirely to the ``sf`` CLI — this module never handles access
tokens, matching the standalone-script pattern already used in this repo
(``scripts/expression_sets/_client.py``, ``scripts/context_service/_client.py``,
``scripts/erd/*``). Every request goes through
``sf api request rest '<path>' -X <METHOD> [-b -] --target-org <alias>``,
which authenticates with the CLI's stored credentials.

``--target-org`` is always the *SF CLI* alias/username (e.g. ``rlm-base__beta``),
NEVER the CCI alias — there is no token on any command line and no CCI-vs-SF
alias ambiguity.

**Three transport surfaces**, because Decision Table authoring spans three APIs:

- **Tooling API** — the 5 setup objects (``DecisionTable`` ``0lD``,
  ``DecisionTableParameter`` ``0lP``, ``DecisionTableDatasetLink`` ``0lX``,
  ``DecisionTblDatasetParameter`` ``0lZ``, ``DecisionTableSourceCriteria``
  ``0VT``). Reached via ``tooling_query()`` → ``/tooling/query?q=…`` and
  ``tooling_sobject_request()`` → ``/tooling/sobjects/<Object>[/<id>|/describe]``.
  These objects are **not** on the normal REST ``/sobjects`` surface.
- **Connect API** — the Decision Table Definitions CRUD resource
  (``connect/business-rules/decision-table/definitions[/{id}]``), reached via
  ``connect_request()`` / ``connect_get()``.
- **Normal REST** — ``PricingRecipeTableMapping`` (trace) and source-object row
  dumps, reached via ``sobjects_request()`` / ``soql_query()``.

Mutation bodies are piped on **stdin** via ``-b -`` — no temp files, no
shell-quoting. The pure enum/field/spec logic lives in ``_schema``; this module
is transport only.
"""

import base64
import json
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

DEFAULT_API_VERSION = "67.0"
_REQUEST_TIMEOUT = 120  # seconds — reads
# A Connect/Metadata mutation that (de)activates or rebuilds a table can take
# minutes server-side; mirror the expression-set / context-service timeout.
_MUTATION_TIMEOUT = 600  # seconds

CONNECT_BASE = "connect/business-rules/decision-table"
DEFINITIONS_PATH = f"{CONNECT_BASE}/definitions"

# The 5 Decision Table setup objects — Tooling API only (see module docstring).
SETUP_OBJECTS = (
    "DecisionTable",
    "DecisionTableParameter",
    "DecisionTableDatasetLink",
    "DecisionTblDatasetParameter",
    "DecisionTableSourceCriteria",
)


class DecisionTableClientError(RuntimeError):
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
        raise DecisionTableClientError(
            "The 'sf' CLI was not found on PATH. Install the Salesforce CLI and "
            "authenticate to your org (`sf org login web --alias <alias>`)."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise DecisionTableClientError(
            f"'sf {' '.join(args)}' timed out after {timeout}s."
        ) from exc


def _summarize_body(body: Any) -> str:
    """A compact one-line shape summary of a mutation body for dry-run logs.

    A full Decision Table definition body (all columns + criteria inlined) can
    run long; logging it verbatim buries the preview. Summarize instead: top-level
    keys and per-collection counts when present. Small bodies (e.g.
    ``{"Status": "Inactive"}``) are shown verbatim since they are already legible.
    """
    if body is None:
        return ""
    raw = json.dumps(body)
    if len(raw) <= 200:
        return raw
    if isinstance(body, dict):
        parts = [f"keys={sorted(body.keys())}"]
        for coll in ("parameters", "decisionTableParameters", "sourceCriteria",
                     "decisionTableSourceCriterias"):
            val = body.get(coll)
            if isinstance(val, list):
                parts.append(f"{coll}={len(val)}")
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
    """Make an authenticated Salesforce REST/Connect/Tooling request via the sf CLI.

    ``path`` is relative to ``/services/data/vXX.0/`` (e.g.
    ``connect/business-rules/decision-table/definitions/<id>``,
    ``tooling/query?q=...``, or ``query?q=...``); the versioned prefix is
    prepended automatically because ``sf api request rest`` 404s on a bare path.

    ``body`` (a dict/list) is JSON-serialized and piped on stdin via ``-b -``.
    When ``dry_run`` is set, **mutating** verbs (anything other than GET/HEAD)
    are logged and skipped (returning ``{}``); **reads always execute** so the
    orchestrator can still resolve ids and log the real mutation sequence.

    Returns parsed JSON (``{}`` for an empty/204 response). Raises
    :class:`DecisionTableClientError` on a non-zero CLI exit.
    """
    log = logger or eprint
    method = method.upper()
    full_path = f"/services/data/v{api_version}/{path.lstrip('/')}"

    if dry_run and method not in ("GET", "HEAD"):
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
        raise DecisionTableClientError(
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
        raise DecisionTableClientError(
            f"Could not parse JSON from 'sf api request rest {method} {path}': {exc}\n"
            f"Raw output (truncated): {stdout[:400]}"
        ) from exc


def connect_get(path: str, target_org: str, api_version: str = DEFAULT_API_VERSION) -> Any:
    """GET a Salesforce REST/Connect resource via the sf CLI and return parsed JSON."""
    return connect_request("GET", path, None, target_org=target_org, api_version=api_version)


# --------------------------------------------------------------------------- #
# Tooling API — the 5 Decision Table setup objects live here, NOT on /sobjects.
# --------------------------------------------------------------------------- #

def tooling_query(
    soql: str, *, target_org: str, api_version: str = DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """Run a **Tooling** SOQL query (``/tooling/query``) and return its records.

    Follows ``nextRecordsUrl`` pagination. The setup objects (``DecisionTable``
    et al.) are only queryable through the Tooling surface, so DeveloperName →
    id resolution and the child-object reads go through here, not ``soql_query``.
    """
    return _paginated_query(
        f"tooling/query?q={quote(soql)}", target_org=target_org, api_version=api_version
    )


def tooling_sobject_request(
    method: str,
    sobject: str,
    record_id: Optional[str] = None,
    suffix: Optional[str] = None,
    body: Any = None,
    *,
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
    dry_run: bool = False,
    logger: Callable[..., None] = None,
) -> Any:
    """Tooling SObject request (``tooling/sobjects/{sobject}[/{id}][/{suffix}]``).

    ``suffix`` supports ``describe`` (``tooling/sobjects/DecisionTable/describe``).
    A Tooling GET of ``DecisionTable/{id}`` returns the ``Metadata`` complexvalue
    with the definition's children (parameters/criteria) inlined. Phase-2 mutators
    POST/PATCH/DELETE through the same path.
    """
    path = f"tooling/sobjects/{sobject}"
    if record_id:
        path = f"{path}/{record_id}"
    if suffix:
        path = f"{path}/{suffix}"
    return connect_request(
        method, path, body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


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
    """Normal-REST SObject request (``sobjects/{sobject}[/{id}]``).

    Used only for non-Tooling reads — ``PricingRecipeTableMapping`` (trace) and
    source-object describes for the data dump. The setup objects use
    :func:`tooling_sobject_request` instead.
    """
    path = f"sobjects/{sobject}"
    if record_id:
        path = f"{path}/{record_id}"
    return connect_request(
        method, path, body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


# --------------------------------------------------------------------------- #
# CSV Based Decision Table — data upload + read (dataSourceType == CsvUpload).
#
# A CsvUpload table's rows do NOT live on a queryable SObject; they are loaded by
# a two-phase Connect flow (live-verified 262 / v67.0) and read back through a
# Connect data sub-resource:
#
#   1. Insert a ``ContentVersion`` holding the CSV (first row = column headers
#      matching the INPUT/OUTPUT ``fieldName``s) → a ``068…`` ContentVersion id.
#   2. POST that id to the table's ``/file`` sub-resource, scoped to a version:
#      ``connect/business-rules/decision-table/{0lD…}/file?versionNumber=N``
#      with ``{"fileId":"068…","deleteAllRows":<bool>}`` — ``false`` appends,
#      ``true`` overwrites (destructive). The import is **async**
#      (``Metadata.uploadStatus``: UploadInProgress → Completed/…), but rows are
#      queryable via the data GET within seconds.
#
# The ``/data`` **GET** (v62+) reads rows back:
#   ``.../{0lD…}/data[?versionNumber=N][&filter=Field:Value][&limit=N]``
#   → ``{"rows":[{"id":"1FI…","rowData":{…}}],"totalRows":<count returned>}``.
# ⚠ ``totalRows`` is the count of rows IN THE RESPONSE (not a grand total) and
# ``offset`` is unreliable — read once with an optional ``limit``, never page by
# offset. (The ``/data`` **POST** row-edit path is non-functional on the probed
# org — the authoritative write path is ``/file``.)
# --------------------------------------------------------------------------- #

def content_version_insert(
    title: str,
    csv_text: str,
    *,
    path_on_client: str = "decision_table_rows.csv",
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
    dry_run: bool = False,
    logger: Callable[..., None] = None,
) -> Any:
    """Insert a ``ContentVersion`` holding ``csv_text`` (base64) → the ``068…`` id.

    Phase 1 of a CsvUpload data load. The CSV body is UTF-8 encoded and
    base64-wrapped into ``VersionData`` (the same pattern ``scripts/docgen`` uses
    for binary uploads). Returns the parsed POST response (``{"id","success"}``);
    honors ``dry_run`` via :func:`sobjects_request` (skipped+logged, returns
    ``{}``). The returned ``id`` is fed to :func:`upload_decision_table_csv`.
    """
    version_data = base64.b64encode(csv_text.encode("utf-8")).decode("ascii")
    body = {"Title": title, "PathOnClient": path_on_client, "VersionData": version_data}
    return sobjects_request(
        "POST", "ContentVersion", body=body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


def upload_decision_table_csv(
    record_id: str,
    file_id: str,
    *,
    delete_all_rows: bool = False,
    version_number: Optional[int] = None,
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
    dry_run: bool = False,
    logger: Callable[..., None] = None,
) -> Any:
    """POST a ContentVersion ``file_id`` to a table's ``/file`` sub-resource (async).

    Phase 2 of a CsvUpload data load. ``delete_all_rows=False`` **appends** to the
    existing rows; ``True`` **overwrites** (destructive — deletes all rows first).
    ``version_number`` targets a specific version (a 262 addition; when omitted the
    platform uses the current/active version). The import is asynchronous — poll
    the ``/data`` GET (or ``Metadata.uploadStatus``) for completion, not this
    response (``{"message":"We are uploading and processing the CSV file."}``).
    Honors ``dry_run`` via :func:`connect_request`.
    """
    path = f"{CONNECT_BASE}/{record_id}/file"
    if version_number is not None:
        path += f"?versionNumber={int(version_number)}"
    body = {"fileId": file_id, "deleteAllRows": bool(delete_all_rows)}
    return connect_request(
        "POST", path, body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


def get_decision_table_data(
    record_id: str,
    *,
    version_number: Optional[int] = None,
    row_filter: Optional[str] = None,
    limit: Optional[int] = None,
    target_org: str,
    api_version: str = DEFAULT_API_VERSION,
) -> Any:
    """GET the uploaded rows of a CsvUpload table (``.../{id}/data``, v62+).

    Optional ``version_number`` (defaults to the current/active version),
    ``row_filter`` (``"Field:Value"`` server-side filter), and ``limit``. Returns
    the parsed envelope ``{"rows":[{"id","rowData":{…}}],"totalRows":<count>}``.
    A read — always executes, even under a dry-run transport. Reads the response
    in ONE call (``totalRows`` counts returned rows, not a grand total; ``offset``
    is unreliable — see the module note), so callers cap with ``limit`` rather than
    paging.
    """
    query: List[str] = []
    if version_number is not None:
        query.append(f"versionNumber={int(version_number)}")
    if row_filter:
        query.append(f"filter={quote(row_filter)}")
    if limit is not None:
        query.append(f"limit={int(limit)}")
    path = f"{CONNECT_BASE}/{record_id}/data"
    if query:
        path += "?" + "&".join(query)
    return connect_request(
        "GET", path, None, target_org=target_org, api_version=api_version
    )


def soql_literal(value: Any) -> str:
    """Escape a value for safe interpolation inside a single-quoted SOQL literal."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def _paginated_query(
    initial_path: str, *, target_org: str, api_version: str
) -> List[Dict[str, Any]]:
    """Shared pagination for normal-REST and Tooling query endpoints.

    ``nextRecordsUrl`` from the Tooling endpoint is a versioned absolute path
    (``/services/data/vXX.0/tooling/query/01g…``); strip the versioned prefix so
    ``connect_request`` rebuilds it, preserving the ``tooling/`` segment.
    """
    resp = connect_request(
        "GET", initial_path, None, target_org=target_org, api_version=api_version
    )
    records: List[Dict[str, Any]] = []
    if isinstance(resp, dict):
        records.extend(r for r in resp.get("records", []) if isinstance(r, dict))
        while not resp.get("done", True) and resp.get("nextRecordsUrl"):
            nurl = resp["nextRecordsUrl"]
            marker = "/services/data/"
            if nurl.startswith(marker):
                # Drop "/services/data/vXX.0/" so connect_request rebuilds it;
                # any remaining "tooling/" segment is preserved.
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


def soql_query(
    soql: str, *, target_org: str, api_version: str = DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """Run a **normal-REST** SOQL query and return its ``records`` list.

    Follows ``nextRecordsUrl``. Used for ``PricingRecipeTableMapping`` and
    source-object row dumps — NOT the setup objects (use :func:`tooling_query`).
    """
    return _paginated_query(
        f"query?q={quote(soql)}", target_org=target_org, api_version=api_version
    )


def eprint(*args, **kwargs):
    """Print to stderr (so --json stdout stays clean)."""
    print(*args, file=sys.stderr, **kwargs)


class Transport:
    """Binds the CLI transport to one org / api-version / dry-run setting.

    A thin OO wrapper over the module functions above. It is the injectable seam
    the read CLIs (Phase 1) and the lifecycle engine + mutator CLIs (Phase 2)
    take, so all can be unit-tested with a fake transport (no org): any object
    exposing ``connect`` / ``connect_get`` / ``tooling_query`` /
    ``tooling_sobject`` / ``sobject`` / ``soql`` with these signatures works.

    ``dry_run`` on the bound transport short-circuits *mutating* verbs
    (everything but GET/HEAD) — they are logged and skipped; reads always execute
    so a dry-run can still resolve ids and log the real mutation sequence.
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

    def connect_get(self, path: str) -> Any:
        """GET a Connect/REST resource (reads always execute, even under dry_run)."""
        return connect_get(path, self.target_org, self.api_version)

    def tooling_query(self, query: str) -> List[Dict[str, Any]]:
        # Reads always execute (non-mutating), even under dry_run.
        return tooling_query(
            query, target_org=self.target_org, api_version=self.api_version
        )

    def tooling_sobject(self, method: str, sobject: str, record_id: Optional[str] = None,
                        suffix: Optional[str] = None, body: Any = None,
                        *, dry_run: Optional[bool] = None) -> Any:
        return tooling_sobject_request(
            method, sobject, record_id, suffix, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
        )

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

    # -- CSV Based Decision Table data layer (dataSourceType == CsvUpload) --

    def content_version_insert(self, title: str, csv_text: str,
                               *, path_on_client: str = "decision_table_rows.csv",
                               dry_run: Optional[bool] = None) -> Any:
        return content_version_insert(
            title, csv_text, path_on_client=path_on_client,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
        )

    def upload_decision_table_csv(self, record_id: str, file_id: str,
                                  *, delete_all_rows: bool = False,
                                  version_number: Optional[int] = None,
                                  dry_run: Optional[bool] = None) -> Any:
        return upload_decision_table_csv(
            record_id, file_id, delete_all_rows=delete_all_rows,
            version_number=version_number,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
        )

    def get_decision_table_data(self, record_id: str, *,
                                version_number: Optional[int] = None,
                                row_filter: Optional[str] = None,
                                limit: Optional[int] = None) -> Any:
        # Reads always execute (non-mutating), even under dry_run.
        return get_decision_table_data(
            record_id, version_number=version_number, row_filter=row_filter,
            limit=limit, target_org=self.target_org, api_version=self.api_version,
        )
