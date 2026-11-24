"""AnalyticsSetupHelper — Robot Framework keyword library for Analytics Setup page.

In Release 262+ (Summer '26), the Analytics Settings VF iframe page
(InsightsSetupSettings/waveSetupSettings.apexp) was removed. CRM Analytics is
now enabled via the "Enable CRM Analytics" button on the Getting Started page:
  /lightning/setup/InsightsSetupGettingStarted/home

Everything here runs as in-page JavaScript that walks shadow roots. No WebDriver
element lookup (``find_element``, ``WebDriverWait``, XPath) is used, on purpose:
on Release 264 orgs Lightning Setup is served from ``*.my.salesforce-setup.com``
and the Getting Started content is out of XPath's reach (``document.evaluate``
finds no button there), and under Chrome/ChromeDriver 158 a WebDriver XPath
lookup on Setup pages either misses or raises ``StaleElementReferenceException``.
``WebDriverWait`` ignores only ``NoSuchElementException``, so an XPath wait
aborted before any fallback ran (measured 2026-11-24 on a fresh 264 scratch
org; tests/test_analytics_setup_helper.py pins the behaviour).

Usage in robot file:
    Library    ../../resources/AnalyticsSetupHelper.py
"""

import time

from selenium.common.exceptions import WebDriverException
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

_SHADOW_WALK_JS = """
    function collect(root, out) {
        var nodes = root.querySelectorAll('button, a, input[type="button"], input[type="submit"]');
        for (var i = 0; i < nodes.length; i++) out.push(nodes[i]);
        var all = root.querySelectorAll('*');
        for (var j = 0; j < all.length; j++) {
            if (all[j].shadowRoot) collect(all[j].shadowRoot, out);
        }
        return out;
    }
    function label(el) {
        return (el.textContent || el.value || '').replace(/\\s+/g, ' ').trim();
    }
"""

# Reports what the Getting Started page currently shows: "enable" (the Enable CRM Analytics
# button is there), "launch" (CRM Analytics is on, so the page offers Launch CRM Analytics),
# or "none" (not rendered yet).
_PAGE_STATE_JS = "return (function() {" + _SHADOW_WALK_JS + """
    var els = collect(document, []);
    var launch = false;
    for (var i = 0; i < els.length; i++) {
        var text = label(els[i]);
        if (text === 'Enable CRM Analytics') return 'enable';
        if (text.indexOf('Launch CRM Analytics') === 0) launch = true;
    }
    return launch ? 'launch' : 'none';
})();
"""

# Finds and clicks the Enable button in one call, so no element handle can go stale between
# the lookup and the click. Returns "clicked" or "not_found".
_CLICK_ENABLE_JS = "return (function() {" + _SHADOW_WALK_JS + """
    var els = collect(document, []);
    for (var i = 0; i < els.length; i++) {
        if (label(els[i]) === 'Enable CRM Analytics') { els[i].click(); return 'clicked'; }
    }
    return 'not_found';
})();
"""


