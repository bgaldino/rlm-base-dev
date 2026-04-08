*** Settings ***
Documentation     Configure Billing Email Delivery Settings: cycle the "Configure Email
...               Delivery Settings" toggle via the UI to trigger auto-creation of the
...               default invoice email template. The Metadata API toggle cycling in
...               prepare_billing (steps 9→10) sets the boolean but does not trigger the
...               Salesforce backend logic that auto-creates and sets the default email
...               template. A UI toggle cycle (off then on) is required. Must run after
...               deploy_billing_template_settings.
Resource          ../../resources/SetupToggles.robot
Suite Setup       _Open Headed Browser For Billing
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                  ${EMPTY}
${BILLING_SETTINGS_URL}       ${EMPTY}
${MANUAL_LOGIN_WAIT}          90s
# Shared shadow-DOM traversal helper prepended to Execute JavaScript blocks that need findEl.
${_JS_FIND_EL}    function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }

*** Test Cases ***
Configure Billing Email Delivery Settings
    [Documentation]    Navigates to Billing Settings and cycles the "Configure Email
    ...    Delivery Settings" toggle off then on via the UI to trigger the Salesforce
    ...    backend that auto-creates and sets the default invoice email template.
    ...    The Disable/Enable keywords check current toggle state before clicking,
    ...    so re-running is safe (the backend template creation is idempotent).
    Open Billing Settings Page
    Capture Page Screenshot
    Wait Until Keyword Succeeds    30s    5s    _Toggle Off Email Delivery
    Sleep    2s    reason=Allow toggle-off state to register
    Wait Until Keyword Succeeds    30s    5s    _Toggle On Email Delivery
    ${template}=    Wait Until Keyword Succeeds    30s    5s    _Assert Email Template Populated
    Capture Page Screenshot
    Log    Configure Email Delivery Settings cycled. Default Email Template confirmed: "${template}".

*** Keywords ***
_Open Headed Browser For Billing
    [Documentation]    Opens Chrome in headed (visible) mode. Required for Billing Settings
    ...    toggle cycling: the LWC dispatches an Apex call on toggle that only completes
    ...    when Chrome is running headed. Headless mode suppresses this backend event.
    ${path}=    WebDriverManager.Get Chrome Driver Path
    ${options}=    Get Headed Chrome Options
    IF    """${path}""" != "None" and """${path}""" != ""
        ${service}=    Evaluate    selenium.webdriver.chrome.service.Service(executable_path=$path)    selenium.webdriver.chrome.service
        Create Webdriver    Chrome    service=${service}    options=${options}
    ELSE
        Create Webdriver    Chrome    options=${options}
    END
    Go To    about:blank
    Maximize Browser Window

Open Billing Settings Page
    [Documentation]    Opens the Billing Settings setup page using sf org open when
    ...    ORG_ALIAS is set, or falls back to BILLING_SETTINGS_URL.
    ${path}=    Set Variable    /lightning/setup/BillingSettings/home
    IF    """${ORG_ALIAS}""" != ""
        Open Setup Page    ${path}
    ELSE IF    """${BILLING_SETTINGS_URL}""" != ""
        Open Setup Page    url=${BILLING_SETTINGS_URL}
    ELSE
        Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or BILLING_SETTINGS_URL
    END

_Toggle Off Email Delivery
    [Documentation]    Turns Configure Email Delivery Settings OFF via targeted JS.
    ...    Uses compareDocumentPosition to find only the toggle following the section
    ...    heading — avoids the top-level Billing service toggle which precedes it.
    ...    Returns page_not_ready when LWC hasn't rendered; retried by caller.
    ${result}=    Execute JavaScript
    ...    ${_JS_GET_INPUT_FROM_TOGGLE}
    ...    return (function() {
    ...        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    ...        while (walker.nextNode()) {
    ...            if (walker.currentNode.textContent.trim() !== 'Configure Email Delivery Settings') continue;
    ...            var textEl = walker.currentNode.parentElement;
    ...            var section = textEl;
    ...            for (var d = 0; d < 8; d++) {
    ...                section = section.parentElement;
    ...                if (!section || section === document.body) break;
    ...                var lis = Array.from(section.querySelectorAll('lightning-input'));
    ...                var after = lis.filter(function(li) { return textEl.compareDocumentPosition(li) & 4; });
    ...                if (after.length === 0) continue;
    ...                var inp = getInputFromToggle(after[0]);
    ...                if (!inp) continue;
    ...                if (!inp.checked) return 'already_off';
    ...                (inp.closest('label') || inp).click();
    ...                return 'turned_off';
    ...            }
    ...            return 'page_not_ready';
    ...        }
    ...        return 'page_not_ready';
    ...    })()
    Log    Toggle OFF result: ${result}
    Should Contain    ${result}    off    msg=${result}

