*** Settings ***
Documentation     Configure Revenue Settings page: set default procedures (Pricing,
...               Usage Rating), enable Instant Pricing, and set the Create Orders
...               from Quote screen flow. Must run after all data and metadata has
...               been deployed and before decision table refresh. Asset Context is
...               configured separately via enable_constraints_settings.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                            ${EMPTY}
${REVENUE_SETTINGS_URL}                 ${EMPTY}
${MANUAL_LOGIN_WAIT}                    90s
# Picklist values for default procedures
${PRICING_PROCEDURE}                    RLM Revenue Management Default Pricing Procedure
${USAGE_RATING_PROCEDURE}               RLM Default Rating Discovery Procedure
# Flow field
${CREATE_ORDERS_FLOW}                   RC_CreateOrdersFromQuote

*** Test Cases ***
Configure Revenue Settings
    [Documentation]    Navigates to Revenue Settings and configures:
    ...    1. Set Up Salesforce Pricing (picklist/pill)
    ...    2. Set Up Usage Rating (picklist/pill)
    ...    3. Enable Instant Pricing toggle
    ...    4. Set Up Flow for Creating Orders from Quotes (text + Save)
    Open Revenue Settings Page
    # 1. Set Up Salesforce Pricing
    Set Picklist Field    Set Up Salesforce Pricing    ${PRICING_PROCEDURE}
    Dismiss Toast If Present
    # 2. Set Up Usage Rating
    Set Picklist Field    Set Up Usage Rating    ${USAGE_RATING_PROCEDURE}
    Dismiss Toast If Present
    # 3. Enable Instant Pricing
    Enable Instant Pricing Toggle
    Dismiss Toast If Present
    # 4. Set Create Orders Flow
    Set Create Orders Flow    ${CREATE_ORDERS_FLOW}
    Capture Page Screenshot
    Log    Revenue Settings configured successfully.

*** Keywords ***
Set Picklist Field
    [Documentation]    Sets a picklist field on the Revenue Settings page. These fields have
    ...    two UI states:
    ...    - NOT SET: A combobox/dropdown is visible with "Select an Option".
    ...    - ALREADY SET: The dropdown is replaced by a pill/chip showing the selected value,
    ...      with an X button (visible on hover) to clear it.
    ...    If the correct value is already set, skips. If a wrong value is set, clears the
    ...    pill first, then selects from the dropdown.
    [Arguments]    ${section_label}    ${target_value}
    # Scroll to the section
    ${section}=    Set Variable    xpath=//*[contains(normalize-space(text()), '${section_label}')]
    ${section_found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section}
    IF    not ${section_found}
        Log    WARNING: Section "${section_label}" not found on page. Skipping.    WARN
        RETURN
    END
    Sleep    1s
    # Check if the target value is already displayed in a pill/chip
    ${pill_with_value}=    _Has Pill With Value    ${section_label}    ${target_value}
    IF    ${pill_with_value}
        Log    "${section_label}" is already set to "${target_value}". No change needed.
        RETURN
    END
    # Check if ANY pill is present (wrong value set) and clear it
    ${has_any_pill}=    _Has Any Pill    ${section_label}
    IF    ${has_any_pill}
        Log    "${section_label}" has a different value set. Clearing to re-select.
        _Clear Pill    ${section_label}
        Sleep    2s    reason=Allow picklist to reappear after clearing pill
    END
    Capture Page Screenshot
    # Now the picklist/combobox should be visible - select the target value
    ${selected}=    _Select From Combobox    ${section_label}    ${target_value}
    IF    not ${selected}
        Log    WARNING: Could not set "${section_label}" to "${target_value}". The option may not exist in this org.    WARN
        Capture Page Screenshot
    END

