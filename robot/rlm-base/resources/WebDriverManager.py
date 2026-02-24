"""Robot Framework library that provides ChromeDriver path via webdriver-manager.

When webdriver-manager is installed, it downloads and manages ChromeDriver
automatically. When it is not installed, falls back to the system ChromeDriver
(i.e. whatever is on PATH), which is the standard SeleniumLibrary behaviour.

To install: pip install webdriver-manager
  (or: pipx inject cumulusci webdriver-manager)
"""

_HAS_WDM = True
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    _HAS_WDM = False


def _normalize_timeout(timeout):
    """Return a timeout valid for requests/urllib3 (int, float, None, or (connect, read) tuple)."""
    if timeout is None:
        return None
    if isinstance(timeout, (int, float)):
        return timeout
    if isinstance(timeout, tuple) and len(timeout) == 2:
        if all(isinstance(t, (int, float)) for t in timeout):
            return timeout
    return (10, 10)


def get_chrome_driver_path():
    """Return the path to the ChromeDriver executable.

    Uses webdriver-manager if available; otherwise returns None so the
    caller can fall back to the default (system PATH) ChromeDriver.
    When webdriver-manager is used, patches requests.Session.request to
    coerce invalid timeout values (e.g. from urllib3 2.x compatibility)
    so ChromeDriver download succeeds even if a dependency passes a sentinel.
    """
    if not _HAS_WDM:
        return None
    try:
        import requests
    except ImportError:
        return ChromeDriverManager().install()
    session_cls = getattr(requests, "Session", None)
    if session_cls is None:
        return ChromeDriverManager().install()
    original_request = session_cls.request

    def _patched_request(self, method, url, *args, **kwargs):
        if "timeout" in kwargs:
            kwargs["timeout"] = _normalize_timeout(kwargs["timeout"])
        return original_request(self, method, url, *args, **kwargs)

    session_cls.request = _patched_request
    try:
        return ChromeDriverManager().install()
    finally:
        session_cls.request = original_request
