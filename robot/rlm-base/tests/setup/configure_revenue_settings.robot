*** Settings ***
Documentation     Configure Revenue Settings page: set default procedures (Pricing,
...               Usage Rating), enable Instant Pricing, and set the Create Orders
...               from Quote screen flow. Must run after all data and metadata has
...               been deployed and before decision table refresh. Asset Context is
...               configured separately via enable_constraints_settings.
...
...               The Pricing and Usage Rating fields are inside an LWC component
...               (runtime_revenue_admin_console-rev-lifecycle-mgmt-settings) that uses
...               synthetic shadow DOM. Each field lives in an <li> setup-assistant step.
...               When not set, the step content area is empty until expanded. When set,
...               it shows a pill. All selectors are scoped to the parent <li> to avoid
...               cross-section interference (preventing accidental Asset Context changes).
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                            ${EMPTY}
${REVENUE_SETTINGS_URL}                 ${EMPTY}
${MANUAL_LOGIN_WAIT}                    90s
${PRICING_PROCEDURE}                    RLM Revenue Management Default Pricing Procedure
${USAGE_RATING_PROCEDURE}               RLM Default Rating Discovery Procedure
${CREATE_ORDERS_FLOW}                   RC_CreateOrdersFromQuote

*** Test Cases ***
Configure Revenue Settings
    [Documentation]    Navigates to Revenue Settings and configures:
    ...    1. Set Up Salesforce Pricing (combobox-recipe in setup assistant step)
    ...    2. Set Up Usage Rating (combobox-recipe in setup assistant step)
    ...    3. Enable Instant Pricing toggle
    ...    4. Set Up Flow for Creating Orders from Quotes (text + Save)
    Open Revenue Settings Page
    Set Procedure Field    Set Up Salesforce Pricing    ${PRICING_PROCEDURE}
    Dismiss Toast If Present
    # Reload the page to ensure a clean state for Usage Rating; selecting a procedure
    # value can leave the page in a transitional state where subsequent comboboxes
    # don't populate their options.
    Reload Page
    Sleep    5s    reason=Allow page to fully reload after Pricing selection
    Wait Until Page Contains Element    css:body    timeout=20s
    Sleep    2s    reason=Allow Lightning to finish rendering
    Set Procedure Field    Set Up Usage Rating    ${USAGE_RATING_PROCEDURE}
    Dismiss Toast If Present
    Enable Instant Pricing Toggle
    Dismiss Toast If Present
    Set Create Orders Flow    ${CREATE_ORDERS_FLOW}
    Capture Page Screenshot
    Log    Revenue Settings configured successfully.

