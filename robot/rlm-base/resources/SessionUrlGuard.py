"""Robot Framework library: authenticated Salesforce navigation without logging the session.

``sf org open --url-only`` prints a frontdoor URL that carries a live session
(``secur/frontdoor.jsp?sid=...``). Robot records keyword arguments, return
values, library log messages and failure text in ``output.xml`` and ``log.html``,
so a URL that passes through a Robot variable or a SeleniumLibrary ``Go To`` is
written to disk. This library keeps the URL inside Python for its whole life:
it is fetched, used for one ``driver.get`` and dropped. It is never returned to
Robot, never passed as a keyword argument and never logged.

While the URL exists the Robot log level is ``NONE`` (the prior level is always
restored in ``finally``), and any exception raised from that window is rewritten
with the known URL, its ``sid``/``otp`` values and every other session-bearing
URL redacted. If the pattern still matches afterwards the whole message is
withheld. Only the org alias and the setup path (no token) are ever visible.

The same applies to reading the current page URL (``Get Record Id From Current
Url``, ``Current Url Should Be Record Page``): the page URL can be a frontdoor
URL while a login redirect is in flight, so it is read with logging off and only
its path is ever reported.

``SESSION_URL_PATTERN`` is the pattern the regression scanner uses
(``scripts/ai/check_robot_session_urls.py``; ``tests/test_robot_session_url_logging.py``).
"""

import json
import re
import shutil
import subprocess
from urllib.parse import parse_qsl, quote, unquote, urlsplit

from robot.api import logger
from robot.api.deco import keyword, library
from robot.errors import RobotError
from robot.libraries.BuiltIn import BuiltIn

