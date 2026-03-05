"""AnalyticsSetupHelper — Robot Framework keyword library for Analytics Setup page.

The "Enable Data Sync and Connections" setting lives in a Visualforce iframe
(waveSetupSettings.apexp) embedded inside the Lightning setup shell at
/lightning/setup/InsightsSetupSettings/home.

The outer Lightning shell is protected by Lightning Web Security (LWS), which
blocks all standard querySelectorAll / XPath DOM queries from Selenium.  The
VF iframe content is NOT included in CDP DOM.getDocument (which only returns
the main frame's DOM).  Selenium's switch_to.frame + native WebDriver element
finding works correctly inside the VF page, which is standard HTML.

Usage in robot file:
    Library    ../../resources/AnalyticsSetupHelper.py
"""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    JavascriptException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class AnalyticsSetupHelper:
    """Keyword library for enabling Analytics settings in the VF iframe."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    TARGET_LABEL = "Enable Data Sync and Connections"

    # Centralised timeout constants (seconds) — tune here if org load times differ.
    IFRAME_WAIT_S = 30
    CHECKBOX_WAIT_S = 30
    SAVE_WAIT_S = 10

    @property
    def _driver(self):
        selib = BuiltIn().get_library_instance("SeleniumLibrary")
        return selib.driver

    @keyword
    def enable_data_sync_and_connections_via_vf_iframe(self):
        """Enable the 'Enable Data Sync and Connections' checkbox in the VF iframe.

        The Analytics Settings page embeds a Visualforce page (waveSetupSettings.apexp)
        in a child iframe.  This keyword:
          1. Waits for the VF iframe to appear (up to IFRAME_WAIT_S seconds).
          2. Switches Selenium into the VF iframe.
          3. Waits for checkboxes to appear in the VF page (up to CHECKBOX_WAIT_S seconds).
          4. Finds the checkbox associated with the 'Enable Data Sync and Connections' label.
          5. Clicks the checkbox if not already enabled.
          6. Clicks the Save button and waits for page reload to persist the setting.

        Always restores Selenium to the default (main) frame via try/finally.

        Returns:
            'already_enabled'  — checkbox was already checked; no action taken.
            'clicked'          — checkbox was found, enabled, and saved.
        Raises:
            AssertionError     — VF iframe, checkbox, or Save button not found.
        """
        log = BuiltIn().log
        driver = self._driver

        # ── Step 1: ensure we start in the main frame ──────────────────
        driver.switch_to.default_content()

        # ── Step 2: wait for the VF iframe ─────────────────────────────
        # vfFrameId is the deterministic name prefix assigned by Salesforce to
        # the Analytics settings VF iframe (e.g. vfFrameId_1772739916061).
        log("Waiting for VF iframe (waveSetupSettings.apexp) to appear...")
        iframe_xpath = "//iframe[contains(@name, 'vfFrameId')]"
        try:
            iframe_el = WebDriverWait(driver, self.IFRAME_WAIT_S).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )
        except TimeoutException:
            raise AssertionError(
                f"Analytics Settings VF iframe not found after {self.IFRAME_WAIT_S} s. "
                "Expected iframe with name attribute containing 'vfFrameId'."
            )
        log(f"VF iframe found: title={iframe_el.get_attribute('title')!r}")

        # ── Steps 3-7: switch frame; always restore context on exit ────
        driver.switch_to.frame(iframe_el)
        try:
            return self._interact_with_vf_page(driver, log)
        finally:
            driver.switch_to.default_content()

    # ── Private helpers ────────────────────────────────────────────────

    def _interact_with_vf_page(self, driver, log):
        """Perform checkbox find/click/save inside the already-switched VF iframe."""

        # ── Step 3: wait for checkboxes to appear ──────────────────────
        log("Waiting for checkboxes in VF page to appear...")
        try:
            WebDriverWait(driver, self.CHECKBOX_WAIT_S).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']"))
            )
        except TimeoutException:
            raise AssertionError(
                f"No checkboxes appeared in VF iframe after {self.CHECKBOX_WAIT_S} s. "
                f"Cannot locate '{self.TARGET_LABEL}'."
            )
        cbs = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        log(f"VF frame: WebDriver found {len(cbs)} checkbox(es)")

        # ── Step 4: find the target checkbox ───────────────────────────
        checkbox = self._find_checkbox_by_label(driver, cbs, log)

        # ── Step 5: check current state ────────────────────────────────
        is_checked = checkbox.is_selected()
        log(f"'{self.TARGET_LABEL}' is_selected: {is_checked}")
        if is_checked:
            return "already_enabled"

        # ── Step 6: enable the checkbox ────────────────────────────────
        click_exceptions = (
            ElementClickInterceptedException,
            ElementNotInteractableException,
            WebDriverException,
        )
        try:
            checkbox.click()
        except click_exceptions as exc:
            log(f"Direct checkbox click failed ({type(exc).__name__}); falling back to JS click")
            driver.execute_script("arguments[0].click();", checkbox)
        log(f"Checkbox clicked; is_selected now: {checkbox.is_selected()}")

        # ── Step 7: click Save to persist the setting ──────────────────
        save_btn = self._find_save_button(driver, log)
        if save_btn is None:
            raise AssertionError(
                "Save button not found in VF page after enabling checkbox. "
                "Checkbox was clicked but the setting cannot be persisted."
            )
        try:
            save_btn.click()
        except click_exceptions as exc:
            log(f"Direct Save click failed ({type(exc).__name__}); falling back to JS click")
            driver.execute_script("arguments[0].click();", save_btn)

        # Staleness of the Save button indicates the page reloaded after submission.
        try:
            WebDriverWait(driver, self.SAVE_WAIT_S).until(EC.staleness_of(save_btn))
            log("Save completed (button became stale); setting persisted")
        except TimeoutException:
            log(f"Save button did not become stale within {self.SAVE_WAIT_S} s; may have saved via AJAX")

        return "clicked"

    def _find_checkbox_by_label(self, driver, checkboxes, log):
        """Return the checkbox element associated with TARGET_LABEL.

        Raises AssertionError if no confident match is found — does NOT fall
        back to an arbitrary checkbox to avoid toggling an unrelated setting.
        """
        target = self.TARGET_LABEL.lower()

        for cb in checkboxes:
            cb_id = cb.get_attribute("id")
            # 1. label[for="<id>"] text match
            if cb_id:
                try:
                    lbl = driver.find_element(By.XPATH, f"//label[@for='{cb_id}']")
                    if target in (lbl.text or "").lower():
                        log(f"Found checkbox via label[@for='{cb_id}']: {lbl.text!r}")
                        return cb
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
            # 2. Row text match
            try:
                row_text = (cb.find_element(By.XPATH, "ancestor::tr[1]").text or "").lower()
                if target in row_text:
                    log("Found checkbox by row text match")
                    return cb
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            # 3. JS closest container text
            try:
                parent_text = (driver.execute_script(
                    "var el=arguments[0]; "
                    "var c=el.closest('tr,td,li,div'); "
                    "return c ? c.innerText : '';",
                    cb
                ) or "").lower()
                if target in parent_text:
                    log("Found checkbox via JS closest container")
                    return cb
            except (JavascriptException, StaleElementReferenceException):
                pass

        # 4. Find label element by text content, then resolve to checkbox
        try:
            lbl_el = driver.find_element(By.XPATH, "//*[contains(text(),'Enable Data Sync')]")
            lbl_for = lbl_el.get_attribute("for")
            if lbl_for:
                return driver.find_element(By.ID, lbl_for)
            return driver.find_element(
                By.XPATH,
                "//*[contains(text(),'Enable Data Sync')]/ancestor::tr[1]//input[@type='checkbox']",
            )
        except (NoSuchElementException, StaleElementReferenceException) as e:
            log(f"Label text fallback failed: {e}")

        raise AssertionError(
            f"Unable to locate checkbox for '{self.TARGET_LABEL}'. "
            f"Checked {len(checkboxes)} candidate checkbox(es) without a confident match."
        )

    @staticmethod
    def _find_save_button(driver, log):
        """Return the Save button element, or None if not found.

        Selectors are constrained to elements that are confidently Save actions
        (by value, name, or id) to avoid accidentally matching Cancel or other
        submit buttons on Visualforce pages.
        """
        for sel in [
            "input[value='Save']",
            "input[name$='saveBtn']",
            "input[name$='save']",
            ".pbButton input[value='Save']",
        ]:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                log(f"Found Save button via CSS '{sel}'")
                return els[0]
        for xp in ["//input[@value='Save']", "//input[contains(@name,'save')]"]:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                log(f"Found Save button via XPath '{xp}'")
                return els[0]
        return None
