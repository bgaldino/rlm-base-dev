"""Robot Framework library that provides ChromeDriver path via webdriver-manager.

When webdriver-manager is installed, it downloads and manages ChromeDriver
automatically. When it is not installed, falls back to the system ChromeDriver
(i.e. whatever is on PATH), which is the standard SeleniumLibrary behaviour.

Also patches Selenium 3.x's RemoteConnection to use a urllib3 2.x-compatible
timeout value (Selenium 3.x passes ``socket._GLOBAL_DEFAULT_TIMEOUT``, a sentinel
``object()``, which urllib3 2.x rejects).

To install: pip install webdriver-manager
  (or: pipx inject cumulusci webdriver-manager)
"""

import logging
import socket

_HAS_WDM = True
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    _HAS_WDM = False

_logger = logging.getLogger(__name__)


def _patch_selenium_timeout():
    """Replace Selenium 3.x's sentinel timeout with None for urllib3 2.x compat.

    Selenium 3.x sets ``RemoteConnection._timeout = socket._GLOBAL_DEFAULT_TIMEOUT``
    and passes it directly to ``urllib3.PoolManager(timeout=...)``.  urllib3 1.x
    silently accepted sentinel objects; urllib3 2.x validates and raises ValueError.
    Converting to ``None`` preserves the "use OS default" semantics while satisfying
    urllib3 2.x's type check.
    """
    try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection

        if getattr(RemoteConnection, "_timeout", None) is socket._GLOBAL_DEFAULT_TIMEOUT:
            RemoteConnection._timeout = None
            _logger.debug("Patched RemoteConnection._timeout for urllib3 2.x compatibility")
    except ImportError:
        pass


_patch_selenium_timeout()


def get_chrome_driver_path():
    """Return the path to the ChromeDriver executable.

    Uses webdriver-manager if available; otherwise returns None so the
    caller can fall back to the default (system PATH) ChromeDriver.
    """
    if not _HAS_WDM:
        return None

    try:
        return ChromeDriverManager().install()
    except Exception:
        _logger.warning(
            "webdriver-manager: ChromeDriverManager().install() failed. "
            "Falling back to system ChromeDriver on PATH.",
            exc_info=True,
        )
        return None