# A frontdoor path, a sid=/otp= parameter (query, cookie or bare, plain / URL-encoded / double
# encoded), or a raw session id. The session-id shape is `00D` + 12 or 15 more org-id characters,
# `!`, then a 20+ character token of letters, digits, `.` and `_` (inferred from Salesforce session
# ids; the token alphabet and length are not measured here).
SESSION_URL_PATTERN = re.compile(
    r"secur(?:/|%2F|%252F)frontdoor\.jsp"
    r"|(?:[?&;]|%3F|%26|%25(?:3F|26))(?:sid|otp)(?:=|%3D|%253D)"
    r"|(?:^|[\s\"';(,])(?:sid|otp)="
    r"|\b00D[0-9A-Za-z]{12,15}![0-9A-Za-z._]{20,}",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
REDACTED = "<session-url-redacted>"
WITHHELD = "<message withheld: it may contain session material>"
_SF_TIMEOUT_SECONDS = 120
_RECORD_PATH_TEMPLATE = "/lightning/r/{sobject}/[a-zA-Z0-9]{{15,18}}"


def _secret_values(url):
    """The sid/otp values (and encoded forms) carried by ``url``."""
    values = set()
    query = urlsplit(str(url)).query
    for name, value in parse_qsl(query, keep_blank_values=False):
        if name.lower() in ("sid", "otp") and value:
            values.add(value)
    # parse_qsl turns '+' into a space; keep the raw values too.
    for part in query.replace(";", "&").split("&"):
        name, _, value = part.partition("=")
        if name.lower() in ("sid", "otp") and value:
            values.add(value)
    for value in list(values):
        values.update({quote(value, safe=""), quote(value), unquote(value)})
    return {v for v in values if v}


def redact_session_urls(text, known_url=None):
    """Remove session material from ``text``; withhold the whole text if any remains."""
    text = str(text)
    secrets = set()
    if known_url:
        known_url = str(known_url)
        secrets |= _secret_values(known_url)
        text = text.replace(known_url, REDACTED).replace(quote(known_url, safe=""), REDACTED)
    text = _URL_RE.sub(
        lambda m: REDACTED if SESSION_URL_PATTERN.search(m.group(0)) else m.group(0), text
    )
    # A leaked URL may have lost its scheme or been cut; look for any value we know.
    for secret in secrets:
        text = text.replace(secret, REDACTED)
    if SESSION_URL_PATTERN.search(text) or any(s in text for s in secrets):
        return WITHHELD
    return text


def _json_dict(text):
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _fetch_url(org_alias, setup_path):
    """Return the one-time frontdoor URL for ``setup_path``. Never log the result."""
    sf = shutil.which("sf")
    if sf is None:
        raise RuntimeError("the Salesforce CLI ('sf') was not found on PATH; install it or fix PATH")
    try:
        result = subprocess.run(
            [sf, "org", "open", "-o", str(org_alias), "--url-only", "-p", str(setup_path), "--json"],
            capture_output=True,
            text=True,
            timeout=_SF_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"sf org open timed out after {_SF_TIMEOUT_SECONDS}s") from None
    payload = _json_dict(result.stdout) or _json_dict(result.stderr)  # sf v2 writes error JSON to stderr
    if result.returncode != 0:
        detail = payload.get("message") or result.stderr.strip() or "no detail"
        raise RuntimeError(f"sf org open failed (exit {result.returncode}): {detail}")
    inner = payload.get("result")
    url = inner.get("url") if isinstance(inner, dict) else None
    if not url:
        raise RuntimeError("sf org open --json did not return result.url")
    return url


@library(scope="GLOBAL", auto_keywords=False)
class SessionUrlGuard:
    @keyword("Go To Authenticated Page")
    def go_to_authenticated_page(self, org_alias, setup_path):
        """Opens ``setup_path`` in the current browser, logged in to ``org_alias``.

        Fetches a one-time frontdoor URL with ``sf org open --url-only --json``
        and navigates to it. The URL is never visible to Robot (see the module
        doc). Fails with a redacted message if the CLI or the navigation fails.
        """
        if not str(org_alias).strip():
            raise AssertionError("ORG_ALIAS must be set (e.g. robot -v ORG_ALIAS:my-scratch ...)")
        logger.info(f"Opening {setup_path} in org {org_alias} through an authenticated session (URL not logged).")
        builtin = BuiltIn()
        previous = builtin.set_log_level("NONE")
        failure = None
        url = None
        try:
            url = _fetch_url(org_alias, setup_path)
            builtin.get_library_instance("SeleniumLibrary").driver.get(url)
        except RobotError:
            raise  # Robot's own control flow (timeouts, missing library): never rewrite or swallow
        except Exception as exc:  # re-raised below, redacted, with the level restored
            failure = f"{type(exc).__name__}: {redact_session_urls(exc, url)}"
        finally:
            builtin.set_log_level(previous)
        if failure is not None:
            raise AssertionError(failure)

    def _current_url(self):
        builtin = BuiltIn()
        previous = builtin.set_log_level("NONE")
        try:
            return builtin.get_library_instance("SeleniumLibrary").driver.current_url
        finally:
            builtin.set_log_level(previous)

    @keyword("Get Record Id From Current Url")
    def get_record_id_from_current_url(self):
        """Returns the 15-18 character record Id in the current page URL, or an empty string.

        The URL is read and matched with logging off and is never returned or logged.
        """
        path = urlsplit(self._current_url()).path
        for pattern in (r"/([a-zA-Z0-9]{15,18})/view", r"/([a-zA-Z0-9]{15,18})$"):
            found = re.search(pattern, path)
            if found:
                return found.group(1)
        return ""

    @keyword("Current Url Should Be Record Page")
    def current_url_should_be_record_page(self, sobject):
        """Fails unless the current page is ``/lightning/r/<sobject>/<id>``. Reports the path only."""
        path = urlsplit(self._current_url()).path
        if not re.search(_RECORD_PATH_TEMPLATE.format(sobject=re.escape(str(sobject))), path):
            raise AssertionError(
                f"Current page is not a {sobject} record page (path: {redact_session_urls(path)})"
            )
