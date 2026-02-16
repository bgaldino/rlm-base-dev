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


def get_chrome_driver_path():
    """Return the path to the ChromeDriver executable.

    Uses webdriver-manager if available; otherwise returns None so the
    caller can fall back to the default (system PATH) ChromeDriver.
    """
    if _HAS_WDM:
        return ChromeDriverManager().install()
    return None
