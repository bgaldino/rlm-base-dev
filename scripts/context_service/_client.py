#!/usr/bin/env python3
"""Shared transport for the Context Service scripts (read *and* mutate).

Auth is delegated entirely to the ``sf`` CLI — this module never handles access
tokens, matching the standalone-script pattern already used in this repo
(``scripts/erd/validate_erd_against_org.py``,
``scripts/erd/schema_diff/extract_schema.py``, which shell out to ``sf``).

Every request goes through ``sf api request rest '<path>' -X <METHOD> [-b -]
--target-org <alias>``, which makes an authenticated request using the CLI's
stored credentials. No ``access_token`` is ever passed on a command line, and
there is no CCI-vs-SF alias ambiguity: ``--target-org`` is always the *SF CLI*
alias/username (e.g. ``rlm-base__beta``), never the CCI alias (e.g. ``beta``).

Mutation bodies are piped on **stdin** via ``-b -`` (``--body -``) — no temp
files, no shell-quoting. Verified live on 262 / v67.0: the server parses a
stdin-piped JSON body on POST/PATCH/DELETE. On any 4xx/5xx the CLI exits
non-zero and prints the Salesforce error array (``[{errorCode, message}]``) to
stdout; :class:`ContextClientError` captures the parsed ``error_codes`` so
callers can implement DUPLICATE_VALUE / UNKNOWN_EXCEPTION recovery the way
``tasks/rlm_extend_stdctx.py`` does.
"""

import json
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

DEFAULT_API_VERSION = "67.0"
_REQUEST_TIMEOUT = 120  # seconds — reads
# Context-definition create/extend calls can take 5-10 minutes server-side
# (mirrors _READ_TIMEOUT in tasks/rlm_extend_stdctx.py). Used for mutating verbs.
_MUTATION_TIMEOUT = 600  # seconds


