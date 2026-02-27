*** Settings ***
Documentation     Set Default Transaction Type to "Advanced Configurator" and enable
...               "Set Up Configuration Rules and Constraints with Constraints Engine"
...               on the Revenue Settings page. Must run before constraint data can be
...               imported (prepare_constraints CML steps).
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                            ${EMPTY}
${REVENUE_SETTINGS_URL}                 ${EMPTY}
${MANUAL_LOGIN_WAIT}                    90s
${DEFAULT_TRANSACTION_TYPE_VALUE}       Advanced Configurator
${ASSET_CONTEXT}                        RLM_AssetContext
${CONSTRAINTS_TOGGLE_LABEL}             Set Up Configuration Rules and Constraints with Constraints Engine

*** Test Cases ***
Configure Constraints Prerequisites
    [Documentation]    Navigate to Revenue Settings and configure constraints prerequisites:
    ...    1. Set Default Transaction Type to "Advanced Configurator"
    ...    2. Set Asset Context for Product Configurator
    ...    3. Enable the Constraints Engine toggle (requires page reload after step 1)
    ...    All must be done before constraint model data can be imported.
    Open Revenue Settings Page
    # 1. Set Default Transaction Type
    Scroll To Transaction Processing Section
    Set Default Transaction Type    ${DEFAULT_TRANSACTION_TYPE_VALUE}
    Sleep    2s    reason=Allow page to update after transaction type change
    Dismiss Toast If Present
    # 2. Set Asset Context for Product Configurator
    Set Asset Context Picklist    ${ASSET_CONTEXT}
    Dismiss Toast If Present
    # 3. Reload page and enable Constraints Engine toggle
    Reload Revenue Settings Page
    Enable Constraints Engine Toggle
    Log    Constraints settings configured: Default Transaction Type = ${DEFAULT_TRANSACTION_TYPE_VALUE}, Asset Context = ${ASSET_CONTEXT}, Constraints Engine toggle enabled.

*** Keywords ***
Reload Revenue Settings Page
    [Documentation]    Reloads the Revenue Settings page and waits for it to render.
    ...    The Constraints Engine toggle section only renders after the Default
    ...    Transaction Type is set to "Advanced Configurator".
    Reload Page
    Sleep    3s    reason=Allow page to fully reload
    Wait Until Page Contains Element    css:body    timeout=20s
    Sleep    2s    reason=Allow Lightning to finish rendering

Scroll To Transaction Processing Section
    [Documentation]    Scroll down the Revenue Settings page until the "Transaction processing"
    ...    section is visible so the Default Transaction Type dropdown can be interacted with.
    ${section}=    Set Variable    xpath=//*[contains(normalize-space(.), 'Transaction processing for quotes and orders')]
    Wait Until Keyword Succeeds    15s    2s    _Scroll To Element    ${section}
    Sleep    1s    reason=Allow section to render

Enable Constraints Engine Toggle
    [Documentation]    Finds and enables the Constraints Engine toggle. First checks if the
    ...    toggle text exists on the page (it may not if the page was not reloaded after
    ...    setting the transaction type). Uses JavaScript shadow DOM traversal to both
    ...    detect the toggle's checked state and click it if needed. The toggle's checked
    ...    property is read directly for accurate state detection (ambient page text is
    ...    unreliable since many other features show "Enabled").
    # Verify the Constraints Engine section exists on the page
    ${page_has_toggle}=    Run Keyword And Return Status    Wait Until Page Contains    Constraints Engine    timeout=15s
    IF    not ${page_has_toggle}
        Capture Page Screenshot
        Fail    msg="Constraints Engine" text not found on Revenue Settings page. Ensure Default Transaction Type is set to "Advanced Configurator" and the page was reloaded.
    END
    # Detect state AND click in one JS call via shadow DOM traversal.
    # Returns 'already_enabled', 'clicked', or 'not_found'.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function findInShadows(root, name) {
    ...            var el = root.querySelector("input[name='" + name + "']");
    ...            if (el) return el;
    ...            var all = root.querySelectorAll("*");
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot) {
    ...                    var r = findInShadows(all[i].shadowRoot, name);
    ...                    if (r) return r;
    ...                }
    ...            }
    ...            return null;
    ...        }
    ...        var el = document.querySelector("input[name='advancedConfiguratorPrefEnabled']")
    ...                 || findInShadows(document.body, 'advancedConfiguratorPrefEnabled');
    ...        if (!el) return 'not_found';
    ...        if (el.checked) return 'already_enabled';
    ...        el.scrollIntoView({block:'center'});
    ...        el.click();
    ...        return 'clicked';
    ...    })()
    Log    Constraints Engine toggle JS result: ${result}
    IF    "${result}" == "already_enabled"
        Log    Constraints Engine toggle is already Enabled. No click needed.
        Capture Page Screenshot
    ELSE IF    "${result}" == "clicked"
        Sleep    3s    reason=Allow toggle state to update after click
        Capture Page Screenshot
        Log    Constraints Engine toggle clicked and should now be Enabled.
    ELSE
        Log    WARNING: Constraints Engine toggle input (advancedConfiguratorPrefEnabled) not found via shadow DOM traversal. Check manually.    WARN
        Capture Page Screenshot
    END

