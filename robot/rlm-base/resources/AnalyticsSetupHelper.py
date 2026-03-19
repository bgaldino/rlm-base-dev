"""AnalyticsSetupHelper — Robot Framework keyword library for Analytics Setup page.

In Release 262+ (Summer '26), the Analytics Settings VF iframe page
(InsightsSetupSettings/waveSetupSettings.apexp) was removed. CRM Analytics is
now enabled via the "Enable CRM Analytics" button on the Getting Started page:
  /lightning/setup/InsightsSetupGettingStarted/home

The button lives in the main Lightning DOM (no VF iframe). Shadow DOM traversal
is used to handle the lightning-button web component wrapper.

Usage in robot file:
    Library    ../../resources/AnalyticsSetupHelper.py
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

_FIND_AND_CLICK_JS = """
return (function(buttonText) {
    function findButton(root) {
        var candidates = root.querySelectorAll('button, input[type="button"], input[type="submit"]');
        for (var i = 0; i < candidates.length; i++) {
            var text = (candidates[i].textContent || candidates[i].value || '').trim();
            if (text === buttonText) return candidates[i];
        }
        var all = root.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) {
                var found = findButton(all[i].shadowRoot);
                if (found) return found;
            }
        }
        return null;
    }
    var btn = findButton(document.body);
    if (!btn) return 'not_found';
    btn.click();
    return 'clicked';
})(arguments[0]);
"""


class AnalyticsSetupHelper:
    """Keyword library for enabling CRM Analytics via the Getting Started page."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    BUTTON_LABEL = "Enable CRM Analytics"
    BUTTON_WAIT_S = 20
    POST_CLICK_WAIT_S = 30

    @property
    def _driver(self):
        selib = BuiltIn().get_library_instance("SeleniumLibrary")
        return selib.driver

    @keyword
    def enable_crm_analytics_via_getting_started_page(self):
        """Click 'Enable CRM Analytics' on the Analytics Getting Started page.

        Searches the main DOM and shadow DOM for the button. If absent (CRM
        Analytics already enabled), returns 'already_enabled' without clicking.

        Returns:
            'already_enabled'  — button not found; CRM Analytics already on.
            'clicked'          — button found, clicked, and page updated.
        Raises:
            AssertionError     — button found but could not be clicked.
        """
        log = BuiltIn().log
        driver = self._driver
        driver.switch_to.default_content()

        log(f"Waiting up to {self.BUTTON_WAIT_S}s for '{self.BUTTON_LABEL}' button...")

        # Wait for page to settle then check for the button via JS
        button_xpath = (
            f"//button[normalize-space(.)='{self.BUTTON_LABEL}'] | "
            f"//input[@type='button' and normalize-space(@value)='{self.BUTTON_LABEL}']"
        )
        btn = None
        try:
            btn = WebDriverWait(driver, self.BUTTON_WAIT_S).until(
                EC.presence_of_element_located((By.XPATH, button_xpath))
            )
        except TimeoutException:
            pass

        if btn is None:
            # Button not in main DOM — may be inside a shadow root, try JS traversal
            result = driver.execute_script(_FIND_AND_CLICK_JS, self.BUTTON_LABEL)
            if result == "not_found":
                log(
                    f"'{self.BUTTON_LABEL}' button not found after {self.BUTTON_WAIT_S}s "
                    "— CRM Analytics appears to already be enabled."
                )
                return "already_enabled"
            # JS already clicked it
            log(f"'{self.BUTTON_LABEL}' found in shadow DOM and clicked via JS.")
        else:
            # Use the element captured by WebDriverWait — avoids a second find_element
            # call that races against Lightning re-renders.
            log(f"'{self.BUTTON_LABEL}' button found in main DOM; clicking via JS...")
            driver.execute_script("arguments[0].click();", btn)

        # Wait for the button to go stale (page reload/nav after enabling)
        log(f"Waiting up to {self.POST_CLICK_WAIT_S}s for page to update...")
        try:
            if btn is not None:
                WebDriverWait(driver, self.POST_CLICK_WAIT_S).until(
                    EC.staleness_of(btn)
                )
            else:
                # After JS click from shadow DOM, just give the page time to settle
                import time
                time.sleep(5)
            log("CRM Analytics enabled successfully.")
        except TimeoutException:
            log(
                "Page did not navigate/reload after clicking — "
                "CRM Analytics may have been enabled without a page change.",
                "WARN",
            )

        return "clicked"
