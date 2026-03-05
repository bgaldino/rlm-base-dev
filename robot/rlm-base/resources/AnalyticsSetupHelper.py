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

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class AnalyticsSetupHelper:
    """Keyword library for enabling Analytics settings in the VF iframe."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    TARGET_LABEL = "Enable Data Sync and Connections"

    @property
    def _driver(self):
        selib = BuiltIn().get_library_instance("SeleniumLibrary")
        return selib.driver

    @keyword
    def enable_data_sync_and_connections_via_cdp(self):
        """Enable the 'Enable Data Sync and Connections' checkbox in the VF iframe.

        The Analytics Settings page embeds a Visualforce page (waveSetupSettings.apexp)
        in a child iframe.  This keyword:
          1. Waits for the VF iframe to appear (up to 30 s).
          2. Switches Selenium into the VF iframe.
          3. Waits for checkboxes to appear in the VF page (up to 30 s).
          4. Finds the checkbox associated with the 'Enable Data Sync and Connections' label.
          5. Clicks the checkbox if not already enabled.
          6. Clicks the Save button to persist the setting.

        Returns:
            'already_enabled'  — checkbox was already checked; no action taken.
            'clicked'          — checkbox was found, enabled, and saved.
        Raises:
            AssertionError     — VF iframe or checkbox not found.
        """
        log = BuiltIn().log
        driver = self._driver

        # ── Step 1: ensure we start in the main frame ──────────────────
        driver.switch_to.default_content()

        # ── Step 2: wait for the VF iframe to appear ───────────────────
        log("Waiting for VF iframe (waveSetupSettings.apexp) to appear...")
        iframe_xpath = "//iframe[contains(@title, 'Salesforce') or contains(@name, 'vfFrameId')]"
        try:
            iframe_el = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )
        except Exception:
            iframe_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[1]"))
            )
        log(f"VF iframe found: title={iframe_el.get_attribute('title')!r}")

        # ── Step 3: switch into the VF iframe ──────────────────────────
        driver.switch_to.frame(iframe_el)

        # ── Step 4: wait for VF page checkboxes to appear ──────────────
        checkbox = None
        deadline = time.time() + 30
        while time.time() < deadline:
            cbs = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            log(f"VF frame: WebDriver found {len(cbs)} checkbox(es)")
            if cbs:
                checkbox = self._find_checkbox_by_label(driver, cbs, log)
                break
            time.sleep(3)

        if checkbox is None:
            raise AssertionError(
                f"Could not find '{self.TARGET_LABEL}' checkbox in VF iframe after 30 s."
            )

        # ── Step 5: check current state ────────────────────────────────
        is_checked = checkbox.is_selected()
        log(f"'{self.TARGET_LABEL}' is_selected: {is_checked}")
        if is_checked:
            driver.switch_to.default_content()
            return "already_enabled"

        # ── Step 6: enable the checkbox ────────────────────────────────
        try:
            checkbox.click()
        except Exception:
            driver.execute_script("arguments[0].click();", checkbox)
        log(f"Checkbox clicked; is_selected now: {checkbox.is_selected()}")

        # ── Step 7: click Save to persist the setting ──────────────────
        save_btn = self._find_save_button(driver, log)
        if save_btn:
            try:
                save_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(3)
            log("Save button clicked; setting persisted")
        else:
            log("WARNING: No Save button found — setting may not persist on page reload")

        driver.switch_to.default_content()
        return "clicked"

    # ── Private helpers ────────────────────────────────────────────────

    def _find_checkbox_by_label(self, driver, checkboxes, log):
        """Return the checkbox element associated with TARGET_LABEL."""
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
                except Exception:
                    pass
            # 2. Row text match
            try:
                row_text = (cb.find_element(By.XPATH, "ancestor::tr[1]").text or "").lower()
                if target in row_text:
                    log(f"Found checkbox by row text match")
                    return cb
            except Exception:
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
                    log(f"Found checkbox via JS closest container")
                    return cb
            except Exception:
                pass

        # 4. Find label by text, then navigate to nearby checkbox
        try:
            lbl_el = driver.find_element(By.XPATH, "//*[contains(text(),'Enable Data Sync')]")
            lbl_for = lbl_el.get_attribute("for")
            if lbl_for:
                return driver.find_element(By.ID, lbl_for)
            return driver.find_element(
                By.XPATH,
                "//*[contains(text(),'Enable Data Sync')]/ancestor::tr[1]//input[@type='checkbox']"
            )
        except Exception as e:
            log(f"Label text fallback failed: {e}")

        log(f"Could not match to '{self.TARGET_LABEL}'; using first checkbox as fallback")
        return checkboxes[0]

    @staticmethod
    def _find_save_button(driver, log):
        """Return the Save button element, or None if not found."""
        for sel in [
            "input[value='Save']",
            "input[type='submit']",
            "input[name$='saveBtn']",
            "input[name$='save']",
            ".pbButton input[type='submit']",
            ".pbButton input",
        ]:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                log(f"Found Save button via CSS '{sel}'")
                return els[0]
        for xp in ["//input[@value='Save']", "//input[@type='submit']"]:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                log(f"Found Save button via XPath '{xp}'")
                return els[0]
        return None