_Has Pill With Value
    [Documentation]    Checks if a pill/chip displaying the target value exists near the section.
    ...    IMPORTANT: Uses a scoped ancestor container to avoid matching pills in adjacent sections
    ...    (e.g. Asset Context pill when looking for Usage Rating).
    [Arguments]    ${section_label}    ${target_value}
    # Find the nearest ancestor container that scopes this section
    ${container}=    _Get Section Container    ${section_label}
    IF    $container != 'NONE'
        ${area_text}=    Get Text    ${container}
        ${has}=    Run Keyword And Return Status    Should Contain    ${area_text}    ${target_value}
        RETURN    ${has}
    END
    # Fallback: look for pill within a narrow range (position <= 8 to stay within this section)
    ${pill}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::*[position() <= 8 and (contains(@class, 'pill') or contains(@class, 'selectedOption'))])[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${pill}
    IF    ${found}
        ${pill_text}=    Get Text    ${pill}
        ${has_value}=    Run Keyword And Return Status    Should Contain    ${pill_text}    ${target_value}
        RETURN    ${has_value}
    END
    RETURN    ${False}

_Has Any Pill
    [Documentation]    Checks if any pill/chip (with an X clear button) exists near the section.
    ...    IMPORTANT: Scoped to the section container to avoid matching pills from adjacent sections.
    [Arguments]    ${section_label}
    # Use the scoped container to check for pills
    ${container}=    _Get Section Container    ${section_label}
    IF    $container != 'NONE'
        ${clear_btn}=    Set Variable    ${container}//button[contains(@title, 'Remove') or contains(@title, 'Clear') or contains(@title, 'close') or contains(@class, 'pill__remove') or contains(@class, 'slds-pill__remove')]
        ${found}=    Run Keyword And Return Status    Get WebElement    ${clear_btn}
        RETURN    ${found}
    END
    # Fallback: narrow position-limited following:: to stay within current section
    ${clear_btn}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::button[position() <= 5 and (contains(@title, 'Remove') or contains(@title, 'Clear') or contains(@title, 'close') or contains(@class, 'pill__remove') or contains(@class, 'slds-pill__remove'))])[1]
    ${found}=    Run Keyword And Return Status    Get WebElement    ${clear_btn}
    RETURN    ${found}

_Clear Pill
    [Documentation]    Clears a pill/chip value by hovering to reveal the X button, then clicking it.
    ...    IMPORTANT: Scoped to the section container to avoid clearing pills from adjacent sections.
    [Arguments]    ${section_label}
    # Use scoped container to find the pill and clear button
    ${container}=    _Get Section Container    ${section_label}
    IF    $container != 'NONE'
        # Find pill within the container to hover over
        ${pill_area}=    Set Variable    ${container}//*[contains(@class, 'pill') or contains(@class, 'selectedOption') or contains(@class, 'slds-pill')]
        ${pill_found}=    Run Keyword And Return Status    Get WebElement    ${pill_area}
        Run Keyword If    ${pill_found}    Mouse Over    ${pill_area}
        Sleep    1s    reason=Allow X button to appear on hover
        # Find and click the clear button within the container
        ${clear_btn}=    Set Variable    ${container}//button[contains(@title, 'Remove') or contains(@title, 'Clear') or contains(@title, 'close') or contains(@class, 'pill__remove') or contains(@class, 'slds-pill__remove')]
        ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${clear_btn}    timeout=5s
        IF    ${found}
            Click Element    ${clear_btn}
            Sleep    1s
            Log    Cleared existing value for "${section_label}".
            RETURN
        END
        # Fallback within container: any close button icon
        ${x_btn}=    Set Variable    ${container}//button[.//lightning-primitive-icon or .//*[contains(@class,'close')]]
        ${x_found}=    Run Keyword And Return Status    Get WebElement    ${x_btn}
        IF    ${x_found}
            Mouse Over    ${x_btn}
            Sleep    0.5s
            Click Element    ${x_btn}
            Sleep    1s
            Log    Cleared existing value for "${section_label}" (fallback X button).
            RETURN
        END
    END
    # Last resort: narrow following:: with position limit
    ${pill_area}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::*[position() <= 8 and (contains(@class, 'pill') or contains(@class, 'selectedOption') or contains(@class, 'slds-pill'))])[1]
    ${pill_found}=    Run Keyword And Return Status    Get WebElement    ${pill_area}
    Run Keyword If    ${pill_found}    Mouse Over    ${pill_area}
    Sleep    1s    reason=Allow X button to appear on hover
    ${clear_btn}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::button[position() <= 5 and (contains(@title, 'Remove') or contains(@title, 'Clear') or contains(@title, 'close') or contains(@class, 'pill__remove') or contains(@class, 'slds-pill__remove'))])[1]
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${clear_btn}    timeout=5s
    IF    ${found}
        Click Element    ${clear_btn}
        Sleep    1s
        Log    Cleared existing value for "${section_label}".
    ELSE
        Log    WARNING: Could not find clear/remove button for "${section_label}".    WARN
    END

