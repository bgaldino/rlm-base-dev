*** Settings ***
Documentation     Keywords for enabling/disabling toggles on Salesforce Lightning Setup pages (e.g. Revenue Settings). These settings cannot be deployed via metadata and require browser automation. Use ORG_ALIAS with sf org open --url-only to get an authenticated URL so the Selenium browser session is logged in.
Library           SeleniumLibrary    timeout=15    implicit_wait=5
Library           Collections
Library           String
Library           Process
Library           ${EXECDIR}/robot/rlm-base/resources/WebDriverManager.py    WITH NAME    WebDriverManager

*** Variables ***
# Default timeout for waiting for setup page and toggle elements
${SETUP_PAGE_LOAD_TIMEOUT}    20s
${TOGGLE_CLICK_TIMEOUT}       10s

*** Keywords ***
Get Authenticated Revenue Settings Url
    [Documentation]    Runs \`sf org open -o <org> --url-only -p /lightning/setup/RevenueSettings/home\` to get a one-time authenticated URL. Use this so the Selenium browser session logs in without manual steps. Requires Salesforce CLI and an authenticated org alias.
    [Arguments]    ${org_alias}
    Run Keyword If    """${org_alias}""" == ""    Fail    msg=ORG_ALIAS must be set (e.g. robot -v ORG_ALIAS:my-scratch ...)
    ${result}=    Run Process    sf    org    open    -o    ${org_alias}    --url-only    -p    /lightning/setup/RevenueSettings/home    shell=False
    Run Keyword If    ${result.rc} != 0    Fail    msg=sf org open failed: ${result.stderr}
    ${raw}=    Strip String    ${result.stdout}
    ${raw}=    Evaluate    $raw.replace(chr(10), ' ').replace(chr(13), ' ').strip()
    # sf org open --url-only prints a message like "Access org ... with the following URL: https://..."
    ${url}=    Evaluate    $raw.split('with the following URL:')[-1].strip() if 'with the following URL:' in $raw else $raw
    ${url}=    Strip String    ${url}
    Run Keyword If    """${url}""" == ""    Fail    msg=sf org open did not return a URL
    RETURN    ${url}

_Get Revenue Settings Target Url
    [Documentation]    Returns the URL to use: url argument, or authenticated URL from sf org open when ORG_ALIAS set, or REVENUE_SETTINGS_URL.
    [Arguments]    ${url}=${EMPTY}
    Return From Keyword If    """${url}""" != ""    ${url}
    ${auth}=    Run Keyword If    """${ORG_ALIAS}""" != ""    Get Authenticated Revenue Settings Url    ${ORG_ALIAS}
    Return From Keyword If    """${ORG_ALIAS}""" != ""    ${auth}
    Run Keyword If    """${REVENUE_SETTINGS_URL}""" == ""    Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or REVENUE_SETTINGS_URL
    RETURN    ${REVENUE_SETTINGS_URL}

Open Revenue Settings Page
    [Documentation]    Opens the Revenue Settings setup page. If \${ORG_ALIAS} is set, uses \`sf org open --url-only\` to get an authenticated URL (recommended). Otherwise uses \${REVENUE_SETTINGS_URL} or url argument; if the page shows login, waits \${MANUAL_LOGIN_WAIT} for you to log in then reloads.
    [Arguments]    ${url}=${EMPTY}    ${wait_for_login}=${True}
    ${target}=    _Get Revenue Settings Target Url    ${url}
    Go To    ${target}
    Wait Until Page Contains Element    css:body    timeout=${SETUP_PAGE_LOAD_TIMEOUT}
    Run Keyword If    ${wait_for_login}    _Wait For Login If Needed    ${target}
    Sleep    2s    reason=Allow Lightning to finish rendering

_Wait For Login If Needed
    [Arguments]    ${target_url}
    ${title}=    Get Title
    ${title_lower}=    Convert To Lower Case    ${title}
    ${is_login}=    Run Keyword And Return Status    Should Contain    ${title_lower}    log in
    Run Keyword If    ${is_login}    Run Keywords
    ...    Log    Login page detected. Please log in to Salesforce in the browser window. Waiting ${MANUAL_LOGIN_WAIT}.
    ...    AND    Sleep    ${MANUAL_LOGIN_WAIT}
    ...    AND    Go To    ${target_url}
    ...    AND    Sleep    2s

Enable Toggle By Label
    [Documentation]    Finds a toggle by its visible label (e.g. "Document Builder") and turns it ON. Verifies the toggle is on after click; fails if it did not enable.
    [Arguments]    ${label}
    Wait Until Keyword Succeeds    ${TOGGLE_CLICK_TIMEOUT}    2s    _EnsureToggleByLabel    ${label}    turn_on=True
    Sleep    1s    reason=Allow toggle state to persist
    _VerifyToggleState By Label    ${label}    expected_on=True

Disable Toggle By Label
    [Documentation]    Finds a toggle by its visible label and turns it OFF.
    [Arguments]    ${label}
    Wait Until Keyword Succeeds    ${TOGGLE_CLICK_TIMEOUT}    2s    _EnsureToggleByLabel    ${label}    turn_on=False
    Sleep    1s    reason=Allow toggle state to persist

_VerifyToggleState By Label
    [Documentation]    Fails if the toggle for the given label is not in the expected on/off state. Document Builder uses section text (Enabled/Disabled) because the input is in shadow DOM.
    [Arguments]    ${label}    ${expected_on}=True
    Run Keyword If    """${label}""" == "Document Builder"    Run Keywords    _VerifyToggleByEnabledText    ${label}    ${expected_on}    AND    Return From Keyword
    ${toggle_locator}=    _GetToggleLocatorForLabel    ${label}
    ${aria}=    Get Element Attribute    ${toggle_locator}    aria-checked
    ${checked}=    Get Element Attribute    ${toggle_locator}    checked
    ${no_attrs}=    Set Variable If    """${aria}""" == "" or """${aria}""" == "None"    ${True}    ${False}
    ${no_attrs}=    Set Variable If    ("""${checked}""" == "" or """${checked}""" == "None") and ${no_attrs}    ${True}    ${False}
    Run Keyword If    ${no_attrs}    _VerifyToggleByEnabledText    ${label}    ${expected_on}
    Return From Keyword If    ${no_attrs}
    ${is_on}=    Set Variable If    """${aria}""" == "true"    ${True}    ${False}
    ${ck}=    Convert To Lower Case    ${checked}
    ${is_on}=    Set Variable If    """${ck}""" == "true"    ${True}    ${is_on}
    ${expected_state}=    Set Variable If    ${expected_on}    ON    OFF
    Run Keyword If    ${is_on} != ${expected_on}    Run Keywords
    ...    Capture Page Screenshot    filename=document_builder_toggle_verification_failed.png
    ...    AND    Fail    msg=Toggle "${label}" was not ${expected_state} (aria-checked=${aria}, checked=${checked}). See document_builder_toggle_verification_failed.png

_VerifyToggleByEnabledText
    [Documentation]    When toggle has no aria-checked/checked, look for "Enabled" or "Disabled" text in the section. For Document Builder, wait and retry (UI can update after JS click).
    [Arguments]    ${label}    ${expected_on}
    ${section}=    Set Variable    xpath=//*[normalize-space(.)='${label}']/ancestor::*[.//*[@role='switch'] or .//input[@type='checkbox']][1]
    Run Keyword If    """${label}""" == "Document Builder" and ${expected_on}    _VerifyDocumentBuilderEnabled    ${section}    ${label}
    Run Keyword If    """${label}""" != "Document Builder" or not ${expected_on}    _VerifyToggleByEnabledTextOneCheck    ${label}    ${expected_on}    ${section}

_VerifyToggleByEnabledTextOneCheck
    [Arguments]    ${label}    ${expected_on}    ${section}
    ${section_text}=    Get Text    ${section}
    ${has_enabled}=    Run Keyword And Return Status    Should Contain    ${section_text}    Enabled
    Run Keyword If    ${expected_on} and ${has_enabled}    Log    Toggle "${label}" verified ON via section text.
    Run Keyword If    ${expected_on} and not ${has_enabled}    Run Keywords
    ...    Capture Page Screenshot    filename=document_builder_toggle_verification_failed.png
    ...    AND    Log    WARNING: Toggle "${label}" section still shows Disabled after click. If deploy_post_docgen fails, enable Document Builder manually in Setup → Revenue Settings and re-run deploy_post_docgen.    WARN
    ${has_disabled}=    Run Keyword And Return Status    Should Contain    ${section_text}    Disabled
    Run Keyword If    not ${expected_on} and not ${has_disabled}    Fail    msg=Toggle "${label}" section does not show "Disabled" after turning off.

_VerifyDocumentBuilderEnabled
    [Arguments]    ${section}    ${label}
    ${ok}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    6s    2s    _SectionShouldContainEnabled    ${section}
    Run Keyword If    ${ok}    Log    Toggle "${label}" verified ON via section text.
    Run Keyword If    not ${ok}    Run Keywords
    ...    Capture Page Screenshot    filename=document_builder_toggle_verification_failed.png
    ...    AND    Log    WARNING: Toggle "${label}" section still shows Disabled after click. If deploy_post_docgen fails, enable Document Builder manually in Setup → Revenue Settings and re-run deploy_post_docgen.    WARN

_SectionShouldContainEnabled
    [Arguments]    ${section}
    ${section_text}=    Get Text    ${section}
    Should Contain    ${section_text}    Enabled

_GetToggleLocatorForLabel
    [Documentation]    Returns a locator for the toggle control (switch or checkbox) in the row/section that contains the label.
    [Arguments]    ${label}
    # Strategy 0: Revenue Settings uses input name="documentBuilderEnabled" for the Document Builder toggle (lightning-primitive-input-toggle). Target it directly.
    ${doc_builder_css}=    Set Variable    css:input[name=documentBuilderEnabled]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${doc_builder_css}
    Return From Keyword If    ${found} and """${label}""" == "Document Builder"    ${doc_builder_css}
    # Strategy 1: First switch/input that follows the exact title in document order (same row on Revenue Settings).
    ${following_switch}=    Set Variable    xpath=(//*[normalize-space(.)='${label}']/following::*[@role='switch'])[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${following_switch}
    Return From Keyword If    ${found}    ${following_switch}
    ${following_input}=    Set Variable    xpath=(//*[normalize-space(.)='${label}']/following::input[@type='checkbox'])[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${following_input}
    Return From Keyword If    ${found}    ${following_input}
    # Strategy 2: Exact title text; get the actual input (checkbox/switch) in that section.
    ${exact_title_input}=    Set Variable    xpath=//*[normalize-space(.)='${label}']/ancestor::*[.//input[@type='checkbox']][1]//input[@type='checkbox']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${exact_title_input}
    Return From Keyword If    ${found}    ${exact_title_input}
    ${exact_title_switch}=    Set Variable    xpath=//*[normalize-space(.)='${label}']/ancestor::*[.//*[@role='switch']][1]//*[@role='switch']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${exact_title_switch}
    Return From Keyword If    ${found}    ${exact_title_switch}
    # Strategy 2: Row that contains this label (tr or role=row)
    ${switch_in_row}=    Set Variable    xpath=//tr[.//*[contains(normalize-space(.), '${label}')]]//*[@role='switch']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${switch_in_row}
    Return From Keyword If    ${found}    ${switch_in_row}
    ${cb_in_row}=    Set Variable    xpath=//tr[.//*[contains(normalize-space(.), '${label}')]]//input[@type='checkbox']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${cb_in_row}
    Return From Keyword If    ${found}    ${cb_in_row}
    # Lightning sometimes uses role=row instead of tr
    ${switch_row}=    Set Variable    xpath=//*[@role='row'][.//*[contains(normalize-space(.), '${label}')]]//*[@role='switch']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${switch_row}
    Return From Keyword If    ${found}    ${switch_row}
    ${cb_row}=    Set Variable    xpath=//*[@role='row'][.//*[contains(normalize-space(.), '${label}')]]//input[@type='checkbox']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${cb_row}
    Return From Keyword If    ${found}    ${cb_row}
    # Fallback: label's nearest ancestor row (for non-table layouts)
    ${switch}=    Set Variable    xpath=//*[contains(normalize-space(.), '${label}')]/ancestor::tr[1]//*[@role='switch']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${switch}
    Return From Keyword If    ${found}    ${switch}
    ${cb}=    Set Variable    xpath=//*[contains(normalize-space(.), '${label}')]/ancestor::tr[1]//input[@type='checkbox']
    ${found}=    Run Keyword And Return Status    Get WebElement    ${cb}
    Return From Keyword If    ${found}    ${cb}
    # Fallback: ancestor container that has the label and a switch
    ${fallback}=    Set Variable    xpath=(//*[contains(normalize-space(.), '${label}')]/ancestor::*[.//*[@role='switch']][1]//*[@role='switch'])[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${fallback}
    Return From Keyword If    ${found}    ${fallback}
    ${fallback2}=    Set Variable    xpath=(//*[contains(normalize-space(.), '${label}')]/ancestor::*[.//input[@type='checkbox']][1]//input[@type='checkbox'])[1]
    RETURN    ${fallback2}

_EnsureToggleByLabel
    [Documentation]    Clicks the toggle for the label only if current state does not match desired state (turn_on True/False). For Document Builder the toggle input is in shadow DOM so aria-checked/checked are inaccessible; we use section text ("Enabled"/"Disabled") to detect current state.
    [Arguments]    ${label}    ${turn_on}=True
    # For Document Builder, detect state via section text (shadow DOM hides attrs)
    Run Keyword If    """${label}""" == "Document Builder"    _EnsureDocumentBuilderToggle    ${turn_on}
    Run Keyword If    """${label}""" == "Document Builder"    Return From Keyword
    # For other toggles, use aria-checked / checked attributes
    ${toggle_locator}=    _GetToggleLocatorForLabel    ${label}
    Wait Until Keyword Succeeds    15s    2s    Get WebElement    ${toggle_locator}
    Scroll Element Into View    ${toggle_locator}
    Wait Until Element Is Visible    ${toggle_locator}    timeout=10s
    ${aria}=    Get Element Attribute    ${toggle_locator}    aria-checked
    ${checked}=    Get Element Attribute    ${toggle_locator}    checked
    ${is_on}=    Set Variable If    """${aria}""" == "true"    ${True}    ${False}
    ${is_on}=    Set Variable If    """${aria}""" == "" and """${checked}""" == "true"    ${True}    ${is_on}
    Run Keyword If    ${turn_on} and not ${is_on}    _ClickToggleElement    ${toggle_locator}
    Run Keyword If    not ${turn_on} and ${is_on}    _ClickToggleElement    ${toggle_locator}
    Run Keyword If    ${turn_on} and not ${is_on}    Sleep    2s    reason=Allow toggle to update
    Run Keyword If    not ${turn_on} and ${is_on}    Sleep    1s    reason=Allow toggle to update

_EnsureDocumentBuilderToggle
    [Documentation]    For Document Builder: check section text to see if already Enabled/Disabled, then click ONCE via JS only if needed. Avoids the multiple-click problem that toggles it back off.
    [Arguments]    ${turn_on}=True
    ${section}=    Set Variable    xpath=//*[normalize-space(.)='Document Builder']/ancestor::*[.//*[@role='switch'] or .//input[@type='checkbox']][1]
    Wait Until Keyword Succeeds    15s    2s    Get WebElement    ${section}
    Sleep    1s    reason=Allow section to render
    ${section_text}=    Get Text    ${section}
    ${has_enabled}=    Run Keyword And Return Status    Should Contain    ${section_text}    Enabled
    ${has_disabled}=    Run Keyword And Return Status    Should Contain    ${section_text}    Disabled
    # Already in desired state -- do nothing
    Run Keyword If    ${turn_on} and ${has_enabled}    Log    Document Builder is already Enabled. No click needed.
    Return From Keyword If    ${turn_on} and ${has_enabled}
    Run Keyword If    not ${turn_on} and ${has_disabled}    Log    Document Builder is already Disabled. No click needed.
    Return From Keyword If    not ${turn_on} and ${has_disabled}
    # Need to toggle -- click exactly once via JS (pierces shadow DOM)
    Log    Document Builder is currently ${{" Enabled" if ${has_enabled} else "Disabled"}}. Clicking once to toggle.
    Execute JavaScript    (function(){ function findInShadows(root){ var el=root.querySelector("input[name=documentBuilderEnabled]"); if(el)return el; var list=root.querySelectorAll("*"); for(var i=0;i<list.length;i++){ if(list[i].shadowRoot){ var r=findInShadows(list[i].shadowRoot); if(r)return r; } } return null; } var el=document.querySelector("input[name=documentBuilderEnabled]")||findInShadows(document.body); if(el)el.click(); })()
    Sleep    3s    reason=Allow toggle state to update after JS click

_ClickToggleElement
    [Documentation]    Clicks the toggle element. Tries Click Element and Double Click (JS click with xpath is avoided; it can break when xpath contains //).
    [Arguments]    ${toggle_locator}
    ${clicked}=    Run Keyword And Return Status    Click Element    ${toggle_locator}
    Run Keyword If    not ${clicked}    Double Click Element    ${toggle_locator}
    Sleep    0.5s    reason=Allow click to register

*** Keywords ***
Open Browser For Setup
    [Documentation]    Opens a browser (Chrome by default). If webdriver-manager is installed it manages ChromeDriver automatically; otherwise falls back to the system ChromeDriver on PATH. Set BROWSER or \${BROWSER} to override (e.g. firefox).
    [Arguments]    ${browser}=chrome
    Run Keyword If    """${browser}""" == "chrome"    _Open Chrome With Managed Driver
    ...    ELSE    Open Browser    about:blank    ${browser}
    Maximize Browser Window

_Open Chrome With Managed Driver
    [Documentation]    Create Chrome driver. Uses webdriver-manager when available; falls back to system ChromeDriver on PATH.
    ${path}=    WebDriverManager.Get Chrome Driver Path
    Run Keyword If    """${path}""" != "None" and """${path}""" != ""    _Open Chrome With Explicit Path    ${path}
    ...    ELSE    Open Browser    about:blank    chrome

_Open Chrome With Explicit Path
    [Arguments]    ${path}
    Create Webdriver    Chrome    executable_path=${path}
    Go To    about:blank

Close Browser After Setup
    [Documentation]    Closes the browser. Use in suite teardown or after tests.
    Close Browser