class ContextClientError(RuntimeError):
    """Raised when a CLI call fails in a way the caller should surface.

    Carries the parsed Salesforce ``error_codes`` (e.g. ``["DUPLICATE_VALUE"]``)
    and the raw response ``body`` so orchestration code can branch on them
    (recover an existing definition, skip a missing base, etc.) instead of
    re-parsing the message string.
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
    """Pull Salesforce ``errorCode`` values from a CLI error payload.

    The CLI prints the raw Salesforce error array on stdout for a failed
    request; tolerate a bare object or non-JSON noise (returns []).
    """
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
        raise ContextClientError(
            "The 'sf' CLI was not found on PATH. Install the Salesforce CLI and "
            "authenticate to your org (`sf org login web --alias <alias>`)."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ContextClientError(
            f"'sf {' '.join(args)}' timed out after {timeout}s."
        ) from exc


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
    ``connect/context-definitions`` or ``sobjects/ContextAttribute/<id>``); the
    fully versioned path is prepended automatically because ``sf api request
    rest`` 404s on a bare ``connect/...`` path.

    ``body`` (a dict/list) is JSON-serialized and piped on stdin via ``-b -``.
    When ``dry_run`` is set, **mutating** verbs (anything other than GET/HEAD)
    are not shelled out — the intended call is logged (``[dry-run] {METHOD}
    {path} {json}``, matching the CCI task's ``_make_request`` dry-run log) and
    ``{}`` is returned. **Reads (GET/HEAD) always execute**, even under dry-run,
    so the orchestrator can still resolve ids and fetch detail and thereby log
    the *real* mutation sequence (mirrors :func:`soql_query`, which never skips).

    Returns parsed JSON (``{}`` for an empty/204 response). Raises
    :class:`ContextClientError` on a non-zero CLI exit, with ``error_codes``
    populated from the Salesforce error payload.
    """
    log = logger or eprint
    method = method.upper()
    full_path = f"/services/data/v{api_version}/{path.lstrip('/')}"

    if dry_run and method not in ("GET", "HEAD"):
        body_repr = json.dumps(body) if body is not None else ""
        log(f"[dry-run] {method} {full_path} {body_repr}")
        return {}

    args = ["api", "request", "rest", full_path, "-X", method, "--target-org", target_org]
    input_text: Optional[str] = None
    if body is not None:
        args += ["-b", "-"]
        input_text = json.dumps(body)
    elif method not in ("GET", "HEAD"):
        # `sf api request rest` rejects a bodiless mutating verb (notably DELETE)
        # with "No 'mode' found in 'body' entry" — it wants a body stanza even
        # when the request has no payload. Piping an empty stdin body via `-b -`
        # satisfies the CLI (live-confirmed on v67.0: a bodiless DELETE fails,
        # the same DELETE with an empty `-b -` reaches the server).
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
        raise ContextClientError(
            f"sf api request {method} '{path}' failed for org '{target_org}'"
            f"{code_note}:\n{detail}\n\n"
            f"Confirm the SF CLI alias is correct (this is the *sf* alias, e.g. "
            f"'rlm-base__beta', not the CCI alias 'beta') and that you are "
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
        raise ContextClientError(
            f"Could not parse JSON from 'sf api request rest {method} {path}': {exc}\n"
            f"Raw output (truncated): {stdout[:400]}"
        ) from exc


def connect_get(path: str, target_org: str, api_version: str = DEFAULT_API_VERSION) -> Any:
    """GET a Salesforce REST/Connect resource via the sf CLI and return parsed JSON.

    Thin wrapper over :func:`connect_request` so reads and writes share one
    transport code path.
    """
    return connect_request(
        "GET", path, None, target_org=target_org, api_version=api_version
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
    """SObject REST request (``sobjects/{sobject}[/{id}]``).

    Needed for the three operations the Connect PATCH cannot do:
    ``MappedContextDefinition`` on ContextNodeMapping, relationship-traversal
    hydration (ContextAttributeMapping + ContextAttrHydrationDetail), and
    ``IsTransient`` on ContextAttribute.
    """
    path = f"sobjects/{sobject}"
    if record_id:
        path = f"{path}/{record_id}"
    return connect_request(
        method, path, body,
        target_org=target_org, api_version=api_version, dry_run=dry_run, logger=logger,
    )


def soql_literal(value: Any) -> str:
    """Escape a value for safe interpolation inside a single-quoted SOQL literal.

    SOQL string literals escape ``\\`` and ``'`` with a backslash (per the SOQL
    reference). Callers still supply the surrounding quotes:
    ``f"WHERE Name='{soql_literal(name)}'"``. This guards plan-authored values
    (e.g. a ``contextAttribute`` name) from producing a malformed query — Context
    Service attribute API names are normally alphanumeric, but plan JSON is
    free-text and reaches these queries unvalidated.
    """
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def soql_query(
    soql: str, *, target_org: str, api_version: str = DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """Run a SOQL query and return its ``records`` list (always executes — reads
    are non-mutating, so this ignores dry-run, matching the CCI task's
    traversal-hydration idempotency check)."""
    resp = connect_request(
        "GET", f"query?q={quote(soql)}", None,
        target_org=target_org, api_version=api_version,
    )
    if isinstance(resp, dict):
        records = resp.get("records")
        if isinstance(records, list):
            return records
    return []


def normalize_definition_list(response: Any) -> List[Dict[str, Any]]:
    """Return a list of definition dicts from a list-endpoint response.

    The Connect list endpoint may return a bare list or wrap the rows under one
    of several keys, so probe each. Shared by list_contexts.py and
    describe_context.py so both tools resolve the same set of definitions.
    """
    if isinstance(response, list):
        return [d for d in response if isinstance(d, dict)]
    if isinstance(response, dict):
        for key in ("contextDefinitionList", "contextDefinitions", "records"):
            value = response.get(key)
            if isinstance(value, list):
                return [d for d in value if isinstance(d, dict)]
    return []


def definition_developer_name(definition: Dict[str, Any]) -> Optional[str]:
    """Read a definition's developer name, tolerating camelCase or PascalCase."""
    if not isinstance(definition, dict):
        return None
    return definition.get("developerName") or definition.get("DeveloperName")


def active_version(definition: Dict[str, Any]) -> Dict[str, Any]:
    """Return the *active* version block of a context-definition GET response.

    The platform enforces exactly one ContextDefinitionVersion per definition
    (MAX_LIMIT_EXCEEDED on second insert, live-verified v67.0), so
    ``contextDefinitionVersionList`` is always a 0-or-1-element list and
    ``versions[0]`` is equivalent to an isActive-preferring search. This helper
    exists for forward-compatibility; prefer the version whose ``isActive``
    flag is set, fall back to the first (only) entry when none is flagged.
    """
    if not isinstance(definition, dict):
        return {}
    versions = [
        v for v in (definition.get("contextDefinitionVersionList") or [])
        if isinstance(v, dict)
    ]
    if not versions:
        return {}
    for version in versions:
        if version.get("isActive") in (True, "true"):
            return version
    return versions[0]


def iter_nodes(node_list: Optional[List[Dict[str, Any]]]):
    """Yield (node, depth) for a nested contextNodes tree (depth starts at 0).

    Handles both the ``{"contextNodes": [...]}`` wrapper shape and a bare list,
    matching the defensive parsing in tasks/rlm_context_service.py.
    """
    def _walk(nodes, depth):
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            yield node, depth
            child_container = node.get("childNodes", {})
            children = (
                child_container.get("contextNodes", [])
                if isinstance(child_container, dict)
                else (child_container or [])
            )
            yield from _walk(children, depth + 1)

    yield from _walk(node_list, 0)


def node_attributes(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a node's attribute list, tolerating list-or-wrapper shapes."""
    container = node.get("attributes", {})
    if isinstance(container, list):
        return container
    if isinstance(container, dict):
        return container.get("contextAttributes", []) or []
    return []


def attr_tag_list(attr: Dict[str, Any]) -> List[Dict[str, Any]]:
    """An attribute's tags, unwrapping the ``{"attributeTags": [...]}`` container.

    A Connect GET returns an attribute's tags either as a bare list or wrapped in
    a container dict; iterating the wrapper directly yields its keys (strings),
    which downstream tag handling silently drops. This is the single source of
    truth for that unwrap — ``_delete``, ``_mutate``, and ``_payload`` all defer
    here so a GET-shape change is fixed in one place. Note the node-vs-attribute
    key asymmetry: attributes unwrap under ``attributeTags`` (see
    :func:`node_tag_list` for nodes).
    """
    tags = attr.get("attributeTags") or attr.get("tags") or []
    if isinstance(tags, dict):
        tags = tags.get("attributeTags") or []
    return tags if isinstance(tags, list) else []


def node_tag_list(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """A node's tags, unwrapping the ``{"tags": [...]}`` container (rare).

    The node key is ``tags`` (attributes use ``attributeTags``); preserve that
    asymmetry — it is why this is a separate helper from :func:`attr_tag_list`.
    """
    tags = node.get("tags") or []
    if isinstance(tags, dict):
        tags = tags.get("tags") or []
    return tags if isinstance(tags, list) else []


def attr_tag_names(attr: Dict[str, Any]) -> set:
    """Set of tag ``name`` values on an attribute (via :func:`attr_tag_list`)."""
    return {t.get("name") for t in attr_tag_list(attr)
            if isinstance(t, dict) and t.get("name")}


def node_tag_names(node: Dict[str, Any]) -> set:
    """Set of tag ``name`` values on a node (via :func:`node_tag_list`)."""
    return {t.get("name") for t in node_tag_list(node)
            if isinstance(t, dict) and t.get("name")}


def guard_active(
    detail: Dict[str, Any], *, context_id: str, auto_deactivate: bool,
    is_active_fn: Callable[[Dict[str, Any]], bool],
    deactivate_fn: Callable[[str], None],
    fetch_detail_fn: Callable[[str], Dict[str, Any]],
    dry_run: bool, logger: Callable[..., None],
    refuse_message: str, exception_type: type,
    deactivate_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Shared "refuse-or-deactivate on an active version" core.

    The platform blocks *modifying or deleting* an existing artifact on an active
    context definition version. ``_delete``, ``_mutate``, and ``_apply`` each need
    that behavior but differ in their **trigger** (unconditional / op-gated /
    flag-gated), **exception type** (``DeletePreflightError`` /
    ``MutatePreflightError`` / ``ContextClientError``), and how they reach
    deactivation. Each keeps its own thin wrapper (trigger + message +
    ``exception_type`` + bound callables); this holds only the common body so the
    three cannot drift:

      * already inactive -> return ``detail`` unchanged (no-op);
      * active and not ``auto_deactivate`` -> raise ``exception_type(refuse_message)``;
      * active and ``auto_deactivate`` -> log, ``deactivate_fn(context_id)``, then
        (unless ``dry_run``) refetch via ``fetch_detail_fn`` and return it.

    Under ``dry_run`` the deactivate PATCH was logged, not executed, so the live
    detail is still active — return ``detail`` rather than refetching (which would
    loop the guard). The caller must apply its own trigger gate *before* calling
    this (e.g. ``_mutate`` returns early when the op does not require inactive).
    """
    if not is_active_fn(detail):
        return detail
    if not auto_deactivate:
        raise exception_type(refuse_message)
    logger(deactivate_message
           or f"Definition {context_id} is active; deactivating first.")
    deactivate_fn(context_id)
    if dry_run:
        return detail
    return fetch_detail_fn(context_id)


def eprint(*args, **kwargs):
    """Print to stderr (so --json stdout stays clean)."""
    print(*args, file=sys.stderr, **kwargs)


# --------------------------------------------------------------------------- #
# Transport adapter (injectable)
# --------------------------------------------------------------------------- #

class Transport:
    """Binds the CLI transport to one org / api-version / dry-run setting.

    A thin OO wrapper over the ``connect_request`` / ``sobjects_request`` /
    ``soql_query`` module functions above — it exists as the injectable seam so
    the design-time orchestrator (``_apply.ContextApplier``) and the runtime
    lifecycle (``_runtime``) can be unit-tested with a fake (no org). Any object
    exposing ``request`` / ``sobject`` / ``soql`` with these signatures works.
    """

    def __init__(self, target_org: str, api_version: str = DEFAULT_API_VERSION,
                 dry_run: bool = False, logger: Callable[..., None] = None):
        self.target_org = target_org
        self.api_version = api_version
        self.dry_run = dry_run
        self.logger = logger or eprint

    def request(self, method: str, path: str, body: Any = None,
                *, dry_run: Optional[bool] = None) -> Any:
        # ``dry_run`` overrides the transport's bound flag for this one call — the
        # runtime path uses it to force read-shaped POSTs (query-record,
        # query-tags) to execute even under a dry-run session (see _runtime.py /
        # the dry-run contract). ``None`` (the design-time default) inherits.
        return connect_request(
            method, path, body,
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
