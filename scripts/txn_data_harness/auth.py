"""Authentication + REST transport for the demo data generator.

``SfRestClient`` hides the HTTP transport entirely so the rest of the tool is
endpoint/shape-agnostic. Two transports live behind one interface:

* ``requests`` (default) -- native ``requests.Session`` with connection pooling
  and bounded retry/backoff. Best for a high-volume generator where per-call
  latency dominates. Sessions are NOT thread-safe, so we hand each worker its
  own session via thread-local storage (see ``_session``).
* ``cli`` (fallback) -- shells out to ``sf api request rest`` so our process
  never sees a token. Maximally stable if every token-display command ever
  disappears, at the cost of a process spawn per call. Select with
  ``--transport cli``.

Token + instance URL come from TWO ``sf`` CLI calls (verified live; see
CONTRACTS.md "Environment verified"):

* token       -> ``sf org auth show-access-token`` (returns ONLY accessToken)
* instanceUrl -> ``sf org display`` (non-secret)

The token is held in memory for the run only -- never written to disk, never
logged, and never passed *to* the ``sf`` CLI as an argument (CLAUDE.md rule:
"never pass access_token to sf CLI"; we read it OUT of the CLI, we don't feed
it in). The ``cli`` transport passes no token at all.
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

log = logging.getLogger("txn_data_harness.auth")

DEFAULT_API_VERSION = "68.0"  # the repo API version; do not silently float to latest.

# Retry on transient transport failures only.
_RETRYABLE_STATUS = {420, 429, 500, 502, 503, 504}
_MAX_RETRIES = 4
_BACKOFF_BASE = 1.5  # seconds; exponential: base * 2**attempt


class SfCliError(RuntimeError):
    """An ``sf`` CLI invocation failed (auth resolution or cli transport)."""


class SfApiError(RuntimeError):
    """A Salesforce REST call returned a non-2xx status after retries."""

    def __init__(self, status: int, body: str, method: str, path: str):
        self.status = status
        self.body = body
        self.method = method
        self.path = path
        super().__init__(f"{method} {path} -> HTTP {status}: {body[:500]}")


def _run_sf(args: list[str]) -> dict:
    """Run an ``sf ... --json`` command and return parsed ``result``.

    Never include a token in ``args`` -- these commands authenticate via the
    CLI's own stored org auth, keyed by ``--target-org <alias>``.
    """
    cmd = ["sf", *args, "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SfCliError(
            f"`{' '.join(cmd)}` failed (exit {proc.returncode}): {_sf_error_text(proc)}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        # Never echo the output: on `org auth show-access-token` it can hold the token.
        raise SfCliError(
            f"`{' '.join(cmd)}` returned output that is not JSON "
            f"({len(proc.stdout)} characters, not shown)"
        ) from None  # the JSONDecodeError keeps the whole output in .doc
    if not isinstance(payload, dict):
        raise SfCliError(f"`{' '.join(cmd)}` returned JSON that is not an object")
    return payload.get("result", {})


def _sf_error_text(proc: subprocess.CompletedProcess) -> str:
    """The error text of a failed ``sf --json`` call, never its raw stdout.

    The ``name`` and ``message`` of the JSON error ``sf`` prints on stdout first (stderr
    often holds only Node or update warnings); otherwise stderr. Raw stdout is not shown,
    because a token command's output can carry the token.
    """
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            name = payload.get("name")
            return f"{name}: {message.strip()}" if isinstance(name, str) and name else message.strip()
    if proc.stderr.strip():
        return proc.stderr.strip()
    return f"no error text ({len(proc.stdout)} characters of output, not shown)"


def resolve_auth(alias: str) -> tuple[str, str]:
    """Resolve ``(access_token, instance_url)`` for an sf alias/username.

    Two calls, because no single command reliably returns both (CONTRACTS.md):
    the token from ``org auth show-access-token``, the instance URL from
    ``org display`` (non-secret).
    """
    token_result = _run_sf(["org", "auth", "show-access-token", "--target-org", alias])
    access_token = token_result.get("accessToken") if isinstance(token_result, dict) else None
    # Some CLI shapes nest under a list/other key; be defensive but explicit.
    if not access_token and isinstance(token_result, str):
        access_token = token_result
    if not access_token:
        raise SfCliError(
            f"Could not read an access token for org '{alias}'. "
            f"Check `sf org auth show-access-token --target-org {alias} --json`."
        )

    display = _run_sf(["org", "display", "--target-org", alias])
    instance_url = display.get("instanceUrl")
    if not instance_url:
        raise SfCliError(
            f"Could not read instanceUrl for org '{alias}'. "
            f"Check `sf org display --target-org {alias} --json`."
        )
    return access_token, instance_url.rstrip("/")


# BillingSettings retrieve on the cli transport: sf's --wait and our own cap.
_RETRIEVE_WAIT_MINUTES = 1
_RETRIEVE_TIMEOUT_S = 90

# Metadata SOAP readMetadata for BillingSettings (no REST equivalent).
_BILLING_SETTINGS_SOAP = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
    'xmlns:met="http://soap.sforce.com/2006/04/metadata">'
    "<soapenv:Header><met:SessionHeader><met:sessionId>{session}</met:sessionId>"
    "</met:SessionHeader></soapenv:Header><soapenv:Body><met:readMetadata>"
    "<met:type>BillingSettings</met:type><met:fullNames>Billing</met:fullNames>"
    "</met:readMetadata></soapenv:Body></soapenv:Envelope>"
)


_CLI_STATUS_LINE = re.compile(r"^HTTP/\S+\s+(\d{3})\b")
_CLI_HEADER_LINE = re.compile(r"^[A-Za-z0-9!#$%&'*+.^_`|~-]+:")


def parse_cli_response(stdout: str) -> tuple[Optional[int], str]:
    """Split ``sf api request rest --include`` output into ``(status, body)``.

    The CLI prints ``HTTP/1.1 <status>``, the response headers one per line,
    then the body, with no blank line in between (sf 2.159, measured
    2026-11-25 on 200, 400 and 404). Returns ``(None, stdout)`` when there is
    no status line (the request never reached the API).
    """
    text = (stdout or "").lstrip("\r\n")
    lines = text.split("\n")
    m = _CLI_STATUS_LINE.match(lines[0]) if lines else None
    if not m:
        return None, (stdout or "").strip()
    i = 1
    while i < len(lines) and _CLI_HEADER_LINE.match(lines[i].rstrip("\r")):
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return int(m.group(1)), "\n".join(lines[i:]).strip()


@dataclass
class SfRestClient:
    """Transport-agnostic Salesforce REST client.

    Construct via :meth:`from_alias`. All paths are absolute service paths
    (e.g. ``/services/data/v68.0/sobjects/Order/<id>``); ``query`` builds the
    query path for you.
    """

    alias: str
    access_token: str = field(repr=False)  # never in a repr, log or traceback
    instance_url: str
    api_version: str = DEFAULT_API_VERSION
    transport: str = "requests"  # "requests" | "cli"
    # thread-local session store; one requests.Session per worker thread.
    _local: threading.local = field(default_factory=threading.local, repr=False)

    # ----- construction -----------------------------------------------------
    @classmethod
    def from_alias(
        cls,
        alias: str,
        api_version: Optional[str] = None,
        transport: str = "requests",
    ) -> "SfRestClient":
        access_token, instance_url = resolve_auth(alias)
        client = cls(
            alias=alias,
            access_token=access_token,
            instance_url=instance_url,
            api_version=api_version or DEFAULT_API_VERSION,
            transport=transport,
        )
        if api_version == "latest":
            client.api_version = client._latest_api_version()
        log.debug(
            "SfRestClient ready: alias=%s instance=%s v%s transport=%s",
            alias, instance_url, client.api_version, transport,
        )
        return client

    # ----- session management (requests transport) --------------------------
    @property
    def _session(self) -> requests.Session:
        """Return this thread's Session, creating it on first use.

        requests.Session is not thread-safe, so each worker thread gets its
        own. All threads share the read-only token + instance URL.
        """
        sess = getattr(self._local, "session", None)
        if sess is None:
            sess = requests.Session()
            sess.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            })
            self._local.session = sess
        return sess

    def _latest_api_version(self) -> str:
        resp = self._session.get(f"{self.instance_url}/services/data/")
        resp.raise_for_status()
        return resp.json()[-1]["version"]

    # ----- core verbs --------------------------------------------------------
    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, body: Any, *, retry: bool = True) -> Any:
        """POST ``body``. ``retry=False`` sends it once: for actions with no
        idempotency key, where a 5xx after the server committed would make a
        transport-level retry act twice. The caller decides what to do."""
        return self._request("POST", path, body, retry=retry)

    def patch(self, path: str, body: Any) -> Any:
        return self._request("PATCH", path, body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def query(self, soql: str) -> list[dict]:
        """Run a SOQL query and return ``records`` (REST query endpoint).

        The REST query endpoint does NOT support Apex bind syntax (``:var``);
        callers interpolate ids into the literal SOQL string. ``requests``
        URL-encodes the ``q`` param; the cli transport encodes it inline.
        """
        from urllib.parse import quote

        path = f"/services/data/v{self.api_version}/query?q={quote(soql)}"
        result = self._request("GET", path)
        records = []
        while isinstance(result, dict):
            records.extend(result.get("records", []))
            next_page = result.get("nextRecordsUrl")
            if not next_page:
                break
            result = self._request("GET", next_page)
        return records

    # ----- transport dispatch ------------------------------------------------
    def _request(self, method: str, path: str, body: Any = None, *, retry: bool = True) -> Any:
        path = self._normalize_path(path)
        if self.transport == "cli":
            return self._request_cli(method, path, body)
        return self._request_requests(method, path, body, retry=retry)

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Reduce ``path`` to a service-relative path (``/services/...``).

        Some responses hand back an absolute URL (e.g. post's ``statusURL``)
        rather than the relative form the rest of the tool passes. Both
        transports assume relative: ``requests`` prepends ``instance_url`` and
        the cli transport feeds ``path`` straight to ``sf api request rest``.
        Strip any scheme+host so an absolute URL works through either transport.
        """
        if path.startswith(("http://", "https://")):
            from urllib.parse import urlsplit

            parts = urlsplit(path)
            return parts.path + (f"?{parts.query}" if parts.query else "")
        return path

    def _request_requests(
        self, method: str, path: str, body: Any, *, retry: bool = True
    ) -> Any:
        url = f"{self.instance_url}{path}"
        data = json.dumps(body) if body is not None else None
        last_exc: Optional[Exception] = None
        attempts = _MAX_RETRIES if retry else 1
        for attempt in range(attempts):
            try:
                resp = self._session.request(method, url, data=data)
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < attempts - 1:
                    self._sleep_backoff(attempt, reason=str(exc))
                continue
            if resp.status_code in _RETRYABLE_STATUS and attempt < attempts - 1:
                self._sleep_backoff(attempt, reason=f"HTTP {resp.status_code}")
                continue
            if not (200 <= resp.status_code < 300):
                raise SfApiError(resp.status_code, resp.text, method, path)
            return self._decode(resp.status_code, resp.text)
        raise SfApiError(-1, f"exhausted retries: {last_exc}", method, path)

    def _request_cli(self, method: str, path: str, body: Any) -> Any:
        """Fallback transport: ``sf api request rest`` makes the call for us.

        Our process never handles a token here. ``--include`` makes the CLI
        print the HTTP status line and headers ahead of the body, so a
        non-2xx surfaces as ``SfApiError`` with the real HTTP status (a 400
        refusal and a 503 are told apart exactly as on the ``requests``
        transport) and the bare response body. A failure that never reached
        the API (no status line: auth, CLI error) keeps the CLI exit code as
        ``status``, which is outside every HTTP range.
        """
        args = [
            "sf", "api", "request", "rest", path, "--target-org", self.alias, "--include",
        ]
        tmp = None
        if method != "GET":
            args += ["--method", method]
        if body is not None:
            tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
            json.dump(body, tmp)
            tmp.flush()
            tmp.close()
            args += ["--body", f"@{tmp.name}"]
        try:
            proc = subprocess.run(args, capture_output=True, text=True)
        finally:
            if tmp is not None:
                os.unlink(tmp.name)
        status, text = parse_cli_response(proc.stdout)
        if status is None:
            if proc.returncode != 0:
                raise SfApiError(
                    proc.returncode, proc.stderr.strip() or text, method, path
                )
            return self._decode(200, text)
        if not (200 <= status < 300):
            raise SfApiError(status, text, method, path)
        return self._decode(status, text)

    # ----- metadata read (BillingSettings) -----------------------------------
    def read_billing_settings_xml(self) -> Optional[str]:
        """The org's ``BillingSettings`` XML, or ``None`` when unreadable.

        There is no REST read for it. ``requests``: Metadata SOAP
        ``readMetadata`` through this thread's session (the SOAP API takes the
        session only inside the envelope, not as a bearer header -- measured
        2026-11-25: ``INVALID_SESSION_ID``). ``cli``: ``sf project retrieve
        start --metadata Settings:Billing`` into a temporary directory, so our
        process never handles a token (works outside an sfdx project).
        """
        if self.transport == "cli":
            return self._read_billing_settings_cli()
        resp = self._session.post(
            f"{self.instance_url}/services/Soap/m/{self.api_version}",
            data=_BILLING_SETTINGS_SOAP.format(session=self.access_token).encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": '""'},
            timeout=60,
        )
        if resp.status_code != 200:
            log.warning("BillingSettings read returned HTTP %s", resp.status_code)
            return None
        return resp.text

    def _read_billing_settings_cli(self) -> Optional[str]:
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            # ``--wait`` (minutes) bounds sf's own polling (33 min by default);
            # the subprocess timeout bounds everything else. The caller holds
            # the per-org level lock, so this must never hang.
            try:
                proc = subprocess.run(
                    ["sf", "project", "retrieve", "start", "--metadata", "Settings:Billing",
                     "--target-metadata-dir", tmp, "--unzip", "--target-org", self.alias,
                     "--wait", str(_RETRIEVE_WAIT_MINUTES), "--json"],
                    capture_output=True, text=True, timeout=_RETRIEVE_TIMEOUT_S,
                )
            except subprocess.TimeoutExpired:
                log.warning("BillingSettings retrieve timed out after %ss",
                            _RETRIEVE_TIMEOUT_S)
                return None
            if proc.returncode != 0:
                log.warning("BillingSettings retrieve failed: %s",
                            (proc.stderr or proc.stdout).strip()[:300])
                return None
            found = list(Path(tmp).rglob("Billing.settings"))
            return found[0].read_text(encoding="utf-8") if found else None

    # ----- helpers -----------------------------------------------------------
    @staticmethod
    def _decode(status: int, text: str) -> Any:
        """Decode a 2xx body. PATCH/DELETE return 204 + empty body (success).

        CONTRACTS.md gotcha: activation/tagging PATCHes succeed with an empty
        2xx body -- treat empty as success, do not JSON-parse it.
        """
        if not text or not text.strip():
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"_raw": text}

    @staticmethod
    def _sleep_backoff(attempt: int, reason: str) -> None:
        delay = _BACKOFF_BASE * (2 ** attempt)
        log.warning("retrying after %.1fs (attempt %d): %s", delay, attempt + 1, reason)
        time.sleep(delay)
