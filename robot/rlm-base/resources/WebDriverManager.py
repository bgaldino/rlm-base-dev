"""Robot Framework library that provides ChromeDriver path via webdriver-manager.

Use this so ChromeDriver does not need to be installed in PATH. Requires
webdriver-manager to be installed in the same environment as Robot (e.g.
pipx inject cumulusci webdriver-manager).
"""


def get_chrome_driver_path():
    """Return the path to the ChromeDriver executable (downloads if needed)."""
    from webdriver_manager.chrome import ChromeDriverManager

    return ChromeDriverManager().install()
