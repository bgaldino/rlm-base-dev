*** Settings ***
Documentation     Configure Revenue Settings page: set default procedures (Pricing,
...               Usage Rating), enable Instant Pricing, and set the Create Orders
...               and Create Contracts from Quote screen flows. Must run after all data and metadata has
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
${CREATE_ORDERS_FLOW}                   RLM_CreateOrdersFromQuote
${CREATE_CONTRACTS_FLOW}                ${EMPTY}
${MANAGE_ASSETS_FLOW}                   ${EMPTY}

*** Test Cases ***
Configure Revenue Settings
    [Documentation]    Navigates to Revenue Settings and configures:
    ...    1. Set Up Salesforce Pricing (combobox-recipe in setup assistant step)
    ...    2. Set Up Usage Rating (combobox-recipe in setup assistant step)
    ...    3. Enable Instant Pricing toggle
    ...    4. Set Up Flow for Creating Orders from Quotes (text + Save)
    ...    5. Set Up Flow for Creating Contracts from Quotes (text + Save, conditional)
    ...    6. Set Up Flow for Managing Assets (text + Save, conditional)
    # Open Browser For Setup ends with Maximize Browser Window, which in headless
    # Chrome shrinks the window to the 800x600 default screen. At that width the
    # procedure pill's remove button straddles the viewport's right edge and a
    # Selenium click on it is intercepted.
    Set Window Size    1920    1080
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
    Dismiss Toast If Present
    IF    $CREATE_CONTRACTS_FLOW != ""
        Set Create Contracts Flow    ${CREATE_CONTRACTS_FLOW}
        Dismiss Toast If Present
    END
    IF    $MANAGE_ASSETS_FLOW != ""
        Set Manage Assets Flow    ${MANAGE_ASSETS_FLOW}
        Dismiss Toast If Present
    END
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
    ...    3. Check if a pill already shows exactly the target value → skip
    ...    4. If wrong pill, clear it (the platform saves the empty value at once)
    ...    5. Find and use the <select> or combobox dropdown to set the value
    ...
    ...    Names are compared exactly, never by substring: a clone named
    ...    "<procedure> Clone" must not pass for "<procedure>", or the reverse.
    ...    Fails if it cleared a pill and could not set the new value, since that
    ...    leaves the org with no procedure for the step.
    [Arguments]    ${step_title}    ${target_value}
    ${cleared}=    Set Variable    ${False}
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
        ${pill_text}=    Strip String    ${pill_text}
        IF    $pill_text == $target_value.strip()
            Log    "${step_title}" already set to "${target_value}". No change needed.
            RETURN
        END
        # Wrong value - clear the pill (scoped to this <li>)
        Log    "${step_title}" has wrong value "${pill_text}". Clearing pill.
        _Remove Pill In Step    ${step_li}    ${step_title}
        ${cleared}=    Set Variable    ${True}
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
        # Exact text match: contains() would pick "<name> Clone" for "<name>".
        ${option}=    Set Variable    xpath=(//*[@role='option' and normalize-space(.)='${target_value}'])[1]
        ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=10s
        IF    not ${opt_found}
            # Try lightning-base-combobox-item
            ${option}=    Set Variable    xpath=(//lightning-base-combobox-item[normalize-space(.)='${target_value}'])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    not ${opt_found}
            # Try any element in a listbox
            ${option}=    Set Variable    xpath=(//*[@role='listbox']//*[normalize-space(text())='${target_value}'])[1]
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    not ${opt_found}
            # Try any link/span in the step li that appeared after click
            ${option}=    Set Variable    ${step_li}//*[normalize-space(text())='${target_value}']
            ${opt_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option}    timeout=5s
        END
        IF    ${opt_found}
            Click Element    ${option}
            Sleep    2s    reason=Allow selection to apply
            Capture Page Screenshot
            _Pill In Step Should Be    ${step_li}    ${step_title}    ${target_value}
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
        ${option2}=    Set Variable    xpath=(//*[@role='option' and normalize-space(.)='${target_value}'])[1]
        ${opt_found2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${option2}    timeout=10s
        IF    ${opt_found2}
            Click Element    ${option2}
            Sleep    2s
            Capture Page Screenshot
            _Pill In Step Should Be    ${step_li}    ${step_title}    ${target_value}
            Log    "${step_title}" set to "${target_value}" (combobox, retry).
            RETURN
        END
    END
    Capture Page Screenshot
    IF    ${cleared}
        Fail    Cleared "${step_title}" but could not set it to "${target_value}"; the org now has no value for this step.
    END
    Log    WARNING: Could not set "${step_title}" to "${target_value}". No interactive element found.    WARN

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
    Set Flow Text Input In Step    Set Up Flow for Creating Orders from Quotes    ${flow_api_name}    Create Orders Flow

Set Create Contracts Flow
    [Documentation]    Sets the "Set Up Flow for Creating Contracts from Quotes" text field
    ...    to the specified flow API name and clicks Save. This section uses the
    ...    same contract-price-flow-input component pattern as the ARC Assets flow.
    [Arguments]    ${flow_api_name}
    Set Flow Text Input In Step    Set Up Flow for Creating Contracts from Quotes    ${flow_api_name}    Create Contracts Flow

Set Manage Assets Flow
    [Documentation]    Sets the "Set Up Flow for Managing Assets" text field
    ...    to the specified flow API name and clicks Save. Same pattern as
    ...    Set Create Orders Flow but targets the ARC flow input section.
    [Arguments]    ${flow_api_name}
    Set Flow Text Input In Step    Set Up Flow for Managing Assets    ${flow_api_name}    Manage Assets Flow

Set Flow Text Input In Step
    [Documentation]    Sets a Revenue Settings text input inside a setup-assistant <li>.
    ...    Uses JavaScript value assignment and button click so the sticky Setup
    ...    search header cannot intercept Selenium clicks after scrollIntoView.
    [Arguments]    ${step_title}    ${flow_api_name}    ${log_label}
    ${step_li}=    Set Variable    xpath=//li[.//span[contains(normalize-space(text()), '${step_title}')]]
    ${title_span}=    Set Variable    xpath=//span[contains(normalize-space(text()), '${step_title}')]
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${title_span}
    IF    not ${found}
        Log    WARNING: "${step_title}" section not found. Skipping.    WARN
        RETURN
    END
    Sleep    1s
    ${input}=    Set Variable    ${step_li}//input[@type='text' and not(@role='combobox')]
    ${input_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${input}    timeout=10s
    IF    not ${input_found}
        Log    WARNING: Could not find input field for "${step_title}". Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    ${input_el}=    Get WebElement    ${input}
    Execute JavaScript    arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});
    ...    ARGUMENTS    ${input_el}
    ${current}=    Get Value    ${input}
    ${current_stripped}=    Strip String    ${current}
    ${target_stripped}=    Strip String    ${flow_api_name}
    IF    $current_stripped == $target_stripped
        Log    ${log_label} is already set to "${flow_api_name}". No change needed.
        RETURN
    END
    Execute JavaScript
    ...    var input = arguments[0], value = arguments[1];
    ...    var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    ...    setter.call(input, value);
    ...    input.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
    ...    input.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
    ...    input.blur();
    ...    ARGUMENTS    ${input_el}    ${flow_api_name}
    Sleep    1s
    ${save_btn}=    Set Variable    ${step_li}//button[normalize-space(.)='Save']
    ${save_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${save_btn}    timeout=10s
    IF    not ${save_found}
        Log    WARNING: Could not find Save button for ${log_label}. Skipping.    WARN
        Capture Page Screenshot
        RETURN
    END
    ${save_el}=    Get WebElement    ${save_btn}
    Execute JavaScript
    ...    arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});
    ...    arguments[0].click();
    ...    ARGUMENTS    ${save_el}
    Sleep    3s    reason=Allow save to complete
    Capture Page Screenshot
    Log    ${log_label} set to "${flow_api_name}" and saved.

_Remove Pill In Step
    [Documentation]    Removes the procedure pill in a setup-assistant step with a JavaScript
    ...    click, then waits for the pill to go. A Selenium click can land outside
    ...    the rendered content when the button sits at the viewport's edge
    ...    (ElementClickInterceptedException). The platform saves the empty value as
    ...    soon as the pill is removed.
    [Arguments]    ${step_li}    ${step_title}
    ${remove_btn}=    Set Variable    ${step_li}//button[contains(@class, 'slds-pill__remove')]
    ${btn_found}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${remove_btn}    timeout=5s
    IF    not ${btn_found}
        Capture Page Screenshot
        Fail    Could not find the remove button on the "${step_title}" pill.
    END
    ${btn_el}=    Get WebElement    ${remove_btn}
    Execute JavaScript
    ...    arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});
    ...    arguments[0].click();
    ...    ARGUMENTS    ${btn_el}
    Wait Until Page Does Not Contain Element    ${step_li}//span[contains(@class, 'slds-pill__label')]
    ...    timeout=10s    error=The "${step_title}" pill was still present 10s after its remove button was clicked.
    Sleep    1s    reason=Allow the combobox to render in place of the pill

_Pill In Step Should Be
    [Documentation]    Fails unless the step's pill reads exactly the expected value.
    [Arguments]    ${step_li}    ${step_title}    ${expected}
    ${pill_label}=    Set Variable    ${step_li}//span[contains(@class, 'slds-pill__label')]
    ${shown}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${pill_label}    timeout=10s
    IF    not ${shown}
        Fail    No pill appeared in "${step_title}" after selecting "${expected}".
    END
    ${pill_text}=    Get Text    ${pill_label}
    ${pill_text}=    Strip String    ${pill_text}
    IF    $pill_text != $expected.strip()
        Fail    "${step_title}" shows "${pill_text}" after selecting "${expected}".
    END

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
