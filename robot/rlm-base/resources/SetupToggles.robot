*** Settings ***
Documentation     Keywords for enabling/disabling toggles on Salesforce Lightning Setup pages (e.g. Revenue Settings). These settings cannot be deployed via metadata and require browser automation. Use ORG_ALIAS to log the Selenium browser in through sf org open --url-only; SessionUrlGuard.py keeps that session URL out of every Robot log (never put it in a Robot variable or keyword argument).
Library           SeleniumLibrary    timeout=15    implicit_wait=5
Library           Collections
Library           String
Library           Process
Library           ${EXECDIR}/robot/rlm-base/resources/WebDriverManager.py    WITH NAME    WebDriverManager
Library           ${EXECDIR}/robot/rlm-base/resources/ChromeOptionsHelper.py
Library           ${EXECDIR}/robot/rlm-base/resources/SessionUrlGuard.py

*** Variables ***
# Default timeout for waiting for setup page and toggle elements
${SETUP_PAGE_LOAD_TIMEOUT}    20s
${TOGGLE_CLICK_TIMEOUT}       30s
# Password used to complete a forced "Change Your Password" reset if frontdoor
# login lands there (safety net; the set_scratch_org_password CCI task normally
# clears the must-reset flag first). Keep in sync with
# scripts/apex/setScratchOrgPassword.apex.
${SCRATCH_NEW_PASSWORD}       Cumulus1234!
# Shared JS helper — pierces lightning-input → lightning-primitive-input-toggle → input.
# Prepended to the _LabelToggleJS block, which both ensure and verify use.
${_JS_GET_INPUT_FROM_TOGGLE}    function getInputFromToggle(li){if(!li.shadowRoot)return null;var inp=li.shadowRoot.querySelector('input[role="switch"],input[type="checkbox"]');if(inp)return inp;var n=li.shadowRoot.querySelector('lightning-primitive-input-toggle');if(n&&n.shadowRoot)return n.shadowRoot.querySelector('input[role="switch"],input[type="checkbox"]');return null;}
# Canonical depth-limited shadow-DOM search (.cursor/rules/robot-tests.mdc). Use this
# instead of an unbounded recursive walk so traversal can't run away on complex pages.
${_JS_FIND_EL}    function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }

