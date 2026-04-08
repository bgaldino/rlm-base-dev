*** Settings ***
Documentation     Configure the Product Discovery Settings page: set the Default Catalog
...               to the specified catalog name. Must run after QB product catalog data
...               has been loaded (insert_quantumbit_pcm_data) so the catalog record
...               exists to be selected.
...
...               The "Select Default Catalog" field is a Lightning combobox. Selecting a
...               value auto-saves and triggers a "Default Catalog Updated" toast — no
...               explicit Save button is needed.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                    ${EMPTY}
${PRODUCT_DISCOVERY_URL}        ${EMPTY}
${MANUAL_LOGIN_WAIT}            90s
${DEFAULT_CATALOG}              QuantumBit Software

*** Test Cases ***
Configure Product Discovery Default Catalog
    [Documentation]    Navigates to Product Discovery Settings and sets the Default Catalog
    ...    to the value specified by ${DEFAULT_CATALOG}. Skips if the catalog is already set
    ...    to the correct value.
    Open Product Discovery Settings Page
    Set Default Catalog    ${DEFAULT_CATALOG}
    Dismiss Toast If Present
    Capture Page Screenshot
    Log    Product Discovery Settings: Default Catalog set to "${DEFAULT_CATALOG}".

*** Keywords ***
Open Product Discovery Settings Page
    [Documentation]    Opens the Product Discovery Settings setup page using sf org open
    ...    when ORG_ALIAS is set, or falls back to PRODUCT_DISCOVERY_URL.
    ${path}=    Set Variable    /lightning/setup/ProductDiscoverySettings/home
    Run Keyword If    """${ORG_ALIAS}""" != ""    Open Setup Page    ${path}
    ...    ELSE IF    """${PRODUCT_DISCOVERY_URL}""" != ""    Go To    ${PRODUCT_DISCOVERY_URL}
    ...    ELSE    Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or PRODUCT_DISCOVERY_URL
    Wait Until Page Contains Element    css:body    timeout=20s
    Sleep    2s    reason=Allow Lightning to finish rendering

Set Default Catalog
    [Documentation]    Sets the "Select Default Catalog" combobox on the Product Discovery
    ...    Settings page to the specified catalog name. The combobox auto-saves on selection.
    ...    Skips if the catalog is already set to the target value.
    [Arguments]    ${target_value}
    # Scroll to the "Select Default Catalog" section heading
    ${section_heading}=    Set Variable    xpath=//*[contains(normalize-space(text()), 'Select Default Catalog')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section_heading}
    IF    not ${found}
        Log    WARNING: "Select Default Catalog" section not found on page. Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    Sleep    1s
    # Check if a pill (selected value) already shows the correct catalog name
    ${pill_label}=    Set Variable    xpath=//span[contains(@class, 'slds-pill__label') and contains(normalize-space(.), '${target_value}')]
    ${has_correct_pill}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${pill_label}    timeout=5s
    IF    ${has_correct_pill}
        Log    Default Catalog is already set to "${target_value}". No change needed.
        RETURN
    END
    # If a different catalog is already selected, clear it first
    ${any_pill}=    Set Variable    xpath=//span[contains(@class, 'slds-pill__label')]
    ${has_pill}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${any_pill}    timeout=3s
    IF    ${has_pill}
        ${pill_text}=    Get Text    ${any_pill}
        Log    Existing Default Catalog is "${pill_text}". Clearing it.
        ${remove_btn}=    Set Variable    xpath=//button[contains(@class, 'pill__rem') or contains(@class, 'slds-pill__remove')]
        ${btn_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${remove_btn}    timeout=5s
        IF    ${btn_found}
            Mouse Over    ${any_pill}
            Sleep    1s    reason=Reveal X button on hover
            Click Element    ${remove_btn}
            Sleep    2s    reason=Allow pill to clear before dropdown appears
        END
    END
    Capture Page Screenshot
    # Try native <select> first
    ${select_el}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select Default Catalog')]/following::select)[1]
    ${is_select}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s    reason=Allow selection to persist
        Capture Page Screenshot
        Log    Default Catalog set to "${target_value}" (native select).
        RETURN
    END
    # Try Lightning combobox
    ${cb_trigger}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Select Default Catalog')]/following::*[@role='combobox' or contains(@class, 'slds-combobox')])[1]
    ${is_cb}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${cb_trigger}    timeout=8s
    IF    ${is_cb}
        Scroll Element Into View    ${cb_trigger}
        Sleep    0.5s
        Click Element    ${cb_trigger}
        Sleep    2s    reason=Allow dropdown options to populate
        Capture Page Screenshot
        # Try role=option first
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
            Sleep    2s    reason=Allow selection to apply and toast to appear
            Capture Page Screenshot
            Log    Default Catalog set to "${target_value}" (combobox).
            RETURN
        ELSE
            ${all_opts}=    Execute JavaScript
            ...    return (function(){
            ...        var opts = document.querySelectorAll('[role="option"]');
            ...        var result = [];
            ...        for (var i = 0; i < opts.length; i++) {
            ...            if (opts[i].offsetParent !== null) result.push(opts[i].textContent.trim().substring(0,80));
            ...        }
            ...        return 'visible_options:[' + result.join('|') + '] total=' + opts.length;
            ...    })()
            Log    WARNING: Option "${target_value}" not found in Default Catalog dropdown. ${all_opts}    WARN
            Press Keys    ${cb_trigger}    ESCAPE
        END
    END
    Log    WARNING: Could not set Default Catalog to "${target_value}". No interactive element found.    WARN
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
