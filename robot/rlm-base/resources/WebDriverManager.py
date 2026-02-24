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


def _make_normalizing_session():
    """Return a requests.Session subclass instance that normalizes timeout values."""
    import requests

    class _NormalizingSession(requests.Session):
        def request(self, method, url, *args, **kwargs):
            if "timeout" in kwargs:
                kwargs["timeout"] = _normalize_timeout(kwargs["timeout"])
            return super().request(method, url, *args, **kwargs)

    return _NormalizingSession()


def get_chrome_driver_path():
    """Return the path to the ChromeDriver executable.

    Uses webdriver-manager if available; otherwise returns None so the
    caller can fall back to the default (system PATH) ChromeDriver.

    Coerces invalid timeout values (e.g. urllib3 2.x sentinels) by injecting
    a custom requests.Session into webdriver-manager's HTTP client. The patch
    is scoped to the single session instance used for the download, so it
    cannot affect other threads or concurrent HTTP calls.
    """
    if not _HAS_WDM:
        return None

    # Try to inject a normalizing session into webdriver-manager's HTTP client.
    # WDMHttpClient (wdm >= 3.x) exposes a `.session` attribute we can replace.
    try:
        import requests  # noqa: F401 — needed to build the session subclass
        from webdriver_manager.core.http import WDMHttpClient

        http_client = WDMHttpClient()
        http_client.session = _make_normalizing_session()
        return ChromeDriverManager(http_client=http_client).install()
    except (ImportError, TypeError, AttributeError):
        # WDMHttpClient or http_client kwarg unavailable in this wdm version;
        # fall back to a bare install (timeout normalisation best-effort only).
        return ChromeDriverManager().install()