class AnalyticsSetupHelper:
    """Keyword library for enabling CRM Analytics via the Getting Started page."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    BUTTON_LABEL = "Enable CRM Analytics"
    BUTTON_WAIT_S = 30
    POST_CLICK_WAIT_S = 60
    POLL_S = 1
    # An org with CRM Analytics already on renders the Enable button for ~0.5-1 s while
    # the page loads, then replaces it with Launch CRM Analytics (measured 2026-11-24 on
    # 264, every load, Chrome 157 and 158). Enable counts only once it has held this long.
    ENABLE_SETTLE_S = 3

    @property
    def _driver(self):
        selib = BuiltIn().get_library_instance("SeleniumLibrary")
        return selib.driver

    def _page_state(self, driver):
        try:
            return driver.execute_script(_PAGE_STATE_JS)
        except WebDriverException:
            # The page is still moving to the Setup domain; read it again on the next poll.
            return "none"

    def _wait_for_state(self, driver, wanted, timeout):
        deadline = time.monotonic() + timeout
        while True:
            state = self._page_state(driver)
            if state in wanted:
                return state
            if time.monotonic() >= deadline:
                return state
            time.sleep(self.POLL_S)

    def _settled_state(self, driver):
        """'launch' as soon as the page shows it; 'enable' only once the Enable button has
        stayed, with no Launch, for ENABLE_SETTLE_S; otherwise the last state read when
        BUTTON_WAIT_S runs out. Only a non-Enable read checks the deadline, so an Enable first
        read at or after it (up to the first read past it) still gets its full settle."""
        deadline = time.monotonic() + self.BUTTON_WAIT_S
        enable_since = None
        while True:
            state = self._page_state(driver)
            now = time.monotonic()
            if state == "launch":
                return state
            if state == "enable":
                if enable_since is None:
                    enable_since = now
                if now - enable_since >= self.ENABLE_SETTLE_S:
                    return state
            else:
                enable_since = None  # re-rendered: the Enable button must hold again
                if now >= deadline:
                    return state
            time.sleep(self.POLL_S)

    @keyword
    def enable_crm_analytics_via_getting_started_page(self):
        """Click 'Enable CRM Analytics' on the Analytics Getting Started page.

        Polls the page (main DOM and shadow DOM) until it shows the Launch CRM
        Analytics button (already on) or the Enable button has held for
        ENABLE_SETTLE_S, so the Enable button an enabled org renders while loading
        is never clicked.

        Returns:
            'already_enabled'  — the page shows CRM Analytics is already on.
            'clicked'          — the button was clicked and the page confirmed it.
        Raises:
            AssertionError     — the page showed neither state; the JS click found no
                                 button although the page still shows one; or the
                                 click (or a click the driver errored on) was not
                                 confirmed by the page.
        """
        log = BuiltIn().log
        driver = self._driver
        driver.switch_to.default_content()

        log(f"Waiting up to {self.BUTTON_WAIT_S}s (plus a {self.ENABLE_SETTLE_S}s settle) for the "
            "Getting Started page...")
        state = self._settled_state(driver)
        if state == "launch":
            log("CRM Analytics is already enabled (page offers Launch CRM Analytics).")
            return "already_enabled"
        if state != "enable":
            raise AssertionError(
                f"The Analytics Getting Started page neither held '{self.BUTTON_LABEL}' for "
                f"{self.ENABLE_SETTLE_S}s nor showed 'Launch CRM Analytics' within {self.BUTTON_WAIT_S}s."
            )

        log(f"'{self.BUTTON_LABEL}' held for {self.ENABLE_SETTLE_S}s; clicking via JS...")
        driver_error = ""
        try:
            clicked = driver.execute_script(_CLICK_ENABLE_JS)
        except WebDriverException as exc:
            # The script may have clicked before the driver failed: let the page decide below.
            # Only the exception type is recorded: driver messages can echo page URLs.
            clicked, driver_error = "unknown", type(exc).__name__
            log(f"Driver raised {driver_error} during the click; checking the page.", "WARN")
        if clicked == "not_found":
            # It re-rendered between the read and the click: read the page again.
            state = self._settled_state(driver)
            if state == "launch":
                log("CRM Analytics is already enabled (page offers Launch CRM Analytics).")
                return "already_enabled"
            if state == "enable":
                raise AssertionError(f"'{self.BUTTON_LABEL}' is on the page but the JS click could not "
                                     "find it (it re-rendered at click time).")
            raise AssertionError(f"'{self.BUTTON_LABEL}' disappeared before it could be clicked.")

        log(f"Waiting up to {self.POST_CLICK_WAIT_S}s for the page to confirm...")
        if self._wait_for_state(driver, ("launch",), self.POST_CLICK_WAIT_S) != "launch":
            attempt = ("Clicked" if clicked == "clicked"
                       else f"The driver raised {driver_error} while clicking")
            raise AssertionError(
                f"{attempt} '{self.BUTTON_LABEL}' and the page did not confirm within "
                f"{self.POST_CLICK_WAIT_S}s (no 'Launch CRM Analytics')."
            )
        log("CRM Analytics enabled successfully.")
        return "clicked"
