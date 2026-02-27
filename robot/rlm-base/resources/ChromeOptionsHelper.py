"""Helper library for creating Chrome options for headless execution.

Used by default for CCI robot tasks (e.g. enable_document_builder, enable_constraints_settings,
configure_revenue_settings). Set BROWSER to use a different browser (e.g. firefox).
"""

from selenium import webdriver


def get_headless_chrome_options():
    """Create and return Chrome options configured for headless execution.

    Returns:
        selenium.webdriver.ChromeOptions: Configured options object
    """
    options = webdriver.ChromeOptions()

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