*** Keywords ***
Set Procedure Field
    [Documentation]    Sets a procedure combobox-recipe field on Revenue Settings.
    ...    Each field lives in its own <li> element within the setup assistant.
    ...    All XPath selectors are scoped to the specific <li> that contains the
    ...    step title, preventing cross-section interference with other fields
    ...    like Asset Context.
    ...
    ...    Flow:
    ...    1. Scroll to the step title to trigger lazy rendering of step content
    ...    2. Click the step title to expand/toggle the content area
    ...    3. Check if a pill already shows the correct value → skip
    ...    4. If wrong pill, clear it
    ...    5. Find and use the <select> or combobox dropdown to set the value
    [Arguments]    ${step_title}    ${target_value}
    # Find the step LI element that contains this title
    ${step_li}=    Set Variable    xpath=//li[.//span[contains(normalize-space(text()), '${step_title}')]]
    # Scroll to step title to trigger rendering
    ${title_span}=    Set Variable    xpath=//span[contains(normalize-space(text()), '${step_title}')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${title_span}
    IF    not ${found}
        Log    WARNING: "${step_title}" not found on page. Skipping.    WARN
        RETURN
    END
    Sleep    1s
    # Click the step title to expand the content area
    Click Element    ${title_span}
    Sleep    2s    reason=Allow step content to render after expand
    # Check if pill already shows the correct value (scoped to this <li>)
    ${pill_label}=    Set Variable    ${step_li}//span[contains(@class, 'slds-pill__label')]
    ${has_pill}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${pill_label}    timeout=5s
    IF    ${has_pill}
        ${pill_text}=    Get Text    ${pill_label}
        ${correct}=    Run Keyword And Return Status    Should Contain    ${pill_text}    ${target_value}
        IF    ${correct}
            Log    "${step_title}" already set to "${target_value}". No change needed.
            RETURN
        END
        # Wrong value - clear the pill (scoped to this <li>)
        Log    "${step_title}" has wrong value "${pill_text}". Clearing pill.
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
    # Try to find a native <select> within this specific <li>
    ${select_el}=    Set Variable    ${step_li}//select
    ${is_select}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s    reason=Allow selection to persist
        Capture Page Screenshot
        Log    "${step_title}" set to "${target_value}" (native select).
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
        # Search for the target option using multiple patterns
        ${option}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${target_value}')])[1]
        ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=10s
        IF    not ${opt_found}
            # Try lightning-base-combobox-item
            ${option}=    Set Variable    xpath=(//lightning-base-combobox-item[contains(normalize-space(.), '${target_value}')])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    not ${opt_found}
            # Try any element in a listbox
            ${option}=    Set Variable    xpath=(//*[@role='listbox']//*[contains(normalize-space(text()), '${target_value}')])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    not ${opt_found}
            # Try any link/span in the step li that appeared after click
            ${option}=    Set Variable    ${step_li}//*[contains(normalize-space(text()), '${target_value}')]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    ${opt_found}
            Click Element    ${option}
            Sleep    2s    reason=Allow selection to apply
            Capture Page Screenshot
            Log    "${step_title}" set to "${target_value}" (combobox).
            RETURN
        ELSE
            # Log all visible options for debugging
            ${all_opts}=    Execute JavaScript
            ...    return (function(){
            ...        var opts = document.querySelectorAll('[role="option"]');
            ...        var result = [];
            ...        for (var i = 0; i < opts.length; i++) {
            ...            if (opts[i].offsetParent !== null) result.push(opts[i].textContent.trim().substring(0,80));
            ...        }
            ...        return 'visible_options:[' + result.join('|') + '] total=' + opts.length;
            ...    })()
            Log    WARNING: Option "${target_value}" not found for "${step_title}". ${all_opts}    WARN
            Press Keys    ${cb_trigger}    ESCAPE
        END
    END
    # Fallback: try clicking the step title again and re-check
    Log    No dropdown found on first attempt. Clicking step title again.    WARN
    Click Element    ${title_span}
    Sleep    3s    reason=Retry: allow content to render
    ${is_select2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${select_el}    timeout=8s
    IF    ${is_select2}
        Scroll Element Into View    ${select_el}
        Sleep    0.5s
        Select From List By Label    ${select_el}    ${target_value}
        Sleep    2s
        Capture Page Screenshot
        Log    "${step_title}" set to "${target_value}" (native select, retry).
        RETURN
    END
    ${is_cb2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${cb_trigger}    timeout=5s
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
            Log    "${step_title}" set to "${target_value}" (combobox, retry).
            RETURN
        END
    END
    Log    WARNING: Could not set "${step_title}" to "${target_value}". No interactive element found.    WARN
    Capture Page Screenshot

Enable Instant Pricing Toggle
    [Documentation]    Enables the Instant Pricing toggle on Revenue Settings.
    ...    Uses JavaScript shadow DOM traversal to detect state and click.
    ${section}=    Set Variable    xpath=//*[normalize-space(text())='Instant Pricing']
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section}
    IF    not ${found}
        Log    WARNING: "Instant Pricing" section not found on page. Skipping.    WARN
        RETURN
    END
    Sleep    1s
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
    ...        var el = document.querySelector("input[name='instantPricingEnabled']")
    ...                 || findInShadows(document.body, 'instantPricingEnabled');
    ...        if (!el) return 'not_found';
    ...        if (el.checked) return 'already_enabled';
    ...        el.scrollIntoView({block:'center'});
    ...        el.click();
    ...        return 'clicked';
    ...    })()
    Log    Instant Pricing toggle JS result: ${result}
    IF    "${result}" == "already_enabled"
        Log    Instant Pricing toggle is already Enabled. No click needed.
    ELSE IF    "${result}" == "clicked"
        Sleep    3s    reason=Allow toggle state to update after click
        Capture Page Screenshot
        Log    Instant Pricing toggle clicked and should now be Enabled.
    ELSE
        Log    WARNING: Instant Pricing toggle input (instantPricingEnabled) not found. Check manually.    WARN
        Capture Page Screenshot
    END

Set Create Orders Flow
    [Documentation]    Sets the "Set Up Flow for Creating Orders from Quotes" text field
    ...    to the specified flow API name and clicks Save.
    [Arguments]    ${flow_api_name}
    ${section}=    Set Variable    xpath=//*[contains(normalize-space(text()), 'Set Up Flow for Creating Orders from Quotes')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section}
    IF    not ${found}
        Log    WARNING: "Set Up Flow for Creating Orders from Quotes" section not found. Skipping.    WARN
        RETURN
    END
    Sleep    1s
    ${input}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Creating Orders from Quotes')]/following::input[@type='text' or (not(@type) and not(@role='switch'))])[1]
    ${input_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${input}    timeout=10s
    IF    not ${input_found}
        ${input}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Creating Orders from Quotes')]/following::input[not(@type='checkbox') and not(@role='switch') and not(@type='hidden')])[1]
        ${input_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${input}    timeout=5s
    END
    IF    not ${input_found}
        Log    WARNING: Could not find input field for "Set Up Flow for Creating Orders from Quotes". Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    Scroll Element Into View    ${input}
    ${current}=    Get Value    ${input}
    ${current_stripped}=    Strip String    ${current}
    ${target_stripped}=    Strip String    ${flow_api_name}
    IF    $current_stripped == $target_stripped
        Log    Create Orders Flow is already set to "${flow_api_name}". No change needed.
        RETURN
    END
    Click Element    ${input}
    Press Keys    ${input}    CTRL+a    DELETE
    Input Text    ${input}    ${flow_api_name}
    Sleep    1s
    ${save_btn}=    Set Variable    xpath=(//*[contains(normalize-space(text()), 'Creating Orders from Quotes')]/following::button[normalize-space(.)='Save'])[1]
    ${save_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${save_btn}    timeout=10s
    IF    not ${save_found}
        ${save_btn}=    Set Variable    xpath=(//button[normalize-space(.)='Save'])[last()]
        ${save_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${save_btn}    timeout=5s
    END
    IF    not ${save_found}
        Log    WARNING: Could not find Save button. Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    Scroll Element Into View    ${save_btn}
    Click Element    ${save_btn}
    Sleep    3s    reason=Allow save to complete
    Capture Page Screenshot
    Log    Create Orders Flow set to "${flow_api_name}" and saved.

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
