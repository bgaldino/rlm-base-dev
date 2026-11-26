"""Helper library for creating Chrome options for headless and visible execution.

Used by default for CCI robot tasks (e.g. enable_document_builder, enable_constraints_settings,
configure_revenue_settings). Set BROWSER to use a different browser (e.g. firefox).

Set CHROME_BINARY to launch an alternate Chrome executable (e.g. Chrome for
Testing) instead of the stock install; CHROME_BIN (used by CI/Docker) is the
fallback. Pair it with CHROMEDRIVER_PATH (see WebDriverManager.py) so the
driver matches that binary's version.

``Allow Synthetic Shadow Element References`` must run right after ``Create
Webdriver``: without it, ChromeDriver 158+ reports every element inside an LWC
synthetic shadow tree as stale (see its docstring).
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


# ChromeDriver 158 (verified through 159) checks that an element it hands to or
# receives from the page is still attached by walking up with
# ``root instanceof ShadowRootConstructor``, where
# ``ShadowRootConstructor = window.cdc_adoQpoasnfa76pfcZLmcfl_ShadowRoot || window.ShadowRoot``
# is a copy of ``window.ShadowRoot`` saved by its document-start script. Lightning
# pages load LWC synthetic shadow afterwards, which replaces ``window.ShadowRoot``
# and gives every synthetic shadow tree a root that is an instance of the
# replacement only. The saved native copy rejects those roots, so each element in
# a synthetic shadow tree reads as detached: an XPath lookup whose matches include
# one (text XPaths and ``//button`` on Setup pages) and a script returning one both
# raise StaleElementReferenceException. CSS lookups are unaffected because LWC's
# patched querySelectorAll never returns those elements. ChromeDriver 157 read
# ``window.ShadowRoot`` at call time. This script, registered for every new
# document, makes the saved copy read ``window.ShadowRoot`` at call time again. It
# also covers a different key after ``cdc_``, by matching ``cdc_<key>_ShadowRoot``
# among the window's own properties (ChromeDriver's script is registered first, so
# it has run when this one does). It cannot tell whether the redefinition took: a
# driver that saved the copy as a non-configurable property, or under another name,
# would bring the stale errors back, and the error text is the signal.
_SYNTHETIC_SHADOW_SHIM = (
    "(function () {"
    " var known = 'cdc_adoQpoasnfa76pfcZLmcfl_ShadowRoot';"
    " var names = Object.getOwnPropertyNames(window).filter(function (n) {"
    " return /^cdc_[A-Za-z0-9]+_ShadowRoot$/.test(n); });"
    " if (names.indexOf(known) < 0) { names.push(known); }"
    " names.forEach(function (name) {"
    " try { Object.defineProperty(window, name, {configurable: true, enumerable: false,"
    " get: function () { return window.ShadowRoot; }, set: function () {}}); } catch (e) {}"
    " });"
    "})();"
)


def allow_synthetic_shadow_element_references():
    """Lets ChromeDriver 158+ reference elements inside LWC synthetic shadow trees.

    Registers a script for every new document (CDP
    ``Page.addScriptToEvaluateOnNewDocument``) so ChromeDriver checks those
    elements against the page's own ``window.ShadowRoot``, as ChromeDriver 157
    did; see the comment above ``_SYNTHETIC_SHADOW_SHIM``. Run it once per
    browser, right after ``Create Webdriver`` and before the first navigation.
    It is a no-op for a driver without CDP (Firefox) and changes nothing on
    ChromeDriver 157 or on pages without synthetic shadow. A CDP failure is
    logged as a warning naming the exception type, not raised: the session
    still works for CSS and JavaScript lookups.

    Returns ``installed`` or ``skipped`` (no CDP, or the CDP call failed).
    """
    from robot.api import logger
    from robot.libraries.BuiltIn import BuiltIn

    driver = BuiltIn().get_library_instance("SeleniumLibrary").driver
    execute_cdp_cmd = getattr(driver, "execute_cdp_cmd", None)
    if execute_cdp_cmd is None:
        logger.info("Browser has no CDP; synthetic shadow reference fix not needed.")
        return "skipped"
    try:
        execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": _SYNTHETIC_SHADOW_SHIM})
    except Exception as exc:  # noqa: BLE001 - any CDP failure leaves the old behaviour
        logger.warn(
            "Could not register the synthetic shadow reference fix "
            f"({type(exc).__name__}); XPath lookups on Lightning pages may raise "
            "StaleElementReferenceException under ChromeDriver 158+."
        )
        return "skipped"
    logger.info("Registered the synthetic shadow reference fix for ChromeDriver 158+ (applies to each new document).")
    return "installed"