*** Keywords ***
_Open Target Page
    [Documentation]    Navigates to an explicit \`${url}\` when given, otherwise to \`${setup_path}\` in
    ...    \${ORG_ALIAS} through an authenticated session (see SessionUrlGuard.py). The
    ...    authenticated URL never enters a Robot variable, so it cannot reach output.xml or log.html.
    [Arguments]    ${setup_path}    ${url}=${EMPTY}
    IF    """${url}""" != ""
        Go To    ${url}
    ELSE IF    """${ORG_ALIAS}""" != ""
        Go To Authenticated Page    ${ORG_ALIAS}    ${setup_path}
    ELSE
        Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or provide a url argument
    END

Open Setup Page
    [Documentation]    Opens any Salesforce setup page by path. If \${ORG_ALIAS} is set, logs in with a one-time \`sf org open --url-only\` session. Otherwise uses the provided url argument, which must not itself carry a session (frontdoor/sid/otp); the authenticated URL is never logged (SessionUrlGuard.py).
    [Arguments]    ${setup_path}=/lightning/setup/RevenueSettings/home    ${url}=${EMPTY}    ${wait_for_login}=${True}
    _Open Target Page    ${setup_path}    ${url}
    Wait Until Page Contains Element    css:body    timeout=${SETUP_PAGE_LOAD_TIMEOUT}
    Run Keyword If    ${wait_for_login}    _Wait For Login If Needed    ${setup_path}    ${url}
    Sleep    2s    reason=Allow Lightning to finish rendering

Open Revenue Settings Page
    [Documentation]    Opens the Revenue Settings setup page. If \${ORG_ALIAS} is set, logs in with a one-time \`sf org open --url-only\` session (recommended; never logged). Otherwise uses the url argument or \${REVENUE_SETTINGS_URL}; if the page shows login, waits \${MANUAL_LOGIN_WAIT} for you to log in then reloads.
    [Arguments]    ${url}=${EMPTY}    ${wait_for_login}=${True}
    IF    """${url}""" == "" and """${ORG_ALIAS}""" == ""
        Run Keyword If    """${REVENUE_SETTINGS_URL}""" == ""    Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or REVENUE_SETTINGS_URL
        ${url}=    Set Variable    ${REVENUE_SETTINGS_URL}
    END
    Open Setup Page    /lightning/setup/RevenueSettings/home    ${url}    ${wait_for_login}

_Wait For Login If Needed
    [Arguments]    ${setup_path}    ${url}=${EMPTY}
    ${title}=    Get Title
    ${title_lower}=    Convert To Lower Case    ${title}
    ${is_login}=    Run Keyword And Return Status    Should Contain    ${title_lower}    log in
    Run Keyword If    ${is_login}    Run Keywords
    ...    Log    Login page detected. Please log in to Salesforce in the browser window. Waiting ${MANUAL_LOGIN_WAIT}.
    ...    AND    Sleep    ${MANUAL_LOGIN_WAIT}
    ...    AND    _Open Target Page    ${setup_path}    ${url}
    ...    AND    Sleep    2s
    _Handle Change Password If Needed    ${setup_path}    ${url}

_Handle Change Password If Needed
    [Documentation]    Safety net for scratch org definitions (e.g. the TSO-derived
    ...    tfid-cdo-rlm template) that flag the admin user to reset password at next
    ...    login. When that happens, frontdoor (sf org open --url-only) redirects to
    ...    "Change Your Password" instead of the requested Setup page, so every toggle
    ...    lookup fails on the wrong page. The set_scratch_org_password CCI task
    ...    (prepare_core step 1) normally clears the flag before any UI step; this
    ...    keyword completes the reset in-browser if the page is still reached, then
    ...    returns to the target Setup URL.
    [Arguments]    ${setup_path}    ${url}=${EMPTY}
    ${title}=    Get Title
    ${title_lower}=    Convert To Lower Case    ${title}
    ${is_change_pw}=    Run Keyword And Return Status    Should Contain    ${title_lower}    change your password
    Return From Keyword If    not ${is_change_pw}
    Log    "Change Your Password" page detected; completing reset in-browser and continuing.
    ${pw_inputs}=    Get WebElements    css:input[type="password"]
    ${count}=    Get Length    ${pw_inputs}
    Run Keyword If    ${count} == 0    Fail
    ...    msg=Change Your Password page reached but no password inputs found. Run `cci task run set_scratch_org_password` against this org, then retry.
    # New Password + Confirm New Password take the same value; frontdoor reset
    # does not require the current password. Input Password masks the value in log.html.
    FOR    ${el}    IN    @{pw_inputs}
        Input Password    ${el}    ${SCRATCH_NEW_PASSWORD}
    END
    ${clicked}=    Run Keyword And Return Status    Click Element
    ...    xpath=//*[(self::input or self::button) and (contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'change password') or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'change password'))]
    Run Keyword If    not ${clicked}    Click Element    css:input[type="submit"], button[type="submit"]
    Wait Until Keyword Succeeds    20s    2s    _Change Password Page Gone
    _Open Target Page    ${setup_path}    ${url}
    Wait Until Page Contains Element    css:body    timeout=${SETUP_PAGE_LOAD_TIMEOUT}
    Sleep    3s    reason=Allow Setup page to load after password change

_Change Password Page Gone
    [Documentation]    Succeeds once the browser has navigated away from the
    ...    "Change Your Password" page (drives Wait Until Keyword Succeeds).
    ${title}=    Get Title
    ${title_lower}=    Convert To Lower Case    ${title}
    Should Not Contain    ${title_lower}    change your password

Enable Toggle By Label
    [Documentation]    Finds a toggle by its visible label (e.g. "Document Builder") and turns it ON. Verifies the toggle is on after click; fails if it did not enable.
    [Arguments]    ${label}
    Wait Until Keyword Succeeds    ${TOGGLE_CLICK_TIMEOUT}    2s    _EnsureToggleByLabel    ${label}    turn_on=True
    Sleep    1s    reason=Allow toggle state to persist
    _VerifyToggleState By Label    ${label}    expected_on=True

Disable Toggle By Label
    [Documentation]    Finds a toggle by its visible label and turns it OFF. Verifies the toggle is off after click.
    [Arguments]    ${label}
    Wait Until Keyword Succeeds    ${TOGGLE_CLICK_TIMEOUT}    2s    _EnsureToggleByLabel    ${label}    turn_on=False
    Sleep    1s    reason=Allow toggle state to persist
    _VerifyToggleState By Label    ${label}    expected_on=False

_VerifyToggleState By Label
    [Documentation]    Fails if the toggle for the given label is not in the expected on/off state.
    ...    For Document Builder, reads the documentBuilderEnabled input (expected ON only warns).
    ...    For other toggles, reads the toggle found by the label text-walker, the same
    ...    element _EnsureToggleByLabel acted on. Reads the client-side checked state; it
    ...    does not reload the page.
    [Arguments]    ${label}    ${expected_on}=True
    Run Keyword If    """${label}""" == "Document Builder"    Run Keywords    _VerifyDocumentBuilderToggle    ${label}    ${expected_on}    AND    Return From Keyword
    _VerifyToggleViaShadowDOM    ${label}    ${expected_on}

_VerifyDocumentBuilderToggle
    [Documentation]    Document Builder verify: reads input[name=documentBuilderEnabled]. Expected ON
    ...    only warns (deploy_post_docgen reports a real failure); expected OFF fails.
    [Arguments]    ${label}    ${expected_on}
    Run Keyword If    ${expected_on}    _VerifyDocumentBuilderEnabled    ${label}
    Run Keyword If    not ${expected_on}    Wait Until Keyword Succeeds    6s    2s    _Document Builder Toggle Should Be Off

_VerifyDocumentBuilderEnabled
    [Arguments]    ${label}
    ${ok}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    6s    2s    _Document Builder Toggle Should Be On
    Run Keyword If    ${ok}    Log    Toggle "${label}" verified ON via shadow DOM JS.
    Run Keyword If    not ${ok}    Run Keywords
    ...    Capture Page Screenshot    filename=document_builder_toggle_verification_failed.png
    ...    AND    Log    WARNING: Toggle "${label}" could not be verified as enabled via shadow DOM. If deploy_post_docgen fails, enable Document Builder manually in Setup → Revenue Settings and re-run deploy_post_docgen.    WARN

_Document Builder Toggle Should Be On
    ${state}=    _Get Document Builder Toggle State
    Should Be Equal    ${state}    on
    ...    msg=Document Builder toggle is not on (got: ${state})

_Document Builder Toggle Should Be Off
    ${state}=    _Get Document Builder Toggle State
    Should Be Equal    ${state}    off
    ...    msg=Document Builder toggle is not off (got: ${state})

_Get Document Builder Toggle State
    ${state}=    Execute JavaScript
    ...    return (function() {
    ...        ${_JS_FIND_EL}
    ...        var el = findEl(document, 'input[name="documentBuilderEnabled"]', 0);
    ...        if (!el) return 'not_found';
    ...        return el.checked ? 'on' : 'off';
    ...    })()
    Should Not Be Equal    ${state}    not_found
    ...    msg=Document Builder input[name="documentBuilderEnabled"] not yet rendered
    RETURN    ${state}

_VerifyToggleViaShadowDOM
    [Documentation]    Verify toggle state by piercing shadow DOM via JavaScript (_LabelToggleJS
    ...    in read mode). Retries while the label or toggle is not resolved, then fails
    ...    rather than falling back to a locator that could read another card's toggle.
    [Arguments]    ${label}    ${expected_on}=True
    ${state}=    Wait Until Keyword Succeeds    15s    2s    _Read Label Toggle State    ${label}
    Log    Shadow DOM verify for "${label}": state=${state}, expected_on=${expected_on}
    IF    "${state}" == "on" and ${expected_on}
        Log    Toggle "${label}" verified ON via shadow DOM JS.
    ELSE IF    "${state}" == "off" and not ${expected_on}
        Log    Toggle "${label}" verified OFF via shadow DOM JS.
    ELSE
        ${expected_state}=    Set Variable If    ${expected_on}    ON    OFF
        Capture Page Screenshot    filename=toggle_verification_failed_${label}.png
        Fail    msg=Toggle "${label}" is ${state} but expected ${expected_state} (shadow DOM verification).
    END

_Read Label Toggle State
    [Arguments]    ${label}
    ${state}=    _LabelToggleJS    ${label}    read
    Should Be True    "${state}" in ("on", "off")
    ...    msg=Toggle "${label}" not resolved by the label text-walker (result: ${state}); retrying...
    RETURN    ${state}

_EnsureToggleByLabel
    [Documentation]    Clicks the toggle for the label only if its current state does not match turn_on.
    ...    Document Builder reads input[name=documentBuilderEnabled] directly. Other labels use
    ...    _LabelToggleJS, which reads and clicks the same element verify reads. An unresolved
    ...    label or toggle fails this attempt so the caller's Wait Until Keyword Succeeds retries;
    ...    there is no xpath fallback, because the old contains() locators resolved to another
    ...    card's checkbox on 264 General Settings (the Word add-in for "Design Document
    ...    Templates in Salesforce"), read it as on and skipped the click.
    [Arguments]    ${label}    ${turn_on}=True
    Run Keyword If    """${label}""" == "Document Builder"    _EnsureDocumentBuilderToggle    ${turn_on}
    Run Keyword If    """${label}""" == "Document Builder"    Return From Keyword
    # Settle first: a toggle can render unchecked before its saved value loads.
    Sleep    5s    reason=Allow the saved toggle value to load before reading it
    ${action}=    Set Variable If    ${turn_on}    on    off
    ${result}=    _LabelToggleJS    ${label}    ${action}
    Run Keyword If    "${result}" == "clicked"    Sleep    3s    reason=Allow toggle state to update after JS click
    Should Be True    "${result}" in ("already_enabled", "already_disabled", "clicked")
    ...    msg=Toggle "${label}" not resolved by the label text-walker (result: ${result}); retrying...

_EnsureDocumentBuilderToggle
    [Documentation]    For Document Builder: read the shadow-DOM input state, then click ONCE via JS only if needed. Avoids the multiple-click problem that toggles it back off.
    [Arguments]    ${turn_on}=True
    # Wait on the input itself (findEl pierces shadow roots). A light-DOM xpath wait on the
    # "Document Builder" section can miss it even when the toggle is rendered and already on.
    # The input can render unchecked before the saved value loads (seen live on 264 with the
    # setting already on), so let it settle and read the state again before deciding to click.
    Wait Until Keyword Succeeds    30s    2s    _Get Document Builder Toggle State
    Sleep    5s    reason=Allow the saved Document Builder value to load into the toggle
    ${state}=    _Get Document Builder Toggle State
    # Already in desired state -- do nothing
    Run Keyword If    ${turn_on} and "${state}" == "on"    Log    Document Builder is already Enabled. No click needed.
    Return From Keyword If    ${turn_on} and "${state}" == "on"
    Run Keyword If    not ${turn_on} and "${state}" == "off"    Log    Document Builder is already Disabled. No click needed.
    Return From Keyword If    not ${turn_on} and "${state}" == "off"
    # Need to toggle -- click exactly once via JS (pierces shadow DOM)
    Log    Document Builder is currently ${state}. Clicking once to toggle.
    Execute JavaScript    (function(){ ${_JS_FIND_EL} var el=findEl(document, 'input[name="documentBuilderEnabled"]', 0); if(el)(el.closest('label')||el).click(); })()
    Sleep    3s    reason=Allow toggle state to update after JS click

_LabelToggleJS
    [Documentation]    Finds the label heading with a light-DOM text walker (exact trimmed text), then
    ...    walks up its ancestors to the first that contains a toggle. At each depth,
    ...    lightning-input elements are checked first (piercing nested shadow roots via
    ...    getInputFromToggle); plain checkbox or switch inputs only at depths with no
    ...    lightning-input. If a lightning-input at that depth has not rendered before a toggle is
    ...    found, returns toggle_not_ready instead of widening the search to a neighbouring card;
    ...    a depth whose lightning-inputs hold no toggle is skipped, plain inputs included. It assumes
    ...    the label's own toggle is the first one reached on the way up.
    ...    action: read returns on or off; on/off returns already_enabled, already_disabled or
    ...    clicked (at most one click, only when the state differs). Failure results:
    ...    label_not_found, section_not_found, toggle_not_ready, toggle_not_found.
    [Arguments]    ${label}    ${action}=read
    ${result}=    Execute Javascript
    ...    ${_JS_GET_INPUT_FROM_TOGGLE}
    ...    return (function(label, action) {
    ...        function act(inp) {
    ...            if (action === 'read') return inp.checked ? 'on' : 'off';
    ...            var want = action === 'on';
    ...            if (want && inp.checked) return 'already_enabled';
    ...            if (!want && !inp.checked) return 'already_disabled';
    ...            (inp.closest('label') || inp).click();
    ...            return 'clicked';
    ...        }
    ...        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    ...        var headingEl = null;
    ...        while (walker.nextNode()) {
    ...            if (walker.currentNode.textContent.trim() === label) {
    ...                headingEl = walker.currentNode.parentElement;
    ...                break;
    ...            }
    ...        }
    ...        if (!headingEl) return 'label_not_found';
    ...        var section = headingEl;
    ...        for (var depth = 0; depth < 10; depth++) {
    ...            section = section.parentElement;
    ...            if (!section || section === document.body) return 'section_not_found';
    ...            var toggles = section.querySelectorAll('lightning-input');
    ...            if (toggles.length > 0) {
    ...                var found = null;
    ...                for (var j = 0; j < toggles.length; j++) {
    ...                    var sr = toggles[j].shadowRoot;
    ...                    if (!sr || sr.childElementCount === 0) { if (!found) return 'toggle_not_ready'; continue; }
    ...                    var inp = getInputFromToggle(toggles[j]);
    ...                    if (inp && !found) found = inp;
    ...                }
    ...                if (found) return act(found);
    ...                continue;
    ...            }
    ...            var plainInputs = section.querySelectorAll('input[type="checkbox"],input[role="switch"]');
    ...            if (plainInputs.length > 0) return act(plainInputs[0]);
    ...        }
    ...        return 'toggle_not_found';
    ...    })(arguments[0], arguments[1])
    ...    ARGUMENTS    ${label}    ${action}
    Log    Label toggle JS (${action}) for "${label}": ${result}
    RETURN    ${result}

*** Keywords ***
Open Browser For Setup
    [Documentation]    Opens a browser (Chrome by default). If webdriver-manager is installed it manages ChromeDriver automatically; otherwise falls back to the system ChromeDriver on PATH. Set BROWSER or \${BROWSER} to override (e.g. firefox).
    [Arguments]    ${browser}=chrome
    Run Keyword If    """${browser}""" == "chrome"    _Open Chrome With Managed Driver
    ...    ELSE    Open Browser    about:blank    ${browser}
    Maximize Browser Window

_Open Chrome With Managed Driver
    [Documentation]    Create Chrome driver with headless options (default for CCI robot tasks). Uses webdriver-manager when available; falls back to system ChromeDriver on PATH.
    ${path}=    WebDriverManager.Get Chrome Driver Path
    Run Keyword If    """${path}""" != "None" and """${path}""" != ""    _Open Chrome With Explicit Path    ${path}
    ...    ELSE    _Open Chrome With Options Fallback

_Open Chrome With Explicit Path
    [Arguments]    ${path}
    ${options}=    Get Headless Chrome Options
    ${service}=    Evaluate    selenium.webdriver.chrome.service.Service(executable_path=$path)    selenium.webdriver.chrome.service
    Create Webdriver    Chrome    service=${service}    options=${options}
    Go To    about:blank

_Open Chrome With Options Fallback
    [Documentation]    Opens Chrome with headless options when no explicit ChromeDriver path is provided.
    ${options}=    Get Headless Chrome Options
    Create Webdriver    Chrome    options=${options}
    Go To    about:blank

Close Browser After Setup
    [Documentation]    Closes the browser. Use in suite teardown or after tests.
    Close Browser