_Select From Combobox
    [Documentation]    Finds the combobox/dropdown near the section, clicks to open, selects target.
    [Arguments]    ${section_label}    ${target_value}
    # Find the combobox trigger
    ${trigger}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::*[@role='combobox' or contains(@class, 'slds-combobox')])[1]
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${trigger}    timeout=8s
    IF    not ${found}
        ${trigger}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::button[@aria-haspopup='listbox' or contains(@class, 'combobox')])[1]
        ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${trigger}    timeout=5s
    END
    IF    not ${found}
        ${trigger}=    Set Variable    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/following::*[contains(normalize-space(.), 'Select an Option') or contains(normalize-space(.), 'Select')])[1]
        ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${trigger}    timeout=5s
    END
    Return From Keyword If    not ${found}    ${False}
    # Click to open
    Scroll Element Into View    ${trigger}
    Sleep    0.5s
    Click Element    ${trigger}
    Sleep    2s    reason=Allow dropdown to populate
    Capture Page Screenshot
    # Find and click the target option
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
    IF    not ${opt_found}
        Log    WARNING: Option "${target_value}" not found in dropdown for "${section_label}".    WARN
        Press Keys    ${trigger}    ESCAPE
        Sleep    0.5s
        RETURN    ${False}
    END
    Click Element    ${option}
    Sleep    2s    reason=Allow selection to apply
    Capture Page Screenshot
    Log    "${section_label}" set to "${target_value}".
    RETURN    ${True}

Enable Instant Pricing Toggle
    [Documentation]    Enables the Instant Pricing toggle on Revenue Settings.
    ...    Uses JavaScript shadow DOM traversal to both detect state and click,
    ...    since setup toggles are Lightning Web Components inside Shadow DOM.
    ...    The toggle's checked property is read directly for accurate state detection.
    ${section}=    Set Variable    xpath=//*[normalize-space(text())='Instant Pricing']
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    20s    2s    _Scroll To Element    ${section}
    IF    not ${found}
        Log    WARNING: "Instant Pricing" section not found on page. Skipping.    WARN
        RETURN
    END
    Sleep    1s
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
        Log    WARNING: Instant Pricing toggle input (instantPricingEnabled) not found via shadow DOM traversal. Check manually.    WARN
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
    # Find the text input (exclude checkboxes/switches)
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
    # Check if already set
    ${current}=    Get Value    ${input}
    ${current_stripped}=    Strip String    ${current}
    ${target_stripped}=    Strip String    ${flow_api_name}
    IF    $current_stripped == $target_stripped
        Log    Create Orders Flow is already set to "${flow_api_name}". No change needed.
        RETURN
    END
    # Clear and type the new value
    Click Element    ${input}
    Press Keys    ${input}    CTRL+a    DELETE
    Input Text    ${input}    ${flow_api_name}
    Sleep    1s
    # Find and click Save
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
    [Documentation]    Clicks the close button on any visible Salesforce toast messages
    ...    to prevent them from intercepting clicks on page elements below.
    ${close_btns}=    Get WebElements    xpath=//button[contains(@class, 'toastClose') or (@title='Close' and ancestor::*[contains(@class, 'toast')])]
    FOR    ${btn}    IN    @{close_btns}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${btn}
        Run Keyword If    ${visible}    Click Element    ${btn}
    END
    Sleep    0.5s

_Get Section Container
    [Documentation]    Returns a WebElement XPath for the nearest ancestor container that scopes
    ...    a Revenue Settings section. This prevents pill/button searches from bleeding
    ...    into adjacent sections (e.g. Asset Context when looking for Usage Rating).
    ...    Returns 'NONE' if no suitable container is found.
    [Arguments]    ${section_label}
    # Try to find a containing div with a class that indicates a section boundary
    # Salesforce setup pages typically wrap each section in a card or form-element container
    @{ancestors}=    Create List
    ...    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/ancestor::div[contains(@class, 'slds-card') or contains(@class, 'card') or contains(@class, 'section') or contains(@class, 'form-element') or contains(@class, 'setup-content')])[last()]
    ...    xpath=(//*[contains(normalize-space(text()), '${section_label}')]/ancestor::div[position() <= 3])[last()]
    FOR    ${xpath}    IN    @{ancestors}
        ${found}=    Run Keyword And Return Status    Get WebElement    ${xpath}
        IF    ${found}
            RETURN    ${xpath}
        END
    END
    RETURN    NONE

_Scroll To Element
    [Arguments]    ${locator}
    ${present}=    Run Keyword And Return Status    Get WebElement    ${locator}
    Run Keyword If    not ${present}    Execute JavaScript    window.scrollBy(0, 500)
    Run Keyword If    not ${present}    Sleep    0.5s
    Wait Until Element Is Visible    ${locator}    timeout=5s
    Scroll Element Into View    ${locator}
