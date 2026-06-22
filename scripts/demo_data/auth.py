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
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

log = logging.getLogger("demo_data.auth")

DEFAULT_API_VERSION = "67.0"  # v262 baseline; do not silently float to latest.

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
            f"`{' '.join(cmd)}` failed (exit {proc.returncode}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SfCliError(f"`{' '.join(cmd)}` returned non-JSON: {proc.stdout[:300]}") from exc
    return payload.get("result", {})


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


@dataclass
class SfRestClient:
    """Transport-agnostic Salesforce REST client.

    Construct via :meth:`from_alias`. All paths are absolute service paths
    (e.g. ``/services/data/v67.0/sobjects/Order/<id>``); ``query`` builds the
    query path for you.
    """

    alias: str
    access_token: str
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

    def post(self, path: str, body: Any) -> Any:
        return self._request("POST", path, body)

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
        return result.get("records", []) if isinstance(result, dict) else []

    # ----- transport dispatch ------------------------------------------------
    def _request(self, method: str, path: str, body: Any = None) -> Any:
        path = self._normalize_path(path)
        if self.transport == "cli":
            return self._request_cli(method, path, body)
        return self._request_requests(method, path, body)

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

    def _request_requests(self, method: str, path: str, body: Any) -> Any:
        url = f"{self.instance_url}{path}"
        data = json.dumps(body) if body is not None else None
        last_exc: Optional[Exception] = None
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.request(method, url, data=data)
            except requests.RequestException as exc:
                last_exc = exc
                self._sleep_backoff(attempt, reason=str(exc))
                continue
            if resp.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES - 1:
                self._sleep_backoff(attempt, reason=f"HTTP {resp.status_code}")
                continue
            if not (200 <= resp.status_code < 300):
                raise SfApiError(resp.status_code, resp.text, method, path)
            return self._decode(resp.status_code, resp.text)
        raise SfApiError(-1, f"exhausted retries: {last_exc}", method, path)

    def _request_cli(self, method: str, path: str, body: Any) -> Any:
        """Fallback transport: ``sf api request rest`` makes the call for us.

        Our process never handles a token here. Non-2xx is reported by the CLI
        on stderr / non-zero exit; we surface it as SfApiError.
        """
        args = ["sf", "api", "request", "rest", path, "--target-org", self.alias]
        tmp = None
        if method != "GET":
            args += ["--method", method]
        if body is not None:
            tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
            json.dump(body, tmp)
            tmp.flush()
            args += ["--body", f"@{tmp.name}"]
        proc = subprocess.run(args, capture_output=True, text=True)
        out = proc.stdout.strip()
        if proc.returncode != 0:
            raise SfApiError(
                proc.returncode, proc.stderr.strip() or out, method, path
            )
        return self._decode(200, out)

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