Set Asset Context Picklist
    [Documentation]    Sets the "Set Up Asset Context for Product Configurator" picklist.
    ...    Uses the same <li>-scoped approach as configure_revenue_settings: all XPath
    ...    selectors are scoped to the specific <li> setup-assistant step that contains
    ...    the "Set Up Asset Context" title, preventing cross-section interference.
    ...
    ...    Flow:
    ...    1. Scroll to step title and click to expand the content area
    ...    2. Check if pill shows correct value → skip
    ...    3. Clear pill if wrong value
    ...    4. Find <select> or combobox within the <li> and set value
    [Arguments]    ${target_value}
    ${step_li}=    Set Variable    xpath=//li[.//span[contains(normalize-space(text()), 'Set Up Asset Context')]]
    ${title_span}=    Set Variable    xpath=//span[contains(normalize-space(text()), 'Set Up Asset Context')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${title_span}
    IF    not ${found}
        Log    WARNING: "Set Up Asset Context" not found on page. Skipping.    WARN
        RETURN
    END
    Sleep    1s
    Click Element    ${title_span}
    Sleep    2s    reason=Allow step content to render after expand
    # Check if pill already shows correct value (scoped to this <li>)
    ${pill_label}=    Set Variable    ${step_li}//span[contains(@class, 'slds-pill__label')]
    ${has_pill}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${pill_label}    timeout=5s
    IF    ${has_pill}
        ${pill_text}=    Get Text    ${pill_label}
        ${correct}=    Run Keyword And Return Status    Should Contain    ${pill_text}    ${target_value}
        IF    ${correct}
            Log    Asset Context already set to "${target_value}". No change needed.
            RETURN
        END
        # Wrong value - clear the pill (scoped to this <li>)
        Log    Asset Context has wrong value "${pill_text}". Clearing pill.
        ${pill_area}=    Set Variable    ${step_li}//span[contains(@class, 'slds-pill')]
        Mouse Over    ${pill_area}
        Sleep    1s    reason=Reveal X button on hover
        ${remove_btn}=    Set Variable    ${step_li}//button[contains(@class, 'pill__rem') or contains(@class, 'slds-pill__remove')]
        ${btn_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${remove_btn}    timeout=5s
        IF    ${btn_found}
            Click Element    ${remove_btn}
            Sleep    2s    reason=Allow pill to clear and dropdown to appear
        END
    END
    Capture Page Screenshot
    # Try native <select> within this specific <li>
    ${select_el}=    Set Variable    ${step_li}//select
    ${is_select}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s    reason=Allow selection to persist
        Capture Page Screenshot
        Log    Asset Context set to "${target_value}" (native select).
        RETURN
    END
    # Try combobox with role='combobox' within this <li>
    ${cb_trigger}=    Set Variable    ${step_li}//*[@role='combobox' or contains(@class, 'slds-combobox')]
    ${is_cb}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${cb_trigger}    timeout=5s
    IF    ${is_cb}
        Scroll Element Into View    ${cb_trigger}
        Sleep    0.5s
        Click Element    ${cb_trigger}
        Sleep    2s    reason=Allow dropdown to populate
        Capture Page Screenshot
        ${option}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${target_value}')])[1]
        ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=10s
        IF    not ${opt_found}
            ${option}=    Set Variable    ${step_li}//*[contains(normalize-space(text()), '${target_value}')]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    ${opt_found}
            Click Element    ${option}
            Sleep    2s    reason=Allow selection to apply
            Capture Page Screenshot
            Log    Asset Context set to "${target_value}" (combobox).
            RETURN
        ELSE
            Log    WARNING: Option "${target_value}" not found in Asset Context dropdown.    WARN
            Press Keys    ${cb_trigger}    ESCAPE
        END
    END
    # Fallback: retry by clicking title again
    Log    No dropdown found on first attempt for Asset Context. Retrying.    WARN
    Click Element    ${title_span}
    Sleep    3s
    ${is_select2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select2}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s
        Capture Page Screenshot
        Log    Asset Context set to "${target_value}" (native select, retry).
        RETURN
    END
    Log    WARNING: Could not set Asset Context to "${target_value}". No interactive element found.    WARN
    Capture Page Screenshot

Dismiss Toast If Present
    [Documentation]    Clicks the close button on any visible Salesforce toast messages.
    ${close_btns}=    Get WebElements    xpath=//button[contains(@class, 'toastClose') or (@title='Close' and ancestor::*[contains(@class, 'toast')])]
    FOR    ${btn}    IN    @{close_btns}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${btn}
        Run Keyword If    ${visible}    Click Element    ${btn}
    END
    Sleep    0.5s

_Scroll To Element
    [Arguments]    ${locator}
    ${present}=    Run Keyword And Return Status    Get WebElement    ${locator}
    Run Keyword If    not ${present}    Execute JavaScript    window.scrollBy(0, 500)
    Run Keyword If    not ${present}    Sleep    0.5s
    Wait Until Element Is Visible    ${locator}    timeout=5s
    Scroll Element Into View    ${locator}

Set Default Transaction Type
    [Documentation]    Sets the "Default Transaction Type" dropdown on Revenue Settings to the
    ...    specified value. Handles both native <select> and Lightning combobox elements.
    ...    Skips if already set to the target value.
    [Arguments]    ${target_value}
    # Try native <select> first
    ${is_native}=    _Try Native Select    ${target_value}
    Return From Keyword If    ${is_native}
    # Fall back to Lightning combobox click approach
    _Set Via Lightning Combobox    ${target_value}

_Try Native Select
    [Documentation]    Attempts to find and use a native <select> element. Returns True if successful.
    [Arguments]    ${target_value}
    ${locator}=    _Find Native Select
    Return From Keyword If    """${locator}""" == "NONE"    ${False}
    Scroll Element Into View    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=10s
    ${current}=    Get Selected List Label    ${locator}
    ${current_stripped}=    Strip String    ${current}
    ${target_stripped}=    Strip String    ${target_value}
    ${already_set}=    Evaluate    $current_stripped == $target_stripped
    Run Keyword If    ${already_set}    Log    Default Transaction Type is already "${target_value}". No change needed.
    Return From Keyword If    ${already_set}    ${True}
    Select From List By Label    ${locator}    ${target_value}
    Sleep    2s    reason=Allow selection to persist
    ${updated}=    Get Selected List Label    ${locator}
    ${updated_stripped}=    Strip String    ${updated}
    Should Be Equal    ${updated_stripped}    ${target_stripped}
    ...    msg=Failed to set Default Transaction Type to "${target_value}" (got "${updated_stripped}")
    Log    Default Transaction Type set to "${target_value}" (native select).
    RETURN    ${True}

_Find Native Select
    [Documentation]    Looks for a native <select> element near the Default Transaction Type label.
    ...    Removed the broad css:select fallback to prevent matching unrelated <select>
    ...    elements (e.g. from other sections on the same page).
    # Strategy 1: select following the label text
    ${loc1}=    Set Variable    xpath=(//*[contains(normalize-space(.), 'Default Transaction Type')]/following::select)[1]
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${loc1}    timeout=8s
    Return From Keyword If    ${found}    ${loc1}
    # Strategy 2: select inside ancestor container
    ${loc2}=    Set Variable    xpath=(//*[contains(normalize-space(.), 'Default Transaction Type')]/ancestor::*[.//select][1]//select)[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${loc2}
    Return From Keyword If    ${found}    ${loc2}
    RETURN    NONE

_Set Via Lightning Combobox
    [Documentation]    Handle Lightning combobox (non-native select). Clicks the combobox button
    ...    to open the dropdown, then clicks the target option.
    [Arguments]    ${target_value}
    # Find the combobox button near "Default Transaction Type"
    ${combobox}=    Set Variable    xpath=(//*[contains(normalize-space(.), 'Default Transaction Type')]/following::*[@role='combobox' or contains(@class, 'slds-combobox')])[1]
    ${button}=    Set Variable    xpath=(//*[contains(normalize-space(.), 'Default Transaction Type')]/following::button[contains(@class, 'combobox') or @role='combobox' or @aria-haspopup='listbox'])[1]
    # Try combobox role element first
    ${found_combo}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${combobox}    timeout=8s
    Run Keyword If    ${found_combo}    Run Keywords    Scroll Element Into View    ${combobox}    AND    Click Element    ${combobox}
    # Try button if combobox role wasn't found
    Run Keyword If    not ${found_combo}    Run Keywords    Wait Until Element Is Visible    ${button}    timeout=8s    AND    Scroll Element Into View    ${button}    AND    Click Element    ${button}
    Sleep    1s    reason=Allow dropdown to open
    # Click the target option
    ${option}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${target_value}')])[1]
    Wait Until Element Is Visible    ${option}    timeout=10s
    Click Element    ${option}
    Sleep    2s    reason=Allow selection to persist
    Log    Default Transaction Type set to "${target_value}" (Lightning combobox).
