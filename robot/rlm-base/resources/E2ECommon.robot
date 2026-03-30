*** Settings ***
Documentation     Shared keywords for E2E functional tests. Provides navigation,
...               QuickAction interaction, async polling, and verification keywords.
...               QuickAction interaction, async polling, browser lifecycle management,
...               and verification keywords. Authentication is handled by the calling suite.
Library           SeleniumLibrary    timeout=15    implicit_wait=5
Library           Collections
Library           String
Library           Process
Library           DateTime
Library           ${EXECDIR}/robot/rlm-base/resources/WebDriverManager.py    WITH NAME    WebDriverManager
Library           ${EXECDIR}/robot/rlm-base/resources/ChromeOptionsHelper.py
Library           ${EXECDIR}/robot/rlm-base/resources/ChromeDebugHelper.py
Library           ${EXECDIR}/robot/rlm-base/resources/SalesforceAPI.py    WITH NAME    SalesforceAPI

*** Variables ***
${ORG_ALIAS}                ${EMPTY}
${HEADED}                   false
${PAUSE_FOR_RECORDING}      false
${PAGE_LOAD_TIMEOUT}        30s
${LIGHTNING_RENDER_WAIT}    3s
${SCREENSHOT_COUNTER}       ${0}

*** Keywords ***

# ── Browser Management ──────────────────────────────────────────────

Open Browser For E2E
    [Documentation]    Opens Chrome in headed (visible + CDP debug) or headless mode
    ...    based on the \${HEADED} variable. Headed mode enables remote debugging
    ...    on port 9222 for Chrome DevTools / CDP connections.
    IF    "${HEADED}" == "true"
        _Open Chrome Headed
    ELSE
        _Open Chrome Headless
    END
    Set Window Size    1920    1080

_Open Chrome Headed
    [Documentation]    Opens Chrome in visible mode with CDP debugging port.
    ${options}=    Get Visible Chrome Options
    ${path}=    WebDriverManager.Get Chrome Driver Path
    IF    "${path}" != "None" and "${path}" != ""
        ${service}=    Evaluate    selenium.webdriver.chrome.service.Service(executable_path=$path)    selenium.webdriver.chrome.service
        Create Webdriver    Chrome    service=${service}    options=${options}
    ELSE
        Create Webdriver    Chrome    options=${options}
    END
    Go To    about:blank

_Open Chrome Headless
    [Documentation]    Opens Chrome in headless mode (same as setup tests).
    ${options}=    Get Headless Chrome Options
    ${path}=    WebDriverManager.Get Chrome Driver Path
    IF    "${path}" != "None" and "${path}" != ""
        ${service}=    Evaluate    selenium.webdriver.chrome.service.Service(executable_path=$path)    selenium.webdriver.chrome.service
        Create Webdriver    Chrome    service=${service}    options=${options}
    ELSE
        Create Webdriver    Chrome    options=${options}
    END
    Go To    about:blank

Close Browser For E2E
    [Documentation]    Closes the browser session.
    Close Browser

# ── Navigation ───────────────────────────────────────────────────────

