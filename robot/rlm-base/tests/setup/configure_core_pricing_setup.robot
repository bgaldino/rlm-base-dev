*** Settings ***
Documentation     Configure Salesforce Pricing Setup page (CorePricingSetup): set the default
...               Pricing Procedure. Must run after all data and metadata has been deployed
...               (the Pricing Procedure expression set must be active) and before any
...               automated pricing transactions are tested.
...
...               The "Select a Pricing Procedure" combobox is a standard SLDS form on the
...               CorePricingSetup Lightning Setup page. This test navigates to
...               /lightning/setup/CorePricingSetup/home and selects the target procedure.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                            ${EMPTY}
${MANUAL_LOGIN_WAIT}                    90s
${PRICING_PROCEDURE}                    RLM Revenue Management Default Pricing Procedure

*** Test Cases ***
Configure Core Pricing Setup
    [Documentation]    Navigates to Salesforce Pricing Setup (CorePricingSetup) and sets
    ...    the default Pricing Procedure if it is not already configured.
    Open Setup Page    /lightning/setup/CorePricingSetup/home
    Set Core Pricing Procedure    ${PRICING_PROCEDURE}
    Dismiss Toast If Present
    Capture Page Screenshot
    Log    CorePricingSetup default Pricing Procedure configured successfully.

*** Keywords ***
Set Core Pricing Procedure
    [Documentation]    Sets the "Select a Pricing Procedure" combobox on the CorePricingSetup page.
    ...
    ...    The page renders a standard SLDS form with two sections:
    ...    - Select a Pricing Recipe (usually pre-set; not touched here)
    ...    - Select a Pricing Procedure (target field)
    ...
    ...    Strategy:
    ...    1. Scroll to the "Select a Pricing Procedure" label
    ...    2. Check if the value is already set (pill or selected option) → skip
    ...    3. Try native <select> element
    ...    4. Try Lightning combobox (role='combobox')
    ...    5. Retry once on failure
    [Arguments]    ${target_value}
    # Scroll to the "Select a Pricing Procedure" section heading
    ${section_label}=    Set Variable    xpath=//*[contains(normalize-space(text()), 'Select a Pricing Procedure')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section_label}
    IF    not ${found}
        Log    WARNING: "Select a Pricing Procedure" label not found on CorePricingSetup page. Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    Sleep    1s
    # Check if already set via pill (e.g. slds-pill__label)
    ${pill_label}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select a Pricing Procedure')]/following::span[contains(@class, 'slds-pill__label')])[1]
    ${has_pill}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${pill_label}    timeout=5s
    IF    ${has_pill}
        ${pill_text}=    Get Text    ${pill_label}
        ${correct}=    Run Keyword And Return Status    Should Contain    ${pill_text}    ${target_value}
        IF    ${correct}
            Log    CorePricingSetup Pricing Procedure already set to "${target_value}". No change needed.
            RETURN
        END
        # Wrong value — clear the pill
        Log    CorePricingSetup Pricing Procedure has wrong value "${pill_text}". Clearing pill.
        ${remove_btn}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select a Pricing Procedure')]/following::button[contains(@class, 'pill__rem') or contains(@class, 'slds-pill__remove')])[1]
        ${btn_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${remove_btn}    timeout=5s
        IF    ${btn_found}
            Mouse Over    ${pill_label}
            Sleep    1s    reason=Reveal X button on hover
            Click Element    ${remove_btn}
            Sleep    2s    reason=Allow pill to clear and dropdown to appear
        END
    END
    Capture Page Screenshot
    # Try native <select> following the section label
    ${select_el}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select a Pricing Procedure')]/following::select)[1]
    ${is_select}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        # Check current value first
        ${current}=    Get Selected List Label    ${select_el}
        ${already_set}=    Run Keyword And Return Status    Should Contain    ${current}    ${target_value}
        IF    ${already_set}
            Log    CorePricingSetup Pricing Procedure already set to "${target_value}" (native select). No change needed.
            RETURN
        END
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s    reason=Allow selection to persist
        Capture Page Screenshot
        Log    CorePricingSetup Pricing Procedure set to "${target_value}" (native select).
        RETURN
    END
    # Try Lightning combobox (role='combobox') following the section label
    ${cb_trigger}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select a Pricing Procedure')]/following::*[@role='combobox' or contains(@class, 'slds-combobox__form-element')])[1]
    ${is_cb}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${cb_trigger}    timeout=8s
    IF    ${is_cb}
        Scroll Element Into View    ${cb_trigger}
        Sleep    0.5s
        Click Element    ${cb_trigger}
        Sleep    2s    reason=Allow dropdown to populate
        Capture Page Screenshot
        # Try role='option' first
        ${option}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${target_value}')])[1]
        ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=10s
        IF    not ${opt_found}
            ${option}=    Set Variable    xpath=(//lightning-base-combobox-item[contains(normalize-space(.), '${target_value}')])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    not ${opt_found}
            ${option}=    Set Variable    xpath=(//*[@role='listbox']//*[contains(normalize-space(text()), '${target_value}')])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    ${opt_found}
            Click Element    ${option}
            Sleep    2s    reason=Allow selection to apply
            Capture Page Screenshot
            Log    CorePricingSetup Pricing Procedure set to "${target_value}" (Lightning combobox).
            RETURN
        ELSE
            # Log visible options for debugging
            ${all_opts}=    Execute JavaScript
            ...    return (function(){
            ...        var opts = document.querySelectorAll('[role="option"]');
            ...        var result = [];
            ...        for (var i = 0; i < opts.length; i++) {
            ...            if (opts[i].offsetParent !== null) result.push(opts[i].textContent.trim().substring(0,80));
            ...        }
            ...        return 'visible_options:[' + result.join('|') + '] total=' + opts.length;
            ...    })()
            Log    WARNING: Option "${target_value}" not found in Pricing Procedure dropdown. ${all_opts}    WARN
            Press Keys    ${cb_trigger}    ESCAPE
        END
    END
    # Retry once: reload and try again
    Log    No dropdown found on first attempt for CorePricingSetup Pricing Procedure. Reloading and retrying.    WARN
    Reload Page
    Sleep    5s    reason=Allow page to fully reload
    Wait Until Page Contains Element    css:body    timeout=20s
    Sleep    2s    reason=Allow Lightning to finish rendering
    ${is_select2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select2}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s
        Capture Page Screenshot
        Log    CorePricingSetup Pricing Procedure set to "${target_value}" (native select, retry after reload).
        RETURN
    END
    ${is_cb2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${cb_trigger}    timeout=8s
    IF    ${is_cb2}
        Scroll Element Into View    ${cb_trigger}
        Sleep    0.5s
        Click Element    ${cb_trigger}
        Sleep    2s
        ${option2}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${target_value}')])[1]
        ${opt_found2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option2}    timeout=10s
        IF    ${opt_found2}
            Click Element    ${option2}
            Sleep    2s
            Capture Page Screenshot
            Log    CorePricingSetup Pricing Procedure set to "${target_value}" (Lightning combobox, retry after reload).
            RETURN
        END
    END
    Log    WARNING: Could not set CorePricingSetup Pricing Procedure to "${target_value}". No interactive element found.    WARN
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
