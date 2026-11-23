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
with every session-bearing URL redacted, so a failure message cannot leak it
either. Only the org alias and the setup path (no token) are ever visible.

``SESSION_URL_PATTERN`` is the same pattern the regression test scans results
for (``tests/test_robot_session_url_logging.py``).
"""

import re
import subprocess

from robot.api import logger
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

# A frontdoor path, or a sid=/otp= query parameter (also catches URL-encoded forms).
SESSION_URL_PATTERN = re.compile(
    r"secur/frontdoor\.jsp|[?&;](?:sid|otp)=|(?:^|[\s\"'(])(?:sid|otp)=[^\s&\"']{6,}",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_URL_MARKER = "with the following URL:"
REDACTED = "<session-url-redacted>"


def redact_session_urls(text):
    """Replace every URL in ``text`` that carries session material."""
    text = str(text)
    return _URL_RE.sub(
        lambda m: REDACTED if SESSION_URL_PATTERN.search(m.group(0)) else m.group(0),
        text,
    )


def _parse_url(stdout):
    raw = " ".join(str(stdout).split())
    return raw.split(_URL_MARKER)[-1].strip() if _URL_MARKER in raw else raw


@library(scope="GLOBAL", auto_keywords=False)
class SessionUrlGuard:
    @keyword("Go To Authenticated Page")
    def go_to_authenticated_page(self, org_alias, setup_path):
        """Opens ``setup_path`` in the current browser, logged in to ``org_alias``.

        Fetches a one-time frontdoor URL with ``sf org open --url-only`` and
        navigates to it. The URL is never visible to Robot (see the module doc).
        Fails with a redacted message if the CLI or the navigation fails.
        """
        if not str(org_alias).strip():
            raise AssertionError("ORG_ALIAS must be set (e.g. robot -v ORG_ALIAS:my-scratch ...)")
        logger.info(f"Opening {setup_path} in org {org_alias} through an authenticated session (URL not logged).")
        builtin = BuiltIn()
        previous = builtin.set_log_level("NONE")
        failure = None
        try:
            url = self._fetch_url(org_alias, setup_path)
            driver = builtin.get_library_instance("SeleniumLibrary").driver
            driver.get(url)
        except Exception as exc:  # re-raised below with the level restored
            failure = f"{type(exc).__name__}: {redact_session_urls(exc)}"
        finally:
            builtin.set_log_level(previous)
        if failure is not None:
            raise AssertionError(failure)

    @staticmethod
    def _fetch_url(org_alias, setup_path):
        result = subprocess.run(
            ["sf", "org", "open", "-o", str(org_alias), "--url-only", "-p", str(setup_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"sf org open failed (exit {result.returncode}): {result.stderr.strip()}")
        url = _parse_url(result.stdout)
        if not url:
            raise RuntimeError("sf org open did not return a URL")
        return url