Get Authenticated Url
    [Documentation]    Gets an authenticated URL for a Lightning page path using
    ...    \`sf org open --url-only\`. Returns the full URL with session token.
    ...    URL-handling steps are wrapped in Set Log Level NONE to prevent the
    ...    session token from leaking into Robot log.html/CI artifacts.
    [Arguments]    ${page_path}
    Run Keyword If    "${ORG_ALIAS}" == ""    Fail    msg=ORG_ALIAS must be set
    ${prev_level}=    Set Log Level    NONE
    ${result}=    Run Process    sf    org    open    -o    ${ORG_ALIAS}    --url-only    -p    ${page_path}    shell=False
    Run Keyword If    ${result.rc} != 0    Set Log Level    ${prev_level}
    Run Keyword If    ${result.rc} != 0    Fail    msg=sf org open failed: ${result.stderr}
    ${raw}=    Strip String    ${result.stdout}
    ${raw}=    Evaluate    $raw.replace(chr(10), ' ').replace(chr(13), ' ').strip()
    ${url}=    Evaluate    $raw.split('with the following URL:')[-1].strip() if 'with the following URL:' in $raw else $raw
    ${url}=    Strip String    ${url}
    Set Log Level    ${prev_level}
    RETURN    ${url}

Navigate To App
    [Documentation]    Navigates to a Salesforce Lightning app by its display name.
    ...    Uses /lightning/app/<DeveloperName> with an authenticated URL.
    ...    The DeveloperName is derived by replacing spaces with underscores
    ...    and prepending the RLM namespace prefix.
    [Arguments]    ${app_name}
    ${app_api_name}=    Evaluate    'RLM_' + $app_name.replace(' ', '_')
    ${url}=    Get Authenticated Url    /lightning/app/c__${app_api_name}
    ${prev_level}=    Set Log Level    NONE
    Go To    ${url}
    Set Log Level    ${prev_level}
    Wait Until Page Contains Element    css:body    timeout=${PAGE_LOAD_TIMEOUT}
    Sleep    ${LIGHTNING_RENDER_WAIT}    reason=Allow app to load
    Log    Navigated to app: ${app_name}

Navigate To Record
    [Documentation]    Navigates to a Salesforce record page by SObject type and Id.
    [Arguments]    ${sobject}    ${record_id}
    ${url}=    Get Authenticated Url    /lightning/r/${sobject}/${record_id}/view
    ${prev_level}=    Set Log Level    NONE
    Go To    ${url}
    Set Log Level    ${prev_level}
    Wait Until Page Contains Element    css:body    timeout=${PAGE_LOAD_TIMEOUT}
    Sleep    ${LIGHTNING_RENDER_WAIT}    reason=Allow Lightning to finish rendering

Navigate To Account
    [Documentation]    Navigates to an Account record page.
    [Arguments]    ${account_id}
    Navigate To Record    Account    ${account_id}

Navigate To Opportunity
    [Documentation]    Navigates to an Opportunity record page.
    [Arguments]    ${opportunity_id}
    Navigate To Record    Opportunity    ${opportunity_id}

Navigate To Quote
    [Documentation]    Navigates to a Quote record page.
    [Arguments]    ${quote_id}
    Navigate To Record    Quote    ${quote_id}

Navigate To Order
    [Documentation]    Navigates to an Order record page.
    [Arguments]    ${order_id}
    Navigate To Record    Order    ${order_id}

Click Record Page Tab
    [Documentation]    Clicks a tab on a Lightning record page by its label.
    ...    Handles tabs inside shadow DOM (LWC tabset components).
    [Arguments]    ${tab_label}
    # Try XPath first (works for light DOM tabs)
    ${tab}=    Set Variable    xpath=//a[@data-label='${tab_label}' and @role='tab']
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${tab}    timeout=10s
    IF    ${found}
        Scroll Element Into View    ${tab}
        Click Element    ${tab}
        Sleep    2s    reason=Allow tab content to render
        RETURN
    END
    # Fallback: shadow DOM traversal
    ${js_result}=    Execute JavaScript
    ...    return (function(label){
    ...        function findAll(root, selector) {
    ...            var found = [];
    ...            var els = root.querySelectorAll(selector);
    ...            for (var i = 0; i < els.length; i++) found.push(els[i]);
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot) found = found.concat(findAll(all[i].shadowRoot, selector));
    ...            }
    ...            return found;
    ...        }
    ...        var tabs = findAll(document, 'a[role="tab"][data-label="' + label + '"]');
    ...        for (var i = 0; i < tabs.length; i++) {
    ...            if (tabs[i].offsetParent !== null) { tabs[i].click(); return 'clicked'; }
    ...        }
    ...        /* Fallback: match by text content */
    ...        var allTabs = findAll(document, 'a[role="tab"]');
    ...        for (var i = 0; i < allTabs.length; i++) {
    ...            if (allTabs[i].textContent.trim() === label && allTabs[i].offsetParent !== null) {
    ...                allTabs[i].click(); return 'clicked_by_text';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${tab_label}
    Log    Click tab result: ${js_result}
    IF    "${js_result}" == "not_found"
        Capture Step Screenshot    tab_not_found_${tab_label}
        Fail    msg=Tab "${tab_label}" not found on record page.
    END
    Sleep    2s    reason=Allow tab content to render

# ── QuickAction / Highlights Panel ──────────────────────────────────

Click Highlights Panel Action
    [Documentation]    Clicks an action button in the Lightning record page highlights
    ...    panel or actions menu. Tries the visible button first, then falls back
    ...    to the overflow "More Actions" menu, then to shadow DOM JS traversal.
    [Arguments]    ${action_label}
    # Try direct button in highlights panel
    ${btn}=    Set Variable    xpath=//runtime_platform_actions-actions-ribbon//button[normalize-space(.)='${action_label}'] | //runtime_platform_actions-action-renderer//a[@title='${action_label}'] | //li[contains(@class,'oneActionsRibbon')]//a[@title='${action_label}']
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${btn}    timeout=10s
    IF    ${found}
        Scroll Element Into View    ${btn}
        Click Element    ${btn}
        Sleep    2s    reason=Allow action modal/flow to open
        RETURN
    END
    # Try overflow menu
    ${more_btn}=    Set Variable    xpath=//runtime_platform_actions-actions-ribbon//button[contains(@class,'slds-button_icon-border') or @title='More Actions' or contains(normalize-space(.),'more actions')] | //lightning-button-menu[contains(@class,'action')]//button
    ${more_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${more_btn}    timeout=5s
    IF    ${more_found}
        Click Element    ${more_btn}
        Sleep    1s    reason=Allow dropdown to render
        ${menu_item}=    Set Variable    xpath=//lightning-menu-item[contains(@data-target-selection-name,'${action_label}') or .//span[normalize-space(.)='${action_label}']] | //a[@title='${action_label}']
        Wait Until Element Is Visible    ${menu_item}    timeout=10s
        Click Element    ${menu_item}
        Sleep    2s    reason=Allow action modal/flow to open
        RETURN
    END
    # Fallback: shadow DOM JS traversal for LWC action buttons
    ${js_result}=    Execute JavaScript
    ...    return (function(label){
    ...        function findAll(root, tag) {
    ...            var found = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === tag) found.push(all[i]);
    ...                if (all[i].shadowRoot) found = found.concat(findAll(all[i].shadowRoot, tag));
    ...            }
    ...            return found;
    ...        }
    ...        /* Try to find and click the overflow menu button via shadow DOM first */
    ...        var ribbon = document.querySelector('runtime_platform_actions-actions-ribbon');
    ...        if (ribbon) {
    ...            var ribbonRoot = ribbon.shadowRoot || ribbon;
    ...            var btns = findAll(ribbonRoot, 'BUTTON');
    ...            /* First try direct action button */
    ...            for (var i = 0; i < btns.length; i++) {
    ...                if (btns[i].textContent.trim() === label) { btns[i].click(); return 'clicked_direct'; }
    ...            }
    ...            /* Try overflow/more actions menu button */
    ...            for (var i = 0; i < btns.length; i++) {
    ...                if (btns[i].title === 'More Actions' || btns[i].getAttribute('aria-label') === 'More Actions') {
    ...                    btns[i].click(); return 'opened_overflow';
    ...                }
    ...            }
    ...        }
    ...        /* Broad search: find any visible button matching label text or name across entire DOM */
    ...        var allBtns = findAll(document, 'BUTTON');
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            if (allBtns[i].offsetParent === null) continue;
    ...            var txt = allBtns[i].textContent.trim();
    ...            var nm = allBtns[i].getAttribute('name') || '';
    ...            if (txt === label || nm === label + 'Order' || nm === label) {
    ...                allBtns[i].click(); return 'clicked_broad';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${action_label}
    Log    Highlights Panel JS result: ${js_result}
    IF    "${js_result}" == "clicked_direct" or "${js_result}" == "clicked_broad"
        Sleep    2s    reason=Allow action modal/flow to open
        RETURN
    END
    IF    "${js_result}" == "opened_overflow"
        Sleep    1s    reason=Allow dropdown to render
        ${menu_item}=    Set Variable    xpath=//lightning-menu-item[contains(@data-target-selection-name,'${action_label}') or .//span[normalize-space(.)='${action_label}']] | //a[@title='${action_label}']
        ${menu_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${menu_item}    timeout=10s
        IF    ${menu_found}
            Click Element    ${menu_item}
            Sleep    2s    reason=Allow action modal/flow to open
            RETURN
        END
    END
    Capture Step Screenshot    action_not_found_${action_label}
    Fail    msg=Action button "${action_label}" not found in highlights panel or overflow menu.

Wait For Modal
    [Documentation]    Waits for a Lightning modal dialog to appear.
    [Arguments]    ${timeout}=15s
    ${modal}=    Set Variable    xpath=//div[contains(@class,'modal-container') or contains(@class,'slds-modal')] | //section[contains(@class,'slds-modal')]
    Wait Until Element Is Visible    ${modal}    timeout=${timeout}
    Sleep    1s    reason=Allow modal content to render

Fill Modal Field
    [Documentation]    Fills a field in a modal dialog by field label.
    ...    Handles both standard input fields and Lightning combobox/lookup fields.
    [Arguments]    ${field_label}    ${value}
    # Try standard input
    ${input}=    Set Variable    xpath=//div[contains(@class,'modal')]//label[normalize-space(.)='${field_label}']/following::input[1] | //div[contains(@class,'modal')]//span[normalize-space(.)='${field_label}']/ancestor::*[contains(@class,'slds-form-element')][1]//input
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${input}    timeout=8s
    IF    ${found}
        Click Element    ${input}
        Press Keys    ${input}    CTRL+a    DELETE
        Input Text    ${input}    ${value}
        Sleep    0.5s
        RETURN
    END
    # Try textarea
    ${textarea}=    Set Variable    xpath=//div[contains(@class,'modal')]//label[normalize-space(.)='${field_label}']/following::textarea[1]
    ${ta_found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${textarea}    timeout=3s
    IF    ${ta_found}
        Click Element    ${textarea}
        Input Text    ${textarea}    ${value}
        RETURN
    END
    Log    WARNING: Could not find field "${field_label}" in modal.    WARN

Select Modal Picklist Value
    [Documentation]    Selects a value from a picklist/combobox field in a modal.
    ...    Tries native <select> first (Aura modals), then Lightning combobox (LWC).
    [Arguments]    ${field_label}    ${value}
    # Strategy 1: Native <select> (common in Aura QuickAction modals)
    ${native_select}=    Set Variable    xpath=(//label[contains(normalize-space(.),'${field_label}')]/following::select[1] | //span[normalize-space(.)='${field_label}']/ancestor::*[.//select][1]//select)[1]
    ${is_native}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${native_select}    timeout=5s
    IF    ${is_native}
        Select From List By Label    ${native_select}    ${value}
        Sleep    1s    reason=Allow selection to apply
        RETURN
    END
    # Strategy 2: Lightning combobox (role=combobox)
    ${combobox}=    Set Variable    xpath=//div[contains(@class,'modal')]//label[normalize-space(.)='${field_label}']/following::*[@role='combobox' or contains(@class,'slds-combobox')][1] | //div[contains(@class,'modal')]//span[normalize-space(.)='${field_label}']/ancestor::*[contains(@class,'slds-form-element')][1]//*[@role='combobox']
    ${is_combobox}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${combobox}    timeout=5s
    IF    ${is_combobox}
        Click Element    ${combobox}
        Sleep    1s    reason=Allow dropdown to populate
        ${option}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${value}')])[1]
        Wait Until Element Is Visible    ${option}    timeout=10s
        Click Element    ${option}
        Sleep    1s    reason=Allow selection to apply
        RETURN
    END
    # Strategy 3: Aura <a> picklist trigger
    ${aura_picklist}=    Set Variable    xpath=(//span[normalize-space(.)='${field_label}']/ancestor::div[contains(@class,'form-element')]//a[contains(@class,'select') or contains(@class,'picklist')])[1]
    ${is_aura}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${aura_picklist}    timeout=5s
    IF    ${is_aura}
        Click Element    ${aura_picklist}
        Sleep    1s    reason=Allow dropdown to populate
        ${aura_option}=    Set Variable    xpath=(//a[@role='menuitemcheckbox' and normalize-space(.)='${value}'] | //li[contains(@class,'uiMenuItem')]//a[normalize-space(.)='${value}'])[1]
        Wait Until Element Is Visible    ${aura_option}    timeout=10s
        Click Element    ${aura_option}
        Sleep    1s    reason=Allow selection to apply
        RETURN
    END
    Capture Step Screenshot    picklist_not_found_${field_label}
    Fail    msg=Could not find picklist/combobox for "${field_label}"

Select Lookup Value
    [Documentation]    Types into a lookup/autocomplete search field and selects a result.
    ...    Finds the input by its placeholder text (e.g. "Search Price Books"),
    ...    types the search value, waits for results, and clicks the match.
    [Arguments]    ${placeholder}    ${value}
    ${input}=    Set Variable    xpath=//input[@placeholder='${placeholder}' or @title='${placeholder}' or contains(@placeholder,'${placeholder}')]
    Wait Until Element Is Visible    ${input}    timeout=10s
    Click Element    ${input}
    Input Text    ${input}    ${value}
    Sleep    2s    reason=Allow lookup results to populate
    # Click the matching result — lookup results appear as role=option or in a listbox
    ${result}=    Set Variable    xpath=(//*[@role='option' and contains(normalize-space(.), '${value}')] | //a[contains(@class,'lookup') and contains(normalize-space(.), '${value}')] | //div[contains(@class,'lookup')]//span[contains(normalize-space(.), '${value}')] | //li[contains(@class,'lookup')]//a[contains(normalize-space(.), '${value}')])[1]
    Wait Until Element Is Visible    ${result}    timeout=10s
    Click Element    ${result}
    Sleep    1s    reason=Allow selection to apply

Save Modal
    [Documentation]    Clicks the Save button in a modal dialog via JavaScript.
    ...    Handles Aura QuickAction modals (cuf-publisherShareButton),
    ...    Flow navigation bars, and LWC modals. Retries up to 30s for the
    ...    button to appear (flow screens can be slow to render).
    [Arguments]    ${button_label}=Save
    Wait Until Keyword Succeeds    30s    3s    _Click Save Button Via JS    ${button_label}
    Sleep    3s    reason=Allow save to complete

_Click Save Button Via JS
    [Documentation]    Internal keyword — attempts to find and click a save button via JS.
    ...    Traverses shadow DOM boundaries to find buttons inside LWC components.
    ...    Fails if not found (so Wait Until Keyword Succeeds can retry).
    [Arguments]    ${button_label}
    ${result}=    Execute JavaScript
    ...    return (function(label){
    ...        /* Recursively find all <button> elements, traversing shadow roots */
    ...        function findAllButtons(root) {
    ...            var btns = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'BUTTON') btns.push(all[i]);
    ...                if (all[i].shadowRoot) {
    ...                    btns = btns.concat(findAllButtons(all[i].shadowRoot));
    ...                }
    ...            }
    ...            return btns;
    ...        }
    ...        /* 1. Aura QuickAction footer — no shadow DOM */
    ...        var btn = document.querySelector('button.cuf-publisherShareButton');
    ...        if (btn) {
    ...            var t = btn.textContent.trim();
    ...            if (t === label || t.indexOf(label) >= 0) { btn.click(); return 'clicked_aura_footer:' + t; }
    ...        }
    ...        /* 2. Flow navigation bar — traverse shadow roots */
    ...        var flowEl = document.querySelector('flowruntime-flow');
    ...        if (flowEl) {
    ...            var root = flowEl.shadowRoot || flowEl;
    ...            var navBar = root.querySelector('flowruntime-navigation-bar');
    ...            if (navBar) {
    ...                var navRoot = navBar.shadowRoot || navBar;
    ...                var navBtns = findAllButtons(navRoot);
    ...                for (var i = 0; i < navBtns.length; i++) {
    ...                    var t = navBtns[i].textContent.trim();
    ...                    if (t === label || t.indexOf(label) >= 0) { navBtns[i].click(); return 'clicked_flow_nav_shadow:' + t; }
    ...                }
    ...            }
    ...            /* Also try all buttons in the flow element via shadow traversal */
    ...            var flowBtns = findAllButtons(root);
    ...            for (var i = 0; i < flowBtns.length; i++) {
    ...                var t = flowBtns[i].textContent.trim();
    ...                if (t === label || t.indexOf(label) >= 0) { flowBtns[i].click(); return 'clicked_flow_shadow:' + t; }
    ...            }
    ...        }
    ...        /* 3. slds-modal footer */
    ...        var footer = document.querySelector('footer.slds-modal__footer');
    ...        if (footer) {
    ...            var fBtns = findAllButtons(footer);
    ...            for (var i = 0; i < fBtns.length; i++) {
    ...                var t = fBtns[i].textContent.trim();
    ...                if (t === label || t.indexOf(label) >= 0) { fBtns[i].click(); return 'clicked_modal_footer:' + t; }
    ...            }
    ...        }
    ...        /* 4. Broad search — all buttons including shadow DOM */
    ...        var allBtns = findAllButtons(document);
    ...        for (var j = 0; j < allBtns.length; j++) {
    ...            var t = allBtns[j].textContent.trim();
    ...            if ((t === label || t.indexOf(label) >= 0) && allBtns[j].offsetParent !== null) {
    ...                allBtns[j].click(); return 'clicked_visible_shadow:' + t;
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${button_label}
    Log    Save Modal JS result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    save_button_not_found
        Fail    msg=${button_label} button not found in modal via JavaScript (will retry).
    END

Advance Through Flow Screens
    [Documentation]    Iteratively advances through all screens in a Flow-based modal.
    ...    Clicks Next/Finish/Done/Create Order buttons until the flow completes or
    ...    no more flow buttons are found. Handles flows with 1 or more screens.
    ${max_screens}=    Set Variable    ${10}
    FOR    ${i}    IN RANGE    ${max_screens}
        Capture Step Screenshot    flow_screen_${i}
        # Look for any actionable flow button via JavaScript (traverses shadow DOM)
        ${btn_result}=    Execute JavaScript
        ...    return (function(){
        ...        var labels = ['Next', 'Finish', 'Done', 'Create Order', 'Create Orders', 'Submit', 'Save', 'Confirm'];
        ...        function findAllButtons(root) {
        ...            var btns = [];
        ...            var all = root.querySelectorAll('*');
        ...            for (var i = 0; i < all.length; i++) {
        ...                if (all[i].tagName === 'BUTTON') btns.push(all[i]);
        ...                if (all[i].shadowRoot) btns = btns.concat(findAllButtons(all[i].shadowRoot));
        ...            }
        ...            return btns;
        ...        }
        ...        /* 1. Flow navigation bar buttons (with shadow DOM traversal) */
        ...        var flowEl = document.querySelector('flowruntime-flow');
        ...        if (flowEl) {
        ...            var fRoot = flowEl.shadowRoot || flowEl;
        ...            var navBar = fRoot.querySelector('flowruntime-navigation-bar');
        ...            if (navBar) {
        ...                var navRoot = navBar.shadowRoot || navBar;
        ...                var navBtns = findAllButtons(navRoot);
        ...                for (var i = 0; i < navBtns.length; i++) {
        ...                    var txt = navBtns[i].textContent.trim();
        ...                    for (var j = 0; j < labels.length; j++) {
        ...                        if (txt === labels[j]) { navBtns[i].click(); return 'clicked:' + txt; }
        ...                    }
        ...                }
        ...            }
        ...        }
        ...        /* 2. Modal footer buttons (with shadow DOM traversal) */
        ...        var footer = document.querySelector('footer.slds-modal__footer');
        ...        if (footer) {
        ...            var fBtns = findAllButtons(footer);
        ...            for (var i = 0; i < fBtns.length; i++) {
        ...                var txt = fBtns[i].textContent.trim();
        ...                for (var j = 0; j < labels.length; j++) {
        ...                    if (txt === labels[j]) { fBtns[i].click(); return 'clicked:' + txt; }
        ...                }
        ...            }
        ...        }
        ...        /* 3. Broad search — all buttons including shadow DOM */
        ...        var allBtns = findAllButtons(document);
        ...        for (var i = 0; i < allBtns.length; i++) {
        ...            if (allBtns[i].offsetParent === null) continue;
        ...            var txt = allBtns[i].textContent.trim();
        ...            for (var j = 0; j < labels.length; j++) {
        ...                if (txt === labels[j]) { allBtns[i].click(); return 'clicked:' + txt; }
        ...            }
        ...        }
        ...        return 'no_button_found';
        ...    })()
        Log    Flow screen ${i}: ${btn_result}
        IF    "${btn_result}" == "no_button_found"
            Log    No more flow buttons found after ${i} screens.
            RETURN
        END
        Sleep    5s    reason=Allow flow screen to advance
        # Check if flow/modal has closed (we're back on the record page)
        ${flow_still_open}=    Run Keyword And Return Status    Page Should Contain Element
        ...    xpath=//flowruntime-flow | //div[contains(@class,'modal-container')] | //section[contains(@class,'slds-modal')]
        IF    not ${flow_still_open}
            Log    Flow/modal closed after clicking ${btn_result}.
            RETURN
        END
    END

# ── Create Order ───────────────────────────────────────────────────

Select Order Creation Method
    [Documentation]    Selects "Create Single Order" in the Create Order flow's
    ...    order-creation-method-picker and clicks Next/Finish.
    ...    The picker uses radio inputs inside runtime_rca-order-creation-method-picker
    ...    which is nested in shadow DOM.
    Wait Until Keyword Succeeds    15s    3s    _Select Single Order Radio Via JS
    Sleep    2s    reason=Allow selection to register
    # Click Finish to advance past the picker screen
    Save Modal    Finish

_Select Single Order Radio Via JS
    [Documentation]    Internal keyword — finds and clicks the Create Single Order radio via JS.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function deepQueryAll(root, selector) {
    ...            var found = [];
    ...            var els = root.querySelectorAll(selector);
    ...            for (var i = 0; i < els.length; i++) found.push(els[i]);
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot) found = found.concat(deepQueryAll(all[i].shadowRoot, selector));
    ...                if (all[i].tagName === 'SLOT') {
    ...                    try {
    ...                        var assigned = all[i].assignedElements({flatten: true});
    ...                        for (var j = 0; j < assigned.length; j++) {
    ...                            found = found.concat(deepQueryAll(assigned[j], selector));
    ...                        }
    ...                    } catch(e) {}
    ...                }
    ...            }
    ...            return found;
    ...        }
    ...        /* Find radio with value="CreateSingleOrder" */
    ...        var radios = deepQueryAll(document, 'input[value="CreateSingleOrder"]');
    ...        for (var i = 0; i < radios.length; i++) {
    ...            radios[i].click();
    ...            return 'selected';
    ...        }
    ...        /* Fallback: find the visual picker div with data-id="single-order" */
    ...        var pickers = deepQueryAll(document, 'div[data-id="single-order"]');
    ...        for (var i = 0; i < pickers.length; i++) {
    ...            var radio = pickers[i].querySelector('input[type="radio"]');
    ...            if (radio) { radio.click(); return 'selected_by_picker'; }
    ...            var label = pickers[i].querySelector('label');
    ...            if (label) { label.click(); return 'selected_by_label'; }
    ...        }
    ...        return 'not_found';
    ...    })()
    Log    Select Order Creation Method JS result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    order_method_not_found
        Fail    msg=Create Single Order radio not found (will retry).
    END

# ── Browse Catalogs ────────────────────────────────────────────────

Click Browse Catalogs
    [Documentation]    Clicks the Browse Catalogs button on a Quote record page.
    ...    Traverses shadow DOM to find the button (name="BrowseCatalog").
    ...    If a "Choose Price Book" modal appears, saves it with Standard Price Book.
    Wait Until Keyword Succeeds    30s    3s    _Click Browse Catalogs Via JS
    Sleep    3s    reason=Allow Browse Catalogs or Price Book modal to load
    # Handle Choose Price Book modal if it appears (retry to allow modal to render)
    Wait Until Keyword Succeeds    15s    2s    _Dismiss Price Book Modal If Present
    Sleep    5s    reason=Allow Browse Catalogs to load

_Dismiss Price Book Modal If Present
    [Documentation]    If a "Choose Price Book" modal appears, clicks Save.
    ...    The modal DOM is: some-component (shadow host) → lightning-modal →
    ...    lightning-modal-footer (shadow host) → slot → lightning-button (shadow host) → button.
    ...    Slotted lightning-button elements are light DOM children of lightning-modal-footer,
    ...    so we must traverse from the light DOM side, not from inside the shadow root.
    ...    Fails if modal is found but Save cannot be clicked (allows retry wrapper).
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        /* Recursively traverse shadow DOM to find elements matching a selector */
    ...        function deepQueryAll(root, selector) {
    ...            var found = [];
    ...            var els = root.querySelectorAll(selector);
    ...            for (var i = 0; i < els.length; i++) found.push(els[i]);
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot) {
    ...                    found = found.concat(deepQueryAll(all[i].shadowRoot, selector));
    ...                }
    ...                /* Also check slotted content via assignedElements */
    ...                if (all[i].tagName === 'SLOT') {
    ...                    try {
    ...                        var assigned = all[i].assignedElements({flatten: true});
    ...                        for (var j = 0; j < assigned.length; j++) {
    ...                            found = found.concat(deepQueryAll(assigned[j], selector));
    ...                            if (assigned[j].matches && assigned[j].matches(selector)) found.push(assigned[j]);
    ...                        }
    ...                    } catch(e) {}
    ...                }
    ...            }
    ...            return found;
    ...        }
    ...        /* Step 1: Check if any Price Book modal is present */
    ...        var headings = deepQueryAll(document, 'h1');
    ...        var hasPriceBookModal = false;
    ...        for (var i = 0; i < headings.length; i++) {
    ...            if (headings[i].textContent.trim().indexOf('Price Book') >= 0) {
    ...                hasPriceBookModal = true; break;
    ...            }
    ...        }
    ...        if (!hasPriceBookModal) return 'no_modal';
    ...        /* Step 2: Find the Save button — try multiple strategies */
    ...        /* 2a: Find lightning-button[data-id="saveButton"] and click its inner button */
    ...        var wrappers = deepQueryAll(document, 'lightning-button[data-id="saveButton"]');
    ...        for (var i = 0; i < wrappers.length; i++) {
    ...            var btn = (wrappers[i].shadowRoot)
    ...                ? wrappers[i].shadowRoot.querySelector('button')
    ...                : wrappers[i].querySelector('button');
    ...            if (btn) { btn.click(); return 'clicked_save_wrapper'; }
    ...        }
    ...        /* 2b: Find button[name="save-button"] anywhere in the DOM */
    ...        var saveBtns = deepQueryAll(document, 'button[name="save-button"]');
    ...        for (var i = 0; i < saveBtns.length; i++) {
    ...            if (saveBtns[i].offsetParent !== null) {
    ...                saveBtns[i].click();
    ...                return 'clicked_save_by_name';
    ...            }
    ...        }
    ...        /* 2c: Find any visible button with text "Save" */
    ...        var allBtns = deepQueryAll(document, 'button');
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            if (allBtns[i].textContent.trim() === 'Save' && allBtns[i].offsetParent !== null) {
    ...                allBtns[i].click();
    ...                return 'clicked_save_by_text';
    ...            }
    ...        }
    ...        return 'modal_found_but_save_not_clicked';
    ...    })()
    Log    Price Book modal result: ${result}
    IF    "${result}" == "no_modal"
        Log    No Price Book modal detected — continuing.
        RETURN
    END
    IF    "${result}" == "modal_found_but_save_not_clicked"
        Fail    msg=Price Book modal found but Save button could not be clicked (will retry).
    END
    Sleep    3s    reason=Allow Price Book selection to process

_Click Browse Catalogs Via JS
    [Documentation]    Internal keyword — finds and clicks Browse Catalogs via JS with shadow DOM traversal.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function findAllButtons(root) {
    ...            var btns = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'BUTTON') btns.push(all[i]);
    ...                if (all[i].shadowRoot) btns = btns.concat(findAllButtons(all[i].shadowRoot));
    ...            }
    ...            return btns;
    ...        }
    ...        var allBtns = findAllButtons(document);
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            if (allBtns[i].getAttribute('name') === 'BrowseCatalog' ||
    ...                allBtns[i].textContent.trim() === 'Browse Catalogs') {
    ...                allBtns[i].click();
    ...                return 'clicked';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })()
    Log    Browse Catalogs JS result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    browse_catalogs_not_found
        Fail    msg=Browse Catalogs button not found (will retry).
    END

Select Catalog By Name
    [Documentation]    Selects a catalog by name in the All Catalogs datatable and clicks Next.
    ...    The datatable uses radio buttons for single selection. Each row has
    ...    data-cell-value on the Name <th> element matching the catalog name.
    ...    Also handles a late-arriving Choose Price Book modal (race condition).
    [Arguments]    ${catalog_name}
    Wait Until Keyword Succeeds    30s    3s    _Dismiss Or Select Catalog    ${catalog_name}
    Sleep    2s    reason=Allow selection to register
    # Click Next in the flow navigation bar
    Save Modal    Next
    Sleep    5s    reason=Allow catalog selection to process

_Dismiss Or Select Catalog
    [Documentation]    Internal keyword — dismisses any Price Book modal, then selects the catalog.
    ...    If the Price Book modal is still showing, dismiss it and fail (will retry).
    [Arguments]    ${catalog_name}
    # Check for and dismiss Price Book modal if it appeared late
    _Dismiss Price Book Modal If Present
    # Now try to select the catalog
    _Select Catalog Radio Via JS    ${catalog_name}

_Select Catalog Radio Via JS
    [Documentation]    Internal keyword — finds the catalog row and clicks its radio button.
    ...    Traverses shadow DOM to find datatable rows inside LWC components.
    [Arguments]    ${catalog_name}
    ${result}=    Execute JavaScript
    ...    return (function(name){
    ...        function findRows(root) {
    ...            var rows = [];
    ...            var trs = root.querySelectorAll('tr[data-row-key-value]');
    ...            for (var i = 0; i < trs.length; i++) rows.push(trs[i]);
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot) {
    ...                    var shadowRows = findRows(all[i].shadowRoot);
    ...                    for (var j = 0; j < shadowRows.length; j++) rows.push(shadowRows[j]);
    ...                }
    ...            }
    ...            return rows;
    ...        }
    ...        function findInputs(root) {
    ...            var inputs = [];
    ...            var all = root.querySelectorAll('input[type="radio"]');
    ...            for (var i = 0; i < all.length; i++) inputs.push(all[i]);
    ...            var els = root.querySelectorAll('*');
    ...            for (var i = 0; i < els.length; i++) {
    ...                if (els[i].shadowRoot) {
    ...                    var shadowInputs = findInputs(els[i].shadowRoot);
    ...                    for (var j = 0; j < shadowInputs.length; j++) inputs.push(shadowInputs[j]);
    ...                }
    ...            }
    ...            return inputs;
    ...        }
    ...        var rows = findRows(document);
    ...        for (var i = 0; i < rows.length; i++) {
    ...            var nameCell = rows[i].querySelector('th[data-cell-value="' + name + '"]');
    ...            if (nameCell) {
    ...                var radios = findInputs(rows[i]);
    ...                if (radios.length > 0) { radios[0].click(); return 'selected:' + name; }
    ...                var radio = rows[i].querySelector('input[type="radio"]');
    ...                if (radio) { radio.click(); return 'selected_direct:' + name; }
    ...            }
    ...        }
    ...        /* Fallback: search by text content */
    ...        for (var i = 0; i < rows.length; i++) {
    ...            var th = rows[i].querySelector('th[data-label="Name"]');
    ...            if (th && th.textContent.trim().indexOf(name) >= 0) {
    ...                var radios = findInputs(rows[i]);
    ...                if (radios.length > 0) { radios[0].click(); return 'selected_by_text:' + name; }
    ...                var radio = rows[i].querySelector('input[type="radio"]');
    ...                if (radio) { radio.click(); return 'selected_by_text_direct:' + name; }
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${catalog_name}
    Log    Select Catalog JS result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    catalog_not_found
        Fail    msg=Catalog "${catalog_name}" not found in datatable (will retry).
    END

Search Product In Catalog
    [Documentation]    Waits for the product catalog to load, then searches for a product
    ...    by name using the search input (name="enter-search") and presses Enter.
    [Arguments]    ${product_name}
    # Wait for the product catalog search input to appear (indicates catalog has loaded)
    Wait Until Keyword Succeeds    30s    3s    _Find Product Search Input
    Sleep    2s    reason=Allow catalog products to fully render
    # Set search value via native setter (triggers LWC reactivity)
    ${input_set}=    Execute JavaScript
    ...    return (function(name){
    ...        function findInputs(root) {
    ...            var inputs = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'INPUT') inputs.push(all[i]);
    ...                if (all[i].shadowRoot) inputs = inputs.concat(findInputs(all[i].shadowRoot));
    ...            }
    ...            return inputs;
    ...        }
    ...        var allInputs = findInputs(document);
    ...        for (var i = 0; i < allInputs.length; i++) {
    ...            if (allInputs[i].getAttribute('name') === 'enter-search' ||
    ...                (allInputs[i].getAttribute('placeholder') && allInputs[i].getAttribute('placeholder').indexOf('Search for products') >= 0)) {
    ...                /* Use native setter to trigger LWC change detection */
    ...                var nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    ...                allInputs[i].focus();
    ...                nativeSetter.call(allInputs[i], name);
    ...                allInputs[i].dispatchEvent(new Event('input', {bubbles: true, composed: true}));
    ...                allInputs[i].dispatchEvent(new Event('change', {bubbles: true, composed: true}));
    ...                return 'set:' + allInputs[i].getAttribute('name');
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${product_name}
    Log    Search input set result: ${input_set}
    IF    "${input_set}" == "not_found"
        Capture Step Screenshot    product_search_not_found
        Fail    msg=Product search input not found.
    END
    # Press Enter via Selenium (more reliable than JS KeyboardEvent for LWC)
    _Press Enter On Search Input
    Sleep    5s    reason=Allow search results to load

_Press Enter On Search Input
    [Documentation]    Internal keyword — sends Enter key to the product search input via Selenium.
    ...    Falls back to JS keyboard event dispatch if Selenium can't find the input.
    # Try Selenium Press Keys on the active/focused element
    ${active}=    Execute JavaScript    return document.activeElement ? document.activeElement.tagName : 'NONE'
    IF    "${active}" == "INPUT"
        Press Keys    ${NONE}    RETURN
        RETURN
    END
    # Fallback: find the input and use Selenium
    ${input_found}=    Run Keyword And Return Status    Wait Until Element Is Visible
    ...    xpath=//input[@name='enter-search' or contains(@placeholder,'Search for products')]    timeout=3s
    IF    ${input_found}
        Press Keys    xpath=//input[@name='enter-search' or contains(@placeholder,'Search for products')]    RETURN
        RETURN
    END
    # Last resort: JS event dispatch with composed: true for shadow DOM
    Execute JavaScript
    ...    (function(){
    ...        function findInputs(root) {
    ...            var inputs = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'INPUT') inputs.push(all[i]);
    ...                if (all[i].shadowRoot) inputs = inputs.concat(findInputs(all[i].shadowRoot));
    ...            }
    ...            return inputs;
    ...        }
    ...        var allInputs = findInputs(document);
    ...        for (var i = 0; i < allInputs.length; i++) {
    ...            if (allInputs[i].getAttribute('name') === 'enter-search' ||
    ...                (allInputs[i].getAttribute('placeholder') && allInputs[i].getAttribute('placeholder').indexOf('Search for products') >= 0)) {
    ...                allInputs[i].focus();
    ...                var opts = {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, composed: true, cancelable: true};
    ...                allInputs[i].dispatchEvent(new KeyboardEvent('keydown', opts));
    ...                allInputs[i].dispatchEvent(new KeyboardEvent('keypress', opts));
    ...                allInputs[i].dispatchEvent(new KeyboardEvent('keyup', opts));
    ...                /* Also try submitting closest form if present */
    ...                var form = allInputs[i].closest('form');
    ...                if (form) form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    ...                break;
    ...            }
    ...        }
    ...    })()

_Find Product Search Input
    [Documentation]    Internal keyword — verifies the product search input is present.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function findInputs(root) {
    ...            var inputs = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'INPUT') inputs.push(all[i]);
    ...                if (all[i].shadowRoot) inputs = inputs.concat(findInputs(all[i].shadowRoot));
    ...            }
    ...            return inputs;
    ...        }
    ...        var allInputs = findInputs(document);
    ...        for (var i = 0; i < allInputs.length; i++) {
    ...            if (allInputs[i].getAttribute('name') === 'enter-search' ||
    ...                (allInputs[i].getAttribute('placeholder') && allInputs[i].getAttribute('placeholder').indexOf('Search for products') >= 0)) {
    ...                return 'found';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })()
    IF    "${result}" == "not_found"
        Fail    msg=Product search input not yet available (will retry).
    END

Add Product By Name
    [Documentation]    Finds a product row by name in the Browse Catalogs results and clicks
    ...    its "Add" button. The product must be visible in the current search results.
    [Arguments]    ${product_name}
    Wait Until Keyword Succeeds    30s    3s    _Click Add Button For Product    ${product_name}
    Sleep    3s    reason=Allow product to be added

_Click Add Button For Product
    [Documentation]    Internal keyword — finds the product row and clicks its Add button via JS.
    [Arguments]    ${product_name}
    ${result}=    Execute JavaScript
    ...    return (function(name){
    ...        function findAllButtons(root) {
    ...            var btns = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'BUTTON') btns.push(all[i]);
    ...                if (all[i].shadowRoot) btns = btns.concat(findAllButtons(all[i].shadowRoot));
    ...            }
    ...            return btns;
    ...        }
    ...        /* Find product rows */
    ...        var rows = document.querySelectorAll('runtime_industries_cpq-product-row');
    ...        for (var i = 0; i < rows.length; i++) {
    ...            var root = rows[i].shadowRoot || rows[i];
    ...            var titleEl = root.querySelector('div[title="' + name + '"]');
    ...            if (!titleEl) {
    ...                /* fallback: check text content */
    ...                var divs = root.querySelectorAll('div.heading-style, div[data-id]');
    ...                for (var d = 0; d < divs.length; d++) {
    ...                    if (divs[d].textContent.trim() === name) { titleEl = divs[d]; break; }
    ...                }
    ...            }
    ...            if (titleEl) {
    ...                var btns = findAllButtons(root);
    ...                for (var b = 0; b < btns.length; b++) {
    ...                    if (btns[b].getAttribute('name') === 'Add' ||
    ...                        btns[b].textContent.trim() === 'Add') {
    ...                        btns[b].click();
    ...                        return 'added:' + name;
    ...                    }
    ...                }
    ...                return 'add_button_not_found';
    ...            }
    ...        }
    ...        /* Fallback: search all visible Add buttons near product name text */
    ...        var allBtns = findAllButtons(document);
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            if ((allBtns[i].getAttribute('name') === 'Add' || allBtns[i].textContent.trim() === 'Add')
    ...                && allBtns[i].getAttribute('title') === 'Add') {
    ...                allBtns[i].click();
    ...                return 'added_fallback';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${product_name}
    Log    Add Product JS result: ${result}
    IF    "${result}" == "not_found" or "${result}" == "add_button_not_found"
        Capture Step Screenshot    add_product_not_found
        Fail    msg=Product "${product_name}" or its Add button not found (will retry).
    END

Click Save Quote In Catalog
    [Documentation]    Clicks the "Save Quote" button in the Browse Catalogs modal.
    ...    Waits for the button to become enabled before clicking.
    ...    The button has data-id="objectActionButton" and title="Save Quote".
    Wait Until Keyword Succeeds    30s    3s    _Click Save Quote Via JS
    Sleep    5s    reason=Allow quote to save and modal to close

_Click Save Quote Via JS
    [Documentation]    Internal keyword — finds and clicks Save Quote button via JS.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function findAllButtons(root) {
    ...            var btns = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'BUTTON') btns.push(all[i]);
    ...                if (all[i].shadowRoot) btns = btns.concat(findAllButtons(all[i].shadowRoot));
    ...            }
    ...            return btns;
    ...        }
    ...        var allBtns = findAllButtons(document);
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            var btn = allBtns[i];
    ...            if ((btn.getAttribute('title') === 'Save Quote' || btn.textContent.trim() === 'Save Quote')
    ...                && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
    ...                btn.click();
    ...                return 'clicked';
    ...            }
    ...        }
    ...        /* Check if button exists but is disabled */
    ...        for (var i = 0; i < allBtns.length; i++) {
    ...            if (allBtns[i].getAttribute('title') === 'Save Quote' || allBtns[i].textContent.trim() === 'Save Quote') {
    ...                return 'found_but_disabled';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })()
    Log    Save Quote JS result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    save_quote_not_found
        Fail    msg=Save Quote button not found (will retry).
    END
    IF    "${result}" == "found_but_disabled"
        Fail    msg=Save Quote button found but still disabled (will retry).
    END

# ── Setup Helpers ──────────────────────────────────────────────────

Lookup Test Account
    [Documentation]    Looks up the test Account by name and sets ACCOUNT_ID as a suite variable.
    ...    Fails if the Account is not found in the org.
    ${acc_id}=    SalesforceAPI.Find Account By Name    ${TEST_ACCOUNT_NAME}
    Set Suite Variable    ${ACCOUNT_ID}    ${acc_id}
    Log    Using Account: ${TEST_ACCOUNT_NAME} (${acc_id})

# ── Composite Workflow Keywords ───────────────────────────────────

Reset Test Account
    [Documentation]    Navigates to the test Account and runs the Reset Account flow.
    ...    Clears transactional data (Opportunities, Quotes, Orders, Assets).
    [Arguments]    ${account_id}
    Navigate To Account    ${account_id}
    Click Highlights Panel Action    Reset Account
    Sleep    5s    reason=Allow Reset Account flow to initialize
    Advance Through Flow Screens
    Dismiss Toast If Present
    Capture Step Screenshot    account_reset

Create Opportunity From Account
    [Documentation]    Creates an Opportunity via the New Opportunity QuickAction on an Account page.
    ...    Returns the new Opportunity Id found via API.
    [Arguments]    ${account_id}
    Navigate To Account    ${account_id}
    Click Highlights Panel Action    New Opportunity
    Wait For Modal
    Save Modal
    Sleep    3s    reason=Allow Opportunity creation to complete
    ${opp_id}=    Wait For Related Record Via API
    ...    SELECT Id FROM Opportunity WHERE AccountId = '${account_id}' ORDER BY CreatedDate DESC LIMIT 1
    Dismiss Toast If Present
    Log    Created Opportunity: ${opp_id}
    RETURN    ${opp_id}

Create Quote From Opportunity
    [Documentation]    Creates a Quote via the New Quote QuickAction on an Opportunity page.
    ...    Returns the new Quote Id found via API.
    [Arguments]    ${opportunity_id}
    Navigate To Opportunity    ${opportunity_id}
    Click Highlights Panel Action    New Quote
    Sleep    5s    reason=Allow Flow to initialize
    Save Modal    Save
    Sleep    3s    reason=Allow Quote creation to complete
    ${q_id}=    Wait For Related Record Via API
    ...    SELECT Id FROM Quote WHERE OpportunityId = '${opportunity_id}' ORDER BY CreatedDate DESC LIMIT 1
    Dismiss Toast If Present
    Log    Created Quote: ${q_id}
    RETURN    ${q_id}

Add Products Via Browse Catalogs
    [Documentation]    Opens Browse Catalogs on a Quote, selects a catalog, searches for a product,
    ...    adds it, and saves the quote. Handles the Choose Price Book modal if it appears.
    [Arguments]    ${quote_id}    ${catalog_name}    ${product_name}
    Navigate To Quote    ${quote_id}
    Click Browse Catalogs
    Select Catalog By Name    ${catalog_name}
    Search Product In Catalog    ${product_name}
    Add Product By Name    ${product_name}
    Sleep    2s    reason=Allow product addition to register
    Click Save Quote In Catalog
    Capture Step Screenshot    products_added
    Sleep    5s    reason=Allow pricing to process

Create Order From Quote
    [Documentation]    Creates a single Order from a Quote via the Create Order flow.
    ...    Selects "Create Single Order" and advances through the flow.
    ...    Returns the new Order Id found via API.
    [Arguments]    ${quote_id}
    Navigate To Quote    ${quote_id}
    Click Highlights Panel Action    Create Order
    Sleep    5s    reason=Allow CreateOrder flow to initialize
    Select Order Creation Method
    Advance Through Flow Screens
    Dismiss Toast If Present
    ${order_id}=    Wait For Related Record Via API
    ...    SELECT Id FROM Order WHERE QuoteId = '${quote_id}' ORDER BY CreatedDate DESC LIMIT 1
    Log    Created Order: ${order_id}
    RETURN    ${order_id}

Activate Order
    [Documentation]    Navigates to an Order, clicks Activate, confirms the dialog,
    ...    and waits for the Order status to become Activated.
    [Arguments]    ${order_id}
    Navigate To Order    ${order_id}
    Click Highlights Panel Action    Activate
    Confirm Modal Action    Activate
    Dismiss Toast If Present
    Wait For Field Value Via API    Order    ${order_id}    Status    Activated
    Capture Step Screenshot    order_activated

Confirm Modal Action
    [Documentation]    Clicks a confirmation button inside a modal dialog footer.
    ...    Retries for up to 15 seconds to allow the modal to render.
    ...    Used for standard Aura confirmation dialogs (e.g. "Activate order?").
    [Arguments]    ${button_label}=Activate
    Wait Until Keyword Succeeds    15s    2s    _Click Modal Footer Button    ${button_label}
    Sleep    3s    reason=Allow action to process

_Click Modal Footer Button
    [Documentation]    Internal keyword — finds and clicks a button inside a modal footer via JS.
    [Arguments]    ${button_label}
    ${result}=    Execute JavaScript
    ...    return (function(label){
    ...        var footers = document.querySelectorAll('div.modal-footer, div.slds-modal__footer, footer.slds-modal__footer');
    ...        for (var f = 0; f < footers.length; f++) {
    ...            var btns = footers[f].querySelectorAll('button');
    ...            for (var i = 0; i < btns.length; i++) {
    ...                var txt = btns[i].textContent.trim();
    ...                var title = btns[i].getAttribute('title') || '';
    ...                if (txt === label || title === label) {
    ...                    btns[i].click();
    ...                    return 'clicked';
    ...                }
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${button_label}
    Log    Modal footer button result: ${result}
    IF    "${result}" == "not_found"
        Capture Step Screenshot    modal_button_not_found
        Fail    msg=${button_label} button not found in modal footer (will retry).
    END

# ── Record ID Extraction ────────────────────────────────────────────

Get Record Id From Url
    [Documentation]    Extracts a Salesforce record Id from the current page URL.
    ...    Returns the 18-character Id from a URL like /lightning/r/SObject/001.../view.
    ${url}=    Get Location
    ${id}=    Evaluate    __import__('re').search(r'/([a-zA-Z0-9]{15,18})/view', $url).group(1) if __import__('re').search(r'/([a-zA-Z0-9]{15,18})/view', $url) else ''
    IF    "${id}" == ""
        # Try alternate URL patterns (e.g. after flow completion)
        ${id}=    Evaluate    __import__('re').search(r'/([a-zA-Z0-9]{15,18})(?:\\?|$|#)', $url).group(1) if __import__('re').search(r'/([a-zA-Z0-9]{15,18})(?:\\?|$|#)', $url) else ''
    END
    RETURN    ${id}

Wait For Record Page And Get Id
    [Documentation]    Waits for a record page to load and extracts the record Id from the URL.
    [Arguments]    ${sobject}    ${timeout}=30s
    Wait Until Keyword Succeeds    ${timeout}    3s    _Page Url Should Contain Record    ${sobject}
    Sleep    ${LIGHTNING_RENDER_WAIT}    reason=Allow page to finish rendering
    ${id}=    Get Record Id From Url
    RETURN    ${id}

_Page Url Should Contain Record
    [Arguments]    ${sobject}
    ${url}=    Get Location
    Should Match Regexp    ${url}    /lightning/r/${sobject}/[a-zA-Z0-9]{15,18}

# ── Async Wait Keywords ─────────────────────────────────────────────

Wait For Field Value Via API
    [Documentation]    Polls a record field via REST API until it matches the expected value.
    ...    Uses Wait Until Keyword Succeeds for retry logic.
    [Arguments]    ${sobject}    ${record_id}    ${field_name}    ${expected_value}    ${timeout}=${ASYNC_TIMEOUT}    ${interval}=${ASYNC_POLL_INTERVAL}
    Wait Until Keyword Succeeds    ${timeout}    ${interval}
    ...    SalesforceAPI.Verify Field Value Via API    ${sobject}    ${record_id}    ${field_name}    ${expected_value}

Wait For Related Record Via API
    [Documentation]    Polls a SOQL query until at least one record is returned.
    ...    Returns the Id of the first matching record.
    [Arguments]    ${soql}    ${timeout}=${ASYNC_TIMEOUT}    ${interval}=${ASYNC_POLL_INTERVAL}
    ${id}=    Wait Until Keyword Succeeds    ${timeout}    ${interval}
    ...    SalesforceAPI.Verify Related Record Exists    ${soql}
    RETURN    ${id}

# ── Verification ─────────────────────────────────────────────────────

Verify Page Contains Text
    [Documentation]    Asserts that the current page contains the specified text.
    [Arguments]    ${text}    ${timeout}=15s
    Wait Until Page Contains    ${text}    timeout=${timeout}

# ── Screenshots ──────────────────────────────────────────────────────

Capture Step Screenshot
    [Documentation]    Captures a screenshot with a descriptive step-name prefix.
    ...    Increments a counter to ensure unique filenames.
    [Arguments]    ${step_name}=step
    ${counter}=    Evaluate    ${SCREENSHOT_COUNTER} + 1
    Set Suite Variable    ${SCREENSHOT_COUNTER}    ${counter}
    Capture Page Screenshot    filename=e2e_${counter}_${step_name}.png

# ── Toast Handling ───────────────────────────────────────────────────

Dismiss Toast If Present
    [Documentation]    Clicks the close button on any visible Salesforce toast messages.
    ...    Uses both XPath and shadow DOM JS traversal for LWC toast components.
    ${close_btns}=    Get WebElements    xpath=//button[contains(@class, 'toastClose') or (@title='Close' and ancestor::*[contains(@class, 'toast')])]
    FOR    ${btn}    IN    @{close_btns}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${btn}
        Run Keyword If    ${visible}    Click Element    ${btn}
    END
    # Fallback: dismiss toasts inside shadow DOM (LWC lightning-notification)
    Execute JavaScript
    ...    (function(){
    ...        function findAll(root, tag) {
    ...            var found = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === tag) found.push(all[i]);
    ...                if (all[i].shadowRoot) found = found.concat(findAll(all[i].shadowRoot, tag));
    ...            }
    ...            return found;
    ...        }
    ...        var toasts = document.querySelectorAll('lightning-notification-toast, div.forceToastManager');
    ...        for (var t = 0; t < toasts.length; t++) {
    ...            var root = toasts[t].shadowRoot || toasts[t];
    ...            var btns = findAll(root, 'BUTTON');
    ...            for (var i = 0; i < btns.length; i++) {
    ...                if (btns[i].title === 'Close' || btns[i].getAttribute('aria-label') === 'Close') {
    ...                    try { btns[i].click(); } catch(e) {}
    ...                }
    ...            }
    ...        }
    ...    })()
    Sleep    0.5s

# ── Recording / Debug ───────────────────────────────────────────────

Pause For Recording If Enabled
    [Documentation]    Pauses test execution when \${PAUSE_FOR_RECORDING} is true.
    ...    Use this at key steps to inspect the DOM via Chrome DevTools (port 9222).
    ...    Press Enter in the terminal to resume.
    [Arguments]    ${message}=Test paused for recording. Press Enter to continue.
    IF    "${PAUSE_FOR_RECORDING}" == "true"
        Log    ${message}    WARN
        ${cdp_url}=    Get Cdp Websocket Url
        Log    CDP WebSocket URL: ${cdp_url}    WARN
        Evaluate    print("\\n" + "=" * 60 + "\\n  PAUSED: ${message}\\n  CDP: " + """${cdp_url}""" + "\\n" + "=" * 60)
        Evaluate    input("  Press Enter to resume...")
        Evaluate    print("  RESUMED\\n" + "=" * 60 + "\\n")
    END

# ── Verification ─────────────────────────────────────────────────────

Verify Assets Exist On Account
    [Documentation]    Checks that at least 1 Asset exists on the Account. Fails if not (for retry).
    [Arguments]    ${account_id}
    ${asset_count}=    SalesforceAPI.Get Asset Count For Account    ${account_id}
    Log    Asset count: ${asset_count}
    Should Be True    ${asset_count} > 0
    ...    msg=No assets yet on Account ${account_id} (will retry).
