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

    Prefers system ChromeDriver (/usr/bin/chromedriver) when available
    (e.g., in CI or when chromium-driver is installed). Falls back to
    webdriver-manager for automatic driver management, or returns None
    to use system PATH as a last resort.
    """
    import os
    import shutil

    # Check for system ChromeDriver first
    system_chromedriver = "/usr/bin/chromedriver"
    if os.path.isfile(system_chromedriver) and os.access(system_chromedriver, os.X_OK):
        _logger.debug(f"Using system ChromeDriver: {system_chromedriver}")
        return system_chromedriver

    # Try PATH-based chromedriver
    path_chromedriver = shutil.which("chromedriver")
    if path_chromedriver:
        _logger.debug(f"Using ChromeDriver from PATH: {path_chromedriver}")
        return path_chromedriver

    # Fall back to webdriver-manager
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