_Toggle On Email Delivery
    [Documentation]    Turns Configure Email Delivery Settings ON via targeted JS.
    ...    Uses compareDocumentPosition to find only the toggle following the section
    ...    heading — avoids the top-level Billing service toggle which precedes it.
    ...    Returns page_not_ready when LWC hasn't rendered; retried by caller.
    ${result}=    Execute JavaScript
    ...    ${_JS_GET_INPUT_FROM_TOGGLE}
    ...    return (function() {
    ...        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    ...        while (walker.nextNode()) {
    ...            if (walker.currentNode.textContent.trim() !== 'Configure Email Delivery Settings') continue;
    ...            var textEl = walker.currentNode.parentElement;
    ...            var section = textEl;
    ...            for (var d = 0; d < 8; d++) {
    ...                section = section.parentElement;
    ...                if (!section || section === document.body) break;
    ...                var lis = Array.from(section.querySelectorAll('lightning-input'));
    ...                var after = lis.filter(function(li) { return textEl.compareDocumentPosition(li) & 4; });
    ...                if (after.length === 0) continue;
    ...                var inp = getInputFromToggle(after[0]);
    ...                if (!inp) continue;
    ...                if (inp.checked) return 'already_on';
    ...                (inp.closest('label') || inp).click();
    ...                return 'turned_on';
    ...            }
    ...            return 'page_not_ready';
    ...        }
    ...        return 'page_not_ready';
    ...    })()
    Log    Toggle ON result: ${result}
    Should Contain    ${result}    on    msg=${result}

_Assert Email Template Populated
    [Documentation]    Calls _Get Email Template Selection and FAILS if the value is
    ...    'not_set'. Designed for use with Wait Until Keyword Succeeds so the retry
    ...    loop actually polls — _Get Email Template Selection always returns a string
    ...    and never raises, so it cannot be used directly with Wait Until Keyword Succeeds.
    ${value}=    _Get Email Template Selection
    Should Not Be Equal    ${value}    not_set
    ...    msg=Default invoice email template not yet populated (got: ${value})
    RETURN    ${value}

_Get Email Template Selection
    [Documentation]    Returns the current value of the "Select Default Email Template"
    ...    combobox via JavaScript, or 'not_set' if empty.
    ${value}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return (function() {
    ...        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    ...        while (walker.nextNode()) {
    ...            if (walker.currentNode.textContent.trim() === 'Select Default Email Template') {
    ...                var el = walker.currentNode.parentElement;
    ...                for (var d = 0; d < 10; d++) {
    ...                    el = el.parentElement;
    ...                    if (!el) break;
    ...                    var pill = findEl(el, '.slds-pill__label', 0);
    ...                    if (pill && pill.textContent.trim()) return pill.textContent.trim();
    ...                    var btn = findEl(el, 'button[role="combobox"]', 0);
    ...                    if (btn) {
    ...                        var t = btn.textContent.trim();
    ...                        if (t && t !== 'Select...' && t !== '') return t;
    ...                    }
    ...                    var sel = el.querySelector('lightning-combobox,select');
    ...                    if (sel && sel.value && sel.value !== '') return sel.value;
    ...                }
    ...                break;
    ...            }
    ...        }
    ...        return 'not_set';
    ...    })()
    RETURN    ${value}
