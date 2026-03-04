"""Helper library for creating Chrome options for headless and visible execution.

Used by default for CCI robot tasks (e.g. enable_document_builder, enable_constraints_settings,
configure_revenue_settings). Set BROWSER to use a different browser (e.g. firefox).
Set HEADLESS to false for visible browser debugging (e.g. robot -v HEADLESS:false ...).

Requirements:
    - Chrome/Chromium 109+ (December 2022) for --headless=new flag
    - Check version: google-chrome --version or chromium --version
"""

from selenium import webdriver


def get_chrome_options(headless=True):
    """Create and return Chrome options, optionally headless.

    Args:
        headless: If True (or "True", "true", "1"), add --headless=new for headless
            execution. If False (or "False", "false", "0"), run with visible browser
            (useful for debugging). Accepts strings from Robot Framework variables.

    Returns:
        selenium.webdriver.ChromeOptions: Configured options object
    """
    options = webdriver.ChromeOptions()

    # Robot passes strings; normalize to bool for portability
    is_headless = str(headless).lower() not in ('false', '0', 'no', '')
    if is_headless:
        options.add_argument('--headless=new')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')

    return options


def get_headless_chrome_options():
    """Create and return Chrome options configured for headless execution.

    Backward-compatible wrapper; calls get_chrome_options(headless=True).

    Returns:
        selenium.webdriver.ChromeOptions: Configured options object
    """
    return get_chrome_options(headless=True)
