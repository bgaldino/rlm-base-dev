"""Helper library for creating Chrome options for headless and visible execution.

Used by default for CCI robot tasks (e.g. enable_document_builder, enable_constraints_settings,
configure_revenue_settings). Set BROWSER to use a different browser (e.g. firefox).

Set CHROME_BINARY to launch an alternate Chrome executable (e.g. Chrome for
Testing) instead of the stock install; CHROME_BIN (used by CI/Docker) is the
fallback. Pair it with CHROMEDRIVER_PATH (see WebDriverManager.py) so the
driver matches that binary's version.
"""

import os

from selenium import webdriver


def get_headless_chrome_options():
    """Create and return Chrome options configured for headless execution.

    Returns:
        selenium.webdriver.ChromeOptions: Configured options object
    """
    options = webdriver.ChromeOptions()

    chrome_binary = os.environ.get('CHROME_BINARY') or os.environ.get('CHROME_BIN')
    if chrome_binary:
        options.binary_location = chrome_binary

    # Required for headless
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # Additional stability options
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')

    return options

