*** Settings ***
Documentation     Shared keywords for E2E functional tests. Provides navigation,
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
# Quote.CalculationStatus groups (264 picklist). Any value ending in "Failed" also counts as
# failed; see Wait For Quote Calculation.
@{QUOTE_CALC_FAILED}        SaveFailedOrIncomplete    QuoteRequestPartiallySaved    PartialSaveSuccess
@{QUOTE_CALC_PRICED}        CompletedWithPricing    CompletedWithTax    TaxCalculationSuccess

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
    ...    Set Log Level NONE wraps both URL retrieval and navigation to prevent
    ...    the session token from appearing in Robot log.html/CI artifacts.
    [Arguments]    ${app_name}
    ${app_api_name}=    Evaluate    'RLM_' + $app_name.replace(' ', '_')
    ${prev_level}=    Set Log Level    NONE
    ${url}=    Get Authenticated Url    /lightning/app/c__${app_api_name}
    Go To    ${url}
    Set Log Level    ${prev_level}
    Wait Until Page Contains Element    css:body    timeout=${PAGE_LOAD_TIMEOUT}
    Sleep    ${LIGHTNING_RENDER_WAIT}    reason=Allow app to load
    Log    Navigated to app: ${app_name}

Navigate To Record
    [Documentation]    Navigates to a Salesforce record page by SObject type and Id.
    ...    Set Log Level NONE wraps both URL retrieval and navigation to prevent
    ...    the session token from appearing in Robot log.html/CI artifacts.
    [Arguments]    ${sobject}    ${record_id}
    ${prev_level}=    Set Log Level    NONE
    ${url}=    Get Authenticated Url    /lightning/r/${sobject}/${record_id}/view
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
    ...    Fails if the flow/modal is still open after max_screens iterations to
    ...    surface stuck or unexpectedly deep flows rather than silently continuing.
    ...
    ...    ⚠ The broad search looks only inside the open flow/modal, never the whole page. Live
    ...    2026-10-13: when the Create Order picker's radio hadn't registered, Finish couldn't
    ...    advance, and a page-wide search for "Create Order" found the RECORD PAGE's Create
    ...    Order button behind the modal, relaunching the flow ten times until max_screens.
    [Arguments]    ${max_screens}=${10}
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
        ...        /* 3. Broad search, scoped to the open flow/modal (shadow DOM included) */
        ...        function deepAll(root, sel, out, depth) {
        ...            if (depth > 30) return out;
        ...            var els = root.querySelectorAll(sel);
        ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
        ...            var all = root.querySelectorAll('*');
        ...            for (var j = 0; j < all.length; j++) {
        ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
        ...            }
        ...            return out;
        ...        }
        ...        var containers = deepAll(document, 'flowruntime-flow, section.slds-modal, div.modal-container', [], 0);
        ...        var allBtns = [];
        ...        for (var c = 0; c < containers.length; c++) {
        ...            allBtns = allBtns.concat(findAllButtons(containers[c]));
        ...            if (containers[c].shadowRoot) { allBtns = allBtns.concat(findAllButtons(containers[c].shadowRoot)); }
        ...        }
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
    # If we exhaust max_screens without the flow closing, fail explicitly
    ${flow_still_open}=    Run Keyword And Return Status    Page Should Contain Element
    ...    xpath=//flowruntime-flow | //div[contains(@class,'modal-container')] | //section[contains(@class,'slds-modal')]
    IF    ${flow_still_open}
        Fail    msg=Flow did not complete after ${max_screens} screens. The flow may have more screens than expected or may be stuck. Increase max_screens or investigate the flow state.
    END

# ── Create Order ───────────────────────────────────────────────────

Select Order Creation Method
    [Documentation]    Selects "Create Single Order" in the Create Order flow's
    ...    order-creation-method-picker and clicks Next/Finish.
    ...    The picker uses radio inputs inside runtime_rca-order-creation-method-picker
    ...    which is nested in shadow DOM.
    ...    ⚠ A click is not a selection. Live 2026-10-13: the radio click returned success while the
    ...    tile stayed unselected, so Finish couldn't advance. The radio must read back `checked`
    ...    (falling back to its label), or the step fails and retries.
    Wait Until Keyword Succeeds    15s    3s    _Select Single Order Radio Via JS
    Sleep    2s    reason=Allow selection to register
    # Again after the settle: the LWC picker can re-render the radio unchecked after the click, and
    # the read-back above is synchronous. The keyword returns early when it is still checked.
    Wait Until Keyword Succeeds    15s    3s    _Select Single Order Radio Via JS
    # Click Finish to advance past the picker screen
    Save Modal    Finish

_Select Single Order Radio Via JS
    [Documentation]    Internal keyword — selects the Create Single Order radio via JS, and succeeds
    ...    only when the radio reads back `checked` (otherwise returns `not_checked`, which retries).
    ...    Returns early, without clicking, when it is already checked.
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
    ...        /* Find radio with value="CreateSingleOrder"; only a radio left CHECKED counts */
    ...        var radios = deepQueryAll(document, 'input[value="CreateSingleOrder"]');
    ...        for (var i = 0; i < radios.length; i++) {
    ...            if (radios[i].checked) { return 'selected'; }
    ...            radios[i].click();
    ...            if (radios[i].checked) { return 'selected'; }
    ...            var root = radios[i].getRootNode();
    ...            var lbl = radios[i].id && root.querySelector ? root.querySelector('label[for="' + radios[i].id + '"]') : null;
    ...            if (lbl) { lbl.click(); if (radios[i].checked) { return 'selected_by_label'; } }
    ...            return 'not_checked';
    ...        }
    ...        /* Fallback: find the visual picker div with data-id="single-order" */
    ...        var pickers = deepQueryAll(document, 'div[data-id="single-order"]');
    ...        for (var i = 0; i < pickers.length; i++) {
    ...            var radio = pickers[i].querySelector('input[type="radio"]');
    ...            if (!radio) continue;
    ...            if (!radio.checked) { radio.click(); }
    ...            var label = pickers[i].querySelector('label');
    ...            if (!radio.checked && label) { label.click(); }
    ...            return radio.checked ? 'selected_by_picker' : 'not_checked';
    ...        }
    ...        return 'not_found';
    ...    })()
    Log    Select Order Creation Method JS result: ${result}
    IF    "${result}" == "not_found" or "${result}" == "not_checked"
        Capture Step Screenshot    order_method_not_found
        Fail    msg=Create Single Order radio not selected (${result}) (will retry).
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
    ...
    ...    When a Default Catalog is configured in Product Discovery Settings (see
    ...    configure_product_discovery_settings.robot), Browse Catalogs skips the All
    ...    Catalogs picker entirely and opens directly into Browse Products for that
    ...    catalog — there is no datatable to select from and no Next button. Detect
    ...    that case up front and skip the picker interaction instead of failing.
    ...
    ...    The direct-browse heading and the legacy picker datatable are checked together,
    ...    every retry, for the full window the legacy path itself gets (30s) — checking one
    ...    for a short window and then unconditionally falling back to the other is a race: a
    ...    slow-rendering direct-browse heading would fall through to the legacy picker wait,
    ...    which can never succeed because no datatable exists in that build.
    [Arguments]    ${catalog_name}
    ${state}=    Set Variable    unknown
    FOR    ${i}    IN RANGE    10
        ${state}=    _Detect Catalog Picker State    ${catalog_name}
        IF    "${state}" != "unknown"    BREAK
        Sleep    3s    reason=Allow Browse Catalogs modal to finish rendering before checking state
    END
    IF    "${state}" == "already_browsing"
        Log    Catalog picker skipped — Browse Catalogs opened directly into "${catalog_name}" (Default Catalog configured).
        RETURN
    END
    Wait Until Keyword Succeeds    30s    3s    _Dismiss Or Select Catalog    ${catalog_name}
    Sleep    2s    reason=Allow selection to register
    # Click Next in the flow navigation bar
    Save Modal    Next
    Sleep    5s    reason=Allow catalog selection to process

_Detect Catalog Picker State
    [Documentation]    Internal keyword — checks, in one pass, whether Browse Catalogs opened
    ...    directly into product browsing for ${catalog_name} (Default Catalog configured; no
    ...    picker datatable will ever appear) or whether the legacy All Catalogs picker
    ...    datatable is present (rows keyed by `data-row-key-value`, same traversal
    ...    `_Select Catalog Radio Via JS` uses). Returns 'already_browsing', 'picker_present',
    ...    or 'unknown' if neither has rendered yet — the caller retries on 'unknown'.
    [Arguments]    ${catalog_name}
    ${result}=    Execute JavaScript
    ...    return (function(name){
    ...        function findHeadings(root, acc) {
    ...            root.querySelectorAll('h1,h2').forEach(function(el){acc.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findHeadings(el.shadowRoot,acc);});
    ...        }
    ...        var heads = []; findHeadings(document, heads);
    ...        for (var i=0;i<heads.length;i++) {
    ...            if (heads[i].textContent.trim() === ('Catalog: ' + name)) return 'already_browsing';
    ...        }
    ...        function findRows(root, acc) {
    ...            root.querySelectorAll('tr[data-row-key-value]').forEach(function(el){acc.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findRows(el.shadowRoot,acc);});
    ...        }
    ...        var rows = []; findRows(document, rows);
    ...        if (rows.length > 0) { return 'picker_present'; }
    ...        return 'unknown';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${catalog_name}
    RETURN    ${result}

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
    [Documentation]    Internal keyword — finds the product's row and clicks the Add button in that
    ...    same row via JS.
    ...
    ...    ⚠ The row is NOT reachable with a plain `document.querySelectorAll`. Live DOM
    ...    2026-10-13: `runtime_industries_cpq-product-row` sits eight shadow roots deep (flow
    ...    runtime → `runtime_revenue_products-prd-lst-container` →
    ...    `runtime_industries_cpq-product-list-page` → `runtime_industries_cpq-product-data-table`
    ...    → a table cell), and the product title (`title="<name>"`) and its Add button
    ...    (`name="Add"`, `title="Add"`) both live inside that row's shadow tree. The search
    ...    descends every shadow root to find the rows, then matches title and button within one row.
    ...    ⚠ There is deliberately no "first Add button on the page" fallback. The previous version
    ...    used one, and since its row lookup never matched, every run clicked whichever Add
    ...    rendered first, product-agnostic. A row that isn't found now fails and is retried.
    [Arguments]    ${product_name}
    ${result}=    Execute JavaScript
    ...    return (function(name){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 30) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        function isTitle(el) {
    ...            if (el.getAttribute('title') === name) return true;
    ...            return el.childElementCount === 0 && (el.textContent || '').trim() === name;
    ...        }
    ...        var rows = deepAll(document, 'runtime_industries_cpq-product-row', [], 0);
    ...        if (rows.length === 0) { return 'no_product_rows'; }
    ...        for (var i = 0; i < rows.length; i++) {
    ...            var root = rows[i].shadowRoot || rows[i];
    ...            var inRow = deepAll(root, '*', [], 0);
    ...            var titled = false;
    ...            for (var t = 0; t < inRow.length; t++) { if (isTitle(inRow[t])) { titled = true; break; } }
    ...            if (!titled) continue;
    ...            var btns = deepAll(root, 'button', [], 0);
    ...            for (var b = 0; b < btns.length; b++) {
    ...                if (btns[b].getAttribute('name') === 'Add' || btns[b].getAttribute('title') === 'Add' ||
    ...                    (btns[b].textContent || '').trim() === 'Add') {
    ...                    if (btns[b].disabled || btns[b].getAttribute('aria-disabled') === 'true') { return 'add_button_disabled'; }
    ...                    btns[b].click();
    ...                    return 'added:' + name;
    ...                }
    ...            }
    ...            return 'add_button_not_found';
    ...        }
    ...        return 'product_row_not_found:' + rows.length + '_rows';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${product_name}
    Log    Add Product JS result: ${result}
    IF    not $result.startswith("added:")
        Capture Step Screenshot    add_product_not_found
        Fail    msg=Product "${product_name}" row or its Add button not ready (${result}) (will retry).
    END

Click Save Quote In Catalog
    [Documentation]    Saves the Browse Catalogs selection, then confirms ${product_name} is a saved
    ...    line on ${quote_id} before moving on. Clicks the "Save Quote" button if present.
    ...    Waits for the button to become enabled before clicking. The button has
    ...    data-id="objectActionButton" and title="Save Quote".
    ...
    ...    Newer Browse Catalogs builds auto-save each product addition immediately (the
    ...    Quote Summary total behind the modal updates live) and have no Save Quote button
    ...    at all — only "Close". Detect absence up front with a quick, retried presence probe
    ...    (NOT the enablement wait below) before falling back to auto-save/Close — a button
    ...    that is present but slow to enable must still get the full enablement wait, not be
    ...    mistaken for an absent one and have its modal closed unsaved.
    ...
    ...    ⚠ "Auto-saves" is not immediate. Live 2026-10-13: the modal showed the product added
    ...    ("View Quote Lines (1)", green check on the card) while the Quote Summary behind it was
    ...    still USD 0.00, and closing ~5s after the click left the Quote with ZERO lines. The
    ...    failure then surfaced a minute later as `line_not_found` in Configure Bundle Line. So on
    ...    the auto-save path the modal stays open until the API shows the line saved, and on the
    ...    Save Quote path the line is checked the same way after the save.
    [Arguments]    ${quote_id}    ${product_name}
    SalesforceAPI.Validate Salesforce Id    ${quote_id}
    ${product_id}=    SalesforceAPI.Find Product By Name    ${product_name}
    SalesforceAPI.Validate Salesforce Id    ${product_id}
    ${line_soql}=    Set Variable
    ...    SELECT Id FROM QuoteLineItem WHERE QuoteId = '${quote_id}' AND Product2Id = '${product_id}' LIMIT 1
    ${present}=    Set Variable    no
    FOR    ${i}    IN RANGE    5
        ${present}=    _Save Quote Button Present
        IF    "${present}" == "yes"    BREAK
        Sleep    1s    reason=Allow Browse Catalogs modal to finish rendering before checking state
    END
    IF    "${present}" == "yes"
        Wait Until Keyword Succeeds    30s    2s    _Click Save Quote Via JS
        Sleep    5s    reason=Allow quote to save and modal to close
        _Wait For Saved Quote Line    ${line_soql}    ${quote_id}    ${product_name}
    ELSE
        Log    Save Quote button not present — Browse Catalogs auto-saves; waiting for the line to save before closing.
        _Wait For Saved Quote Line    ${line_soql}    ${quote_id}    ${product_name}
        Wait Until Keyword Succeeds    30s    3s    _Click Close Browse Catalogs Modal
        Sleep    3s    reason=Allow modal to close and the quote page to refresh
    END

_Wait For Saved Quote Line
    [Documentation]    Internal keyword — polls the API for the saved quote line, failing with a
    ...    screenshot and a message that names the quote and product. (For a QUOTE_ID passed into
    ...    order_from_quote.robot that already carries the product, this passes at once.)
    [Arguments]    ${line_soql}    ${quote_id}    ${product_name}
    ${saved}=    Run Keyword And Return Status
    ...    Wait For Related Record Via API    ${line_soql}    timeout=60s    interval=3s
    IF    not ${saved}
        Capture Step Screenshot    quote_line_not_saved
        Fail    msg=Browse Catalogs showed "${product_name}" added, but no saved quote line appeared on ${quote_id} within 60s.
    END

_Save Quote Button Present
    [Documentation]    Internal keyword — quick, non-retrying check for whether the Save Quote
    ...    button exists in the DOM at all, regardless of its enabled/disabled state.
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
    ...            if (allBtns[i].getAttribute('title') === 'Save Quote' || allBtns[i].textContent.trim() === 'Save Quote') {
    ...                return 'yes';
    ...            }
    ...        }
    ...        return 'no';
    ...    })()
    RETURN    ${result}

_Click Close Browse Catalogs Modal
    [Documentation]    Internal keyword — clicks the "Close" button in the Browse Catalogs
    ...    modal footer via JS with shadow DOM traversal.
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
    ...            if (allBtns[i].textContent.trim() === 'Close') {
    ...                allBtns[i].click();
    ...                return 'clicked';
    ...            }
    ...        }
    ...        return 'not_found';
    ...    })()
    IF    "${result}" == "not_found"
        Fail    msg=Close button not found in Browse Catalogs modal (will retry).
    END

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

# ── Bundle Configurator ────────────────────────────────────────────

Configure Bundle Line
    [Documentation]    Opens the product configurator on a bundle PARENT quote line, selects an
    ...    optional component, and commits with "Save & Exit".
    ...
    ...    ⚠ The configurator is reached from the row-level actions dropdown on the RIGHT of each
    ...    line ("Show Actions" → Configure). It is NOT a gear icon and NOT the "+" affordance
    ...    beside it.
    ...    ⚠ Configure the BUNDLE PARENT only. Child lines carry their own action menus; opening
    ...    one of those configures the wrong product.
    ...
    ...    Every selector below was read off the live DOM on 2026-07-28, not inferred.
    ...
    ...    ⚠ The retries here are LOAD-BEARING, not padding: on a live run the menu items, the
    ...    modal tabs and the modal footer each miss on their first attempt and succeed on a
    ...    later one. Screenshots from those attempts are suffixed `_retry` — seeing
    ...    `configurator_tab_retry.png` in a results folder does NOT mean the run failed.
    ...
    ...    ⚠ The whole configurator pass is retried once from a fresh page. Live 2026-10-13,
    ...    intermittently: the configurator opened on "Something went wrong while hydrating the
    ...    context. We couldn't process your request. Try again." and rendered no tabs. Selecting
    ...    the option is idempotent (``already_selected``), so a second pass after a commit that
    ...    did land is harmless. The hydration error came right after a failed pricing call and
    ...    recurred on an immediate retry, so the retry first clears the quote
    ...    (``_Clear Quote Calculation``).
    ...    ⚠ A pass only counts once the API shows ${option_name}'s quote line. CalculationStatus
    ...    alone can't tell: right after "Save & Exit" it still reads the previous CompletedWithTax.
    ...    The line proves the save landed, not that repricing has started; the fixed sleep before
    ...    the pricing wait, and the time until Create Order, are what let repricing begin. That
    ...    guard is timing-based: a reprice that starts much later would still be missed.
    ...    Before the retry pass the API is checked again: a line that saved late means the first
    ...    commit landed, and a second pass on an unchanged configuration could find "Save & Exit"
    ...    disabled.
    ...    Live 2026-10-13: Save & Exit hadn't saved the option, the order was created without it,
    ...    and the renewal Opportunity came out one line short, so the renewal check timed out
    ...    3 minutes later with nothing pointing at the configurator.
    [Arguments]    ${quote_id}    ${line_name}    ${option_name}    ${tab_label}=${EMPTY}
    ${configured}    ${reason}=    Run Keyword And Ignore Error
    ...    _Configure Bundle Line Once    ${quote_id}    ${line_name}    ${option_name}    ${tab_label}
    IF    "${configured}" == "FAIL"
        Capture Step Screenshot    configurator_failed_retrying
        Log    Configuring "${line_name}" on ${quote_id} failed (${reason}); retrying once from a fresh page.    WARN
        _Clear Quote Calculation    ${quote_id}
        ${saved_late}=    _Quote Has Product Line    ${quote_id}    ${option_name}
        IF    not ${saved_late}
            _Configure Bundle Line Once    ${quote_id}    ${line_name}    ${option_name}    ${tab_label}
        END
    END
    Sleep    8s    reason=Allow the configuration to commit and repricing to start
    Wait For Quote Calculation    ${quote_id}    require_priced=${True}
    Capture Step Screenshot    configurator_saved

_Configure Bundle Line Once
    [Documentation]    Internal keyword — one configurator pass for Configure Bundle Line: open the
    ...    line's configurator, pick the tab and option, and commit with "Save & Exit".
    [Arguments]    ${quote_id}    ${line_name}    ${option_name}    ${tab_label}
    Navigate To Quote    ${quote_id}
    Sleep    3s    reason=Let the ag-Grid line-items grid finish rendering before we inspect it
    Capture Step Screenshot    before_line_action_open
    Wait Until Keyword Succeeds    60s    3s    _Open Line Action Menu    ${line_name}
    Capture Step Screenshot    after_line_action_open
    Wait Until Keyword Succeeds    30s    2s    _Click Line Action    Configure
    Capture Step Screenshot    configurator_opened
    IF    "${tab_label}" != "${EMPTY}"
        Wait Until Keyword Succeeds    60s    3s    _Select Configurator Tab    ${tab_label}
    END
    Wait Until Keyword Succeeds    60s    3s    _Select Configurator Option    ${option_name}
    Capture Step Screenshot    configurator_option_selected
    Wait Until Keyword Succeeds    30s    3s    _Commit Configurator
    Wait Until Keyword Succeeds    60s    3s    _Quote Should Have Product Line    ${quote_id}    ${option_name}

_Quote Should Have Product Line
    [Documentation]    Internal keyword — fails (for retry) until ${quote_id} has a line for ${product_name}.
    [Arguments]    ${quote_id}    ${product_name}
    ${found}=    _Quote Has Product Line    ${quote_id}    ${product_name}
    Should Be True    ${found}
    ...    msg=No saved "${product_name}" line on ${quote_id} yet (will retry).

_Open Line Action Menu
    [Documentation]    Internal keyword — opens the row-level actions dropdown for a quote line.
    ...
    ...    The line grid is ag-Grid, and it is split into separate PINNED-LEFT / CENTER row
    ...    containers per visual row — confirmed live: the `div[role="row"]` matching the product
    ...    name's `row-id` has a bounding rect only ~250px wide (pinned-left section: checkbox,
    ...    name, disclosure toggle only); the "+"/actions-trigger icons at the row's far right live
    ...    in a DIFFERENT `div[role="row"]` container that does NOT share the same `row-id`/
    ...    `row-index` attribute (or isn't reachable from the same shadow-DOM subtree) — row-id
    ...    joining across sections does not work here, despite being standard ag-Grid behavior
    ...    elsewhere.
    ...    ⚠ The row-action icon is `visibility:hidden` until the row is hovered (confirmed live
    ...    via computed style) — CSS-gated, same as ag-Grid's stock hover-reveal actions column.
    ...    We must dispatch a genuine, trusted `Mouse Over` on the row BEFORE searching for the
    ...    icon, not after: searching first and hovering only on success is circular (the icon
    ...    a pre-hover search finds is never the real trigger). This is a two-phase JS call: find
    ...    the row and stash it, hover it from Robot (trusted event), THEN search for the icon.
    ...    ⚠ `icon-name` is NOT a reliable discriminator — the disclosure toggle AND the real
    ...    actions-trigger icon can both report an empty `icon-name` depending on the render pass.
    ...    Position is reliable: the disclosure toggle sits near the row's left edge (~x=110); the
    ...    real actions trigger sits in the right ~40% of the viewport. Filter candidates on
    ...    `left > innerWidth * 0.6`, excluding the decorative "utility:lock" icon by name, then
    ...    take the rightmost survivor.
    ...    ⚠ We DO NOT scope the icon search to any row container. We take the product-name row's
    ...    vertical CENTER (`getBoundingClientRect()`, not `top`) and search the ENTIRE document
    ...    (all shadow roots) for clickable elements (`button`, `a`, `[role="button"]`,
    ...    `lightning-icon`, `lightning-button-icon` — the real trigger is a plain `button`, not
    ...    an icon) whose own vertical center is within 15px of it — this finds the trigger
    ...    regardless of which ag-Grid section container (pinned-left vs center) it actually
    ...    renders in.
    ...    ⚠ A raw JS `.click()` on the found element is NOT equivalent to a real click — it does
    ...    not check visibility (so it "succeeds" against a still-hidden button) and dispatches an
    ...    untrusted event that some LWC/Aura components reject, surfacing as an empty dropdown +
    ...    a genuine "Sorry to interrupt / CSS Error" toast. We return the DOM element itself
    ...    (Robot/Selenium wraps it as a real WebElement) and use native `Click Element` — a
    ...    trusted click — after `scrollIntoView`.
    ...    Clicking a bare `lightning-icon` does nothing — walk up to the nearest real clickable
    ...    ancestor (`button`, `a`, a `lightning-button-icon`'s shadow-root `button`, or
    ...    `role="button"`), crossing shadow-root boundaries via `getRootNode().host` when
    ...    `parentElement` is null. It is not a `lightning-button-menu` any more either.
    ...    ⚠ Previously, clicking the disclosure toggle by mistake collapsed the bundle's child
    ...    lines AND reliably produced the same "Sorry to interrupt / CSS Error" — do not
    ...    reintroduce a fallback that clicks the leftmost/disclosure icon.
    ...    ⚠ Hierarchy level does NOT identify the bundle parent — every row is `ag-row-level-0`,
    ...    children included. Match on the product name.
    [Arguments]    ${line_name}
    ${row_result}=    Execute JavaScript
    ...    return (function(name){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        var scrollers = deepAll(document, '.ag-center-cols-viewport, .ag-body-horizontal-scroll-viewport, [class*="scroll"]', [], 0);
    ...        for (var s = 0; s < scrollers.length; s++) { scrollers[s].scrollLeft = scrollers[s].scrollWidth; }
    ...        var rows = deepAll(document, 'div[role="row"]', [], 0);
    ...        var targetRow = null;
    ...        for (var i = 0; i < rows.length; i++) {
    ...            if ((rows[i].innerText || '').indexOf(name) !== -1) { targetRow = rows[i]; break; }
    ...        }
    ...        if (!targetRow) { return 'line_not_found'; }
    ...        window.__e2eRow = targetRow;
    ...        return 'row_found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${line_name}
    Log    Find quote line row: ${row_result}
    IF    "${row_result}" != "row_found"
        Capture Step Screenshot    line_action_menu_retry
        Fail    msg=Could not find quote line "${line_name}" (${row_result}) (will retry).
    END
    ${row_element}=    Execute JavaScript    return window.__e2eRow
    Execute JavaScript    arguments[0].scrollIntoView({block: 'center', inline: 'center'});    ARGUMENTS    ${row_element}
    Mouse Over    ${row_element}
    Sleep    0.3s    reason=Let the CSS :hover transition reveal the row-action icon (it is visibility:hidden until hover)
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        function clickableAncestor(el) {
    ...            var cur = el;
    ...            var depth = 0;
    ...            while (cur && depth < 15) {
    ...                if (cur.tagName === 'BUTTON' || cur.tagName === 'A') { return cur; }
    ...                if (cur.tagName === 'LIGHTNING-BUTTON-ICON' && cur.shadowRoot) {
    ...                    var b = cur.shadowRoot.querySelector('button');
    ...                    if (b) { return b; }
    ...                }
    ...                if (cur.getAttribute && cur.getAttribute('role') === 'button') { return cur; }
    ...                var root = cur.getRootNode ? cur.getRootNode() : null;
    ...                cur = cur.parentElement || (root && root.host) || null;
    ...                depth++;
    ...            }
    ...            return null;
    ...        }
    ...        var targetRow = window.__e2eRow;
    ...        var targetRect = targetRow.getBoundingClientRect();
    ...        var targetCenterY = (targetRect.top + targetRect.bottom) / 2;
    ...        var allClickable = deepAll(document, 'button, a, [role="button"], lightning-icon, lightning-button-icon', [], 0);
    ...        var rowClickable = allClickable.filter(function(el){
    ...            var r = el.getBoundingClientRect();
    ...            if (r.width === 0 || r.height === 0) { return false; }
    ...            var cy = (r.top + r.bottom) / 2;
    ...            return Math.abs(cy - targetCenterY) < 15;
    ...        });
    ...        var candidates = rowClickable.filter(function(el){
    ...            var r = el.getBoundingClientRect();
    ...            var n = (el.getAttribute('icon-name') || '') + ' ' + (el.getAttribute('aria-label') || '') + ' ' + (el.title || '');
    ...            if (n.indexOf('lock') !== -1) { return false; }
    ...            return r.left > (window.innerWidth * 0.6);
    ...        });
    ...        var byRight = candidates.slice().sort(function(x, y){
    ...            return y.getBoundingClientRect().left - x.getBoundingClientRect().left;
    ...        });
    ...        for (var c = 0; c < byRight.length; c++) {
    ...            var target = clickableAncestor(byRight[c]);
    ...            if (target) {
    ...                window.__e2eTarget = target;
    ...                var rr = byRight[c].getBoundingClientRect();
    ...                return 'menu_target_found:' + byRight[c].tagName.toLowerCase() + '@' + Math.round(rr.left);
    ...            }
    ...        }
    ...        var dump = rowClickable.map(function(el){
    ...            var r = el.getBoundingClientRect();
    ...            return el.tagName.toLowerCase() + '(' + (el.getAttribute('icon-name') || el.getAttribute('aria-label') || '?') + ')@' + Math.round(r.left);
    ...        });
    ...        return 'row_action_not_found:[centerY=' + Math.round(targetCenterY) + ' vw=' + window.innerWidth + ' icons=' + dump.join(',') + ']';
    ...    })()
    Log    Open line action menu: ${result}
    IF    not $result.startswith("menu_target_found")
        Capture Step Screenshot    line_action_menu_retry
        Fail    msg=Could not open the actions menu for quote line "${line_name}" (${result}) (will retry).
    END
    ${target_element}=    Execute JavaScript    return window.__e2eTarget
    Execute JavaScript    arguments[0].scrollIntoView({block: 'center', inline: 'center'});    ARGUMENTS    ${target_element}
    ${diag}=    Execute JavaScript
    ...    var el = arguments[0]; var r = el.getBoundingClientRect(); var cs = getComputedStyle(el);
    ...    return JSON.stringify({tag: el.tagName, rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], display: cs.display, visibility: cs.visibility, pointerEvents: cs.pointerEvents, opacity: cs.opacity, vw: window.innerWidth, vh: window.innerHeight, elAtCenter: (document.elementFromPoint(r.left + r.width/2, r.top + r.height/2) || {}).tagName});
    ...    ARGUMENTS    ${target_element}
    Log    Target element diagnostic before click: ${diag}
    Click Element    ${target_element}

_Click Line Action
    [Documentation]    Internal keyword — clicks a named item in the open row-action menu.
    ...
    ...    ⚠ The menu items are rendered ASYNCHRONOUSLY after the trigger is clicked — they do
    ...    not exist in the same JS tick. That is why this is a separate, retried keyword rather
    ...    than part of _Open Line Action Menu. Verified live 2026-07-28: querying immediately
    ...    after the click returns zero items.
    [Arguments]    ${action_label}
    ${result}=    Execute JavaScript
    ...    return (function(label){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        var items = deepAll(document, 'lightning-menu-item', [], 0);
    ...        var seen = [];
    ...        for (var i = 0; i < items.length; i++) {
    ...            var a = items[i].shadowRoot ? items[i].shadowRoot.querySelector('a[role="menuitem"]') : null;
    ...            if (!a) { continue; }
    ...            var t = (a.textContent || '').trim();
    ...            seen.push(t);
    ...            if (t === label) {
    ...                window.__e2eTarget = a;
    ...                return 'target_found';
    ...            }
    ...        }
    ...        var menuitems = deepAll(document, '[role="menuitem"]', [], 0);
    ...        for (var m = 0; m < menuitems.length; m++) {
    ...            var mt = (menuitems[m].textContent || '').trim();
    ...            if (mt === label) { window.__e2eTarget = menuitems[m]; return 'target_found_via_role_menuitem'; }
    ...        }
    ...        var panels = deepAll(document, 'div.modal-container, section.slds-modal, div[role="dialog"], div[role="menu"], ul[role="menu"]', [], 0);
    ...        var dump = [];
    ...        for (var p = 0; p < panels.length; p++) {
    ...            var kids = panels[p].querySelectorAll('*');
    ...            var kidTags = [];
    ...            for (var q = 0; q < Math.min(kids.length, 40); q++) { kidTags.push(kids[q].tagName.toLowerCase()); }
    ...            dump.push(panels[p].tagName.toLowerCase() + '.' + (panels[p].className || '') + '[' + kidTags.join(',') + ']');
    ...        }
    ...        var errBoxes = deepAll(document, '.auraErrorBox', [], 0);
    ...        var errText = errBoxes.map(function(e){ return (e.textContent || '').trim().slice(0, 300); }).join(' /// ');
    ...        return 'not_found:[' + seen.join('|') + '] menuitems:[' + menuitems.map(function(e){return (e.textContent||'').trim();}).join('|') + '] panels:[' + dump.join(' ;; ') + '] err:[' + errText + ']';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${action_label}
    Log    Click line action: ${result}
    IF    not ("${result}" == "target_found" or "${result}" == "target_found_via_role_menuitem")
        Capture Step Screenshot    click_line_action_retry
        Fail    msg=Row action "${action_label}" not clickable yet (${result}) (will retry).
    END
    ${target_element}=    Execute JavaScript    return window.__e2eTarget
    Execute JavaScript    arguments[0].scrollIntoView({block: 'center', inline: 'center'});    ARGUMENTS    ${target_element}
    Click Element    ${target_element}

_Select Configurator Tab
    [Documentation]    Internal keyword — selects an option-group tab inside the configurator by
    ...    its `data-label`. Retried because the modal takes several seconds to render.
    [Arguments]    ${tab_label}
    ${result}=    Execute JavaScript
    ...    return (function(label){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        var tabs = deepAll(document, 'a[role="tab"]', [], 0);
    ...        var seen = [];
    ...        for (var i = 0; i < tabs.length; i++) {
    ...            var l = tabs[i].getAttribute('data-label');
    ...            if (!l) { continue; }
    ...            seen.push(l);
    ...            if (l === label) {
    ...                tabs[i].click();
    ...                return 'tab_selected';
    ...            }
    ...        }
    ...        return 'tab_not_found:[' + seen.join('|') + ']';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${tab_label}
    Log    Select configurator tab: ${result}
    IF    "${result}" != "tab_selected"
        Capture Step Screenshot    configurator_tab_retry
        Fail    msg=Configurator tab "${tab_label}" not found (${result}) (will retry).
    END

_Select Configurator Option
    [Documentation]    Internal keyword — ticks an optional component's checkbox in the
    ...    configurator. Idempotent: an already-selected option is a success, not a re-click.
    ...
    ...    ⚠ `textContent` does NOT cross shadow boundaries, and each option renders its product
    ...    name inside a nested shadow root — so a plain textContent match finds nothing and the
    ...    option looks absent. The deepText walker below is required, not defensive coding.
    ...    ⚠ The option list for a tab renders asynchronously after the tab is selected, so this
    ...    is retried.
    [Arguments]    ${option_name}
    ${result}=    Execute JavaScript
    ...    return (function(name){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        function deepText(node, depth) {
    ...            if (depth > 25) return '';
    ...            var t = '';
    ...            var kids = node.childNodes;
    ...            for (var i = 0; i < kids.length; i++) {
    ...                var c = kids[i];
    ...                if (c.nodeType === 3) { t += c.textContent + ' '; }
    ...                else if (c.nodeType === 1) {
    ...                    if (c.shadowRoot) { t += deepText(c.shadowRoot, depth + 1); }
    ...                    t += deepText(c, depth + 1);
    ...                }
    ...            }
    ...            return t;
    ...        }
    ...        function squash(s) {
    ...            var out = '';
    ...            var prevWasSpace = false;
    ...            for (var i = 0; i < s.length; i++) {
    ...                var code = s.charCodeAt(i);
    ...                var isSpace = (code === 32 || code === 9 || code === 10 || code === 13);
    ...                if (isSpace) {
    ...                    if (!prevWasSpace && out.length > 0) { out += ' '; }
    ...                    prevWasSpace = true;
    ...                } else {
    ...                    out += s.charAt(i);
    ...                    prevWasSpace = false;
    ...                }
    ...            }
    ...            return out;
    ...        }
    ...        var opts = deepAll(document, 'runtime_industries_cfg-option', [], 0);
    ...        var seen = [];
    ...        for (var i = 0; i < opts.length; i++) {
    ...            var root = opts[i].shadowRoot || opts[i];
    ...            var txt = squash(deepText(root, 0));
    ...            seen.push(txt.slice(0, 30));
    ...            if (txt.indexOf(name) === -1) { continue; }
    ...            var cb = deepAll(root, 'input[type="checkbox"]', [], 0)[0];
    ...            if (!cb) { return 'option_has_no_checkbox'; }
    ...            if (cb.checked) { return 'already_selected'; }
    ...            cb.click();
    ...            return cb.checked ? 'selected' : 'click_did_not_take';
    ...        }
    ...        return 'option_not_found:[' + seen.join('|') + ']';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${option_name}
    Log    Select configurator option: ${result}
    IF    "${result}" != "selected" and "${result}" != "already_selected"
        Capture Step Screenshot    configurator_option_retry
        Fail    msg=Could not select configurator option "${option_name}" (${result}) (will retry).
    END

_Commit Configurator
    [Documentation]    Internal keyword — commits the configuration via "Save & Exit".
    ...    ⚠ "Save & Exit" both saves and closes; there is no separate close step.
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function deepAll(root, sel, out, depth) {
    ...            if (depth > 25) return out;
    ...            var els = root.querySelectorAll(sel);
    ...            for (var i = 0; i < els.length; i++) { out.push(els[i]); }
    ...            var all = root.querySelectorAll('*');
    ...            for (var j = 0; j < all.length; j++) {
    ...                if (all[j].shadowRoot) { deepAll(all[j].shadowRoot, sel, out, depth + 1); }
    ...            }
    ...            return out;
    ...        }
    ...        var btns = deepAll(document, 'button', [], 0);
    ...        for (var i = 0; i < btns.length; i++) {
    ...            var b = btns[i];
    ...            if (b.disabled || b.getAttribute('aria-disabled') === 'true') { continue; }
    ...            if ((b.textContent || '').trim() === 'Save & Exit') {
    ...                b.click();
    ...                return 'committed';
    ...            }
    ...        }
    ...        return 'commit_button_not_found';
    ...    })()
    Log    Commit configurator: ${result}
    IF    "${result}" != "committed"
        Capture Step Screenshot    configurator_commit_retry
        Fail    msg=Configurator "Save & Exit" not clickable (${result}) (will retry).
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
    SalesforceAPI.Validate Salesforce Id    ${account_id}
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
    SalesforceAPI.Validate Salesforce Id    ${opportunity_id}
    ${q_id}=    Wait For Related Record Via API
    ...    SELECT Id FROM Quote WHERE OpportunityId = '${opportunity_id}' ORDER BY CreatedDate DESC LIMIT 1
    Dismiss Toast If Present
    Log    Created Quote: ${q_id}
    RETURN    ${q_id}

Add Products Via Browse Catalogs
    [Documentation]    Opens Browse Catalogs on a Quote, selects a catalog, searches for a product,
    ...    adds it, and saves the quote. Handles the Choose Price Book modal if it appears.
    ...
    ...    ⚠ One retry, from a fresh page. Live 2026-10-13, intermittently: the catalog listed no
    ...    products ("Something went wrong when calculating product prices"), or an Add click
    ...    that reported success saved nothing (the card stayed at "View Quote Lines (0)",
    ...    USD 0). The quote is then left SaveFailedOrIncomplete, and a second add onto it fails
    ...    the same way, so the retry first clears it (``_Clear Quote Calculation``), then checks
    ...    the API so a line that saved late isn't added twice, and only then reopens the catalog.
    [Arguments]    ${quote_id}    ${catalog_name}    ${product_name}
    Wait For Quote Calculation    ${quote_id}
    ${added}    ${reason}=    Run Keyword And Ignore Error
    ...    _Add Product Via Browse Catalogs Once    ${quote_id}    ${catalog_name}    ${product_name}
    IF    "${added}" == "FAIL"
        Log    Browse Catalogs didn't save "${product_name}" on ${quote_id} (${reason}); retrying once from a fresh page.    WARN
        _Clear Quote Calculation    ${quote_id}
        ${saved_late}=    _Quote Has Product Line    ${quote_id}    ${product_name}
        IF    not ${saved_late}
            _Add Product Via Browse Catalogs Once    ${quote_id}    ${catalog_name}    ${product_name}
        END
    END
    Capture Step Screenshot    products_added
    Sleep    5s    reason=Allow pricing to process

_Add Product Via Browse Catalogs Once
    [Documentation]    Internal keyword — one pass of Add Products Via Browse Catalogs: open the
    ...    catalog, search, add, save, and wait for the saved line.
    [Arguments]    ${quote_id}    ${catalog_name}    ${product_name}
    Navigate To Quote    ${quote_id}
    Click Browse Catalogs
    Select Catalog By Name    ${catalog_name}
    Search Product In Catalog    ${product_name}
    Add Product By Name    ${product_name}
    Sleep    2s    reason=Allow product addition to register
    Click Save Quote In Catalog    ${quote_id}    ${product_name}

_Quote Has Product Line
    [Documentation]    Internal keyword — True if ${quote_id} has a line for ${product_name}.
    [Arguments]    ${quote_id}    ${product_name}
    SalesforceAPI.Validate Salesforce Id    ${quote_id}
    ${product_id}=    SalesforceAPI.Find Product By Name    ${product_name}
    SalesforceAPI.Validate Salesforce Id    ${product_id}
    ${rows}=    SalesforceAPI.Query Records
    ...    SELECT Id FROM QuoteLineItem WHERE QuoteId = '${quote_id}' AND Product2Id = '${product_id}' LIMIT 1
    ${found}=    Evaluate    len($rows) > 0
    RETURN    ${found}

Create Order From Quote
    [Documentation]    Creates a single Order from a Quote via the Create Order flow.
    ...    Selects "Create Single Order" and advances through the flow.
    ...    Returns the new Order Id found via API.
    ...
    ...    ⚠ Retried once when no Order appears. Live 2026-10-13 on 264.8.101, intermittently:
    ...    createOrdersFromQuote gacked ("An error occurred... error ID: 343818103-482580",
    ...    IndexOutOfBoundsException in AdvancedQuoteToOrderHeaderCreationUtil) and created nothing.
    ...    The single-order method creates the order synchronously inside the flow, so 45s with no
    ...    Order on the quote means the attempt failed; only then is the flow run again.
    [Arguments]    ${quote_id}
    SalesforceAPI.Validate Salesforce Id    ${quote_id}
    Wait For Quote Calculation    ${quote_id}    require_priced=${True}
    # An Order already on the quote (a QUOTE_ID reused from an earlier run) must not count as
    # this attempt's, or a failed attempt would go unnoticed and the old Order be returned.
    ${earlier}=    SalesforceAPI.Query Records
    ...    SELECT CreatedDate FROM Order WHERE QuoteId = '${quote_id}' ORDER BY CreatedDate DESC LIMIT 1
    ${newer_than}=    Set Variable    ${EMPTY}
    IF    $earlier
        ${since}=    Evaluate    $earlier[0]['CreatedDate'][:19] + 'Z'
        Should Match Regexp    ${since}    ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$
        ...    msg=Quote ${quote_id}'s earlier Order has no usable CreatedDate: ${earlier}
        ${newer_than}=    Set Variable    ${SPACE}AND CreatedDate > ${since}
    END
    ${order_soql}=    Set Variable
    ...    SELECT Id FROM Order WHERE QuoteId = '${quote_id}'${newer_than} ORDER BY CreatedDate DESC LIMIT 1
    ${flow}    ${reason}=    Run Keyword And Ignore Error    _Run Create Order Flow    ${quote_id}
    ${created}=    Run Keyword And Return Status
    ...    Wait For Related Record Via API    ${order_soql}    timeout=45s    interval=3s
    IF    not ${created}
        Capture Step Screenshot    create_order_failed_retrying
        Log    Create Order on ${quote_id} produced no Order (flow: ${flow} ${reason}); retrying once.    WARN
        _Run Create Order Flow    ${quote_id}
    END
    ${order_id}=    Wait For Related Record Via API    ${order_soql}
    Log    Created Order: ${order_id}
    RETURN    ${order_id}

_Run Create Order Flow
    [Documentation]    Internal keyword — runs the Quote's Create Order flow with "Create Single Order".
    [Arguments]    ${quote_id}
    Navigate To Quote    ${quote_id}
    Click Highlights Panel Action    Create Order
    Sleep    5s    reason=Allow CreateOrder flow to initialize
    Select Order Creation Method
    Advance Through Flow Screens
    Dismiss Toast If Present

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

Wait For Quote Calculation
    [Documentation]    Waits until ${quote_id}'s CalculationStatus has settled, failing at once on a
    ...    failed status. With ``require_priced``, settled means a @{QUOTE_CALC_PRICED} value,
    ...    which is what Create Order and Create Contract need.
    ...
    ...    ⚠ RLM_CreateOrdersFromQuote no longer gates on this (#353 removed the gate, whose
    ...    `Completed` value is no longer on the picklist), so a test that starts Create Order while
    ...    the quote is still pricing gets "We couldn't create an order for this quote because the
    ...    calculation status of the quote is invalid". The flow then never closes (it looks stuck)
    ...    and no order, assets or renewal follow. Live 2026-10-13, from the flow error emails. Fixed
    ...    sleeps after configuring the bundle aren't enough when pricing runs long.
    ...
    ...    ⚠ The platform intermittently leaves a quote failed for no reason in the test's control
    ...    (SaveFailedOrIncomplete after a configurator save, TaxCalculationFailed after a catalog
    ...    add; PricingApiExecution rows show Failure with no detail). Live 2026-10-13 on a fresh
    ...    264 build: in about a third of runs, with or without the approval-flags overlay. A fresh
    ...    reprice clears it, so a failed status gets ONE reprice (Place Sales Transaction,
    ...    pricingPref Force) and a second wait. It's logged as a WARN so the rate stays visible;
    ...    a second failure fails the test.
    ...    With ``require_priced``, CompletedWithoutPricing counts as failed too: the next step
    ...    needs prices.
    ...
    ...    The recovery reprice is synchronous: Place Sales Transaction returned with the quote
    ...    already repriced in every one of ~500 probe calls (2026-10-13), so the status read right
    ...    after it is the new one. ``reprice=${False}`` turns the recovery off, for callers that
    ...    just repriced.
    [Arguments]    ${quote_id}    ${require_priced}=${False}    ${timeout}=180s    ${reprice}=${True}
    SalesforceAPI.Validate Salesforce Id    ${quote_id}
    ${status}=    Wait Until Keyword Succeeds    ${timeout}    5s
    ...    _Quote Calculation Settled    ${quote_id}    ${require_priced}
    ${failed}=    _Is Failed Calculation Status    ${status}    ${require_priced}
    IF    ${failed} and ${reprice}
        Log    Quote ${quote_id} calculation ended ${status}; repricing once.    WARN
        Capture Step Screenshot    quote_calculation_failed_repricing
        SalesforceAPI.Reprice Quote Via API    ${quote_id}
        ${status}=    Wait Until Keyword Succeeds    ${timeout}    5s
        ...    _Quote Calculation Settled    ${quote_id}    ${require_priced}
        ${failed}=    _Is Failed Calculation Status    ${status}    ${require_priced}
    END
    IF    ${failed}
        Capture Step Screenshot    quote_calculation_failed
        Fail    msg=Quote ${quote_id} calculation failed, also after a reprice: CalculationStatus=${status}.
    END
    RETURN    ${status}

_Quote Calculation Settled
    [Documentation]    Internal keyword — returns CalculationStatus once it's settled (or failed), and
    ...    fails, so the caller retries, while it's queued or in progress. Under ``require_priced``
    ...    a settled but unpriced status is returned as failed (CompletedWithoutPricing) or
    ...    retried (NotStarted, ImportQLISuccess), since pricing may not have started yet.
    [Arguments]    ${quote_id}    ${require_priced}
    ${quote}=    SalesforceAPI.Query Record By Id    Quote    ${quote_id}    fields=CalculationStatus
    ${status}=    Evaluate    $quote['CalculationStatus'] or 'NotStarted'
    Log    Quote ${quote_id} CalculationStatus: ${status}
    ${failed}=    _Is Failed Calculation Status    ${status}    ${require_priced}
    IF    ${failed}
        RETURN    ${status}
    END
    ${busy}=    Evaluate    'Queued' in $status or $status.endswith('InProgress') or $status.endswith('InProcess') or $status in ('Saving', 'TaxCalculationWaiting')
    IF    ${busy}
        Fail    msg=Quote ${quote_id} is still calculating (${status}) (will retry).
    END
    IF    ${require_priced} and $status not in $QUOTE_CALC_PRICED
        Fail    msg=Quote ${quote_id} isn't priced yet (${status}) (will retry).
    END
    RETURN    ${status}

_Clear Quote Calculation
    [Documentation]    Internal keyword — reprices ${quote_id} (Place Sales Transaction, pricingPref
    ...    Force) and waits for it to settle, so a step retried after a platform failure starts
    ...    from a freshly calculated quote rather than one left SaveFailedOrIncomplete or with a
    ...    broken context.
    ...    It doesn't fail the step: a reprice that errors, or a quote that stays failed, is logged
    ...    as a WARN and the retry goes ahead, so the step's own failure is what gets reported.
    [Arguments]    ${quote_id}
    ${repriced}    ${detail}=    Run Keyword And Ignore Error    SalesforceAPI.Reprice Quote Via API    ${quote_id}
    IF    "${repriced}" == "FAIL"
        Log    Repricing ${quote_id} before the retry failed: ${detail}    WARN
        RETURN
    END
    ${cleared}    ${detail}=    Run Keyword And Ignore Error
    ...    Wait For Quote Calculation    ${quote_id}    reprice=${False}
    IF    "${cleared}" == "FAIL"
        Log    Quote ${quote_id} didn't recover before the retry: ${detail}    WARN
    END

_Is Failed Calculation Status
    [Documentation]    Internal keyword — True for a failed CalculationStatus: any ``*Failed`` value, a
    ...    @{QUOTE_CALC_FAILED} value, or, under ``require_priced``, CompletedWithoutPricing.
    [Arguments]    ${status}    ${require_priced}
    ${failed}=    Evaluate    $status.endswith('Failed') or $status in $QUOTE_CALC_FAILED or ($require_priced and $status == 'CompletedWithoutPricing')
    RETURN    ${failed}

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

Create Contract From Quote
    [Documentation]    Creates a Contract from ${quote_id} the way a rep does: the Quote's
    ...    ``New Contract`` action, which Revenue Settings routes to the
    ...    ``RLM_CreateContractFromQuote`` flow. Checks the renewal term the flow set,
    ...    activates the Contract and returns its Id. The Order created from the Quote
    ...    afterwards picks the Contract up and links its Assets to it
    ...    (AssetContractRelationship).
    ...
    ...    The flow is what makes contract-first renewals work. The standard
    ...    ``createContract`` action on its own leaves ``RenewalTerm2`` / ``RenewalTermUnit``
    ...    blank, so the Assets get no renewal term, ``getRenewableAssetsSummary`` fails ("All
    ...    assets in a request must have values for RenewalTermUnit and RenewalTerm") and no
    ...    renewal Opportunity is created (live-checked on 264). So this keyword must not set
    ...    the renewal term itself: that would hide a regression in the flow. Setting
    ...    ``Order.ContractId`` directly is not a substitute either: it creates no
    ...    AssetContractRelationship rows and fails the same way.
    ...
    ...    ⚠ Retried once, but only when the flow says so. Live 2026-10-13, intermittently, on a
    ...    priced quote: "The contract could not be created. Your contract couldn't be created. Ask
    ...    your Salesforce admin to turn on context definitions and ensure they're mapped to
    ...    contracts." and no Contract. The same quote succeeds on a second try. The retry runs
    ...    only when that message is on screen, so a contract that's merely slow to appear is
    ...    never created twice.
    [Arguments]    ${quote_id}
    SalesforceAPI.Validate Salesforce Id    ${quote_id}
    Wait For Quote Calculation    ${quote_id}    require_priced=${True}
    ${contract_soql}=    Set Variable
    ...    SELECT Id FROM Contract WHERE SourceQuoteId = '${quote_id}' ORDER BY CreatedDate DESC LIMIT 1
    _Submit New Contract Flow    ${quote_id}
    ${created}=    Run Keyword And Return Status
    ...    Wait For Related Record Via API    ${contract_soql}    timeout=45s    interval=3s
    IF    not ${created}
        ${flow_failed}=    _Page Shows Text    The contract could not be created
        IF    ${flow_failed}
            Log    New Contract on ${quote_id} failed in the flow; retrying once.    WARN
            _Submit New Contract Flow    ${quote_id}
        END
    END
    ${contract_id}=    Wait For Related Record Via API    ${contract_soql}
    # The test bundle is a 12-month Annual subscription: 12 months, renewed as 1 Annual term.
    SalesforceAPI.Verify Field Value Via API    Contract    ${contract_id}    ContractTerm    12
    ${renewal_term}=    SalesforceAPI.Query Field Value    Contract    ${contract_id}    RenewalTerm2
    Should Be Equal As Numbers    ${renewal_term}    1
    ...    msg=Contract ${contract_id} RenewalTerm2 is ${renewal_term}, expected 1
    SalesforceAPI.Verify Field Value Via API    Contract    ${contract_id}    RenewalTermUnit    Annual
    ${result}=    Run Process    sf    data    update    record    -o    ${ORG_ALIAS}
    ...    --sobject    Contract    --record-id    ${contract_id}
    ...    --values    Status\=Activated    --json    shell=False
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Could not activate Contract ${contract_id}: ${result.stdout}
    Log    Created and activated Contract ${contract_id} from Quote ${quote_id}
    RETURN    ${contract_id}

_Submit New Contract Flow
    [Documentation]    Internal keyword — runs the Quote's ``New Contract`` action and clicks the
    ...    flow's Create button.
    [Arguments]    ${quote_id}
    Navigate To Quote    ${quote_id}
    Click Highlights Panel Action    New Contract
    Sleep    5s    reason=Allow RLM_CreateContractFromQuote flow to initialize
    Wait Until Keyword Succeeds    30s    3s    _Click Flow Navigation Button    Create
    Capture Step Screenshot    contract_flow_submitted

_Page Shows Text
    [Documentation]    Internal keyword — True if ${text} appears anywhere on the page, including
    ...    inside shadow roots (``Page Should Contain`` doesn't look there, and flow screens
    ...    render inside them).
    [Arguments]    ${text}
    ${found}=    Execute JavaScript
    ...    return (function(text){
    ...        function walk(root, depth) {
    ...            if (depth > 30) return false;
    ...            if ((root.textContent || '').indexOf(text) >= 0) return true;
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].shadowRoot && walk(all[i].shadowRoot, depth + 1)) return true;
    ...            }
    ...            return false;
    ...        }
    ...        return walk(document.documentElement, 0);
    ...    })(arguments[0])
    ...    ARGUMENTS    ${text}
    RETURN    ${found}

_Click Flow Navigation Button
    [Documentation]    Internal keyword. Clicks the button labelled ${label} inside the
    ...    running screen flow, searching through shadow roots. ``Advance Through Flow Screens`` only
    ...    knows the generic labels (Next, Finish, ...), not a flow's custom one such as Create.
    [Arguments]    ${label}
    ${result}=    Execute JavaScript
    ...    return (function(label){
    ...        function find(root){
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === 'BUTTON' && all[i].textContent.trim() === label) {
    ...                    all[i].click(); return 'clicked';
    ...                }
    ...                if (all[i].shadowRoot) { var r = find(all[i].shadowRoot); if (r) return r; }
    ...            }
    ...            return null;
    ...        }
    ...        var flow = document.querySelector('flowruntime-flow');
    ...        return find(flow ? (flow.shadowRoot || flow) : document) || 'not found';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${label}
    Should Be Equal    ${result}    clicked    msg=Flow button "${label}" not found
    Sleep    3s    reason=Allow flow to process

Wait For Assets From Order
    [Documentation]    Waits for ${order_id}'s activation to produce Assets.
    ...
    ...    ⚠ Assetization is asynchronous and, intermittently, never starts. Live 2026-10-13: an
    ...    order activated at 20:04Z produced no AssetizationAsyncJob tracker at all in 3 minutes,
    ...    while every other activation that day produced assets within 2 seconds. So after
    ...    ${first_wait} with no assets, assetization is requested once directly (the documented
    ...    ``createOrUpdateAssetFromOrder`` invocable action), with a WARN, and the wait continues.
    ...    The action needs the Assetize Order permission set, which builds grant through the
    ...    RLM_PSL permission set group; if the run user lacks it, the refusal is logged and the
    ...    wait simply continues.
    ...    The check is scoped to ${order_id} (assets whose AssetActionSource points at its order
    ...    products), so assets left by an earlier run can't satisfy it.
    [Arguments]    ${order_id}    ${first_wait}=90s
    SalesforceAPI.Validate Salesforce Id    ${order_id}
    # Run the query once outside the retry, so a query the org rejects fails here at once
    # instead of being polled as "no assets yet" and triggering a direct assetization.
    ${soql}=    _Order Asset Source Soql    ${order_id}
    SalesforceAPI.Query Records    ${soql}
    ${found}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    ${first_wait}    ${ASYNC_POLL_INTERVAL}
    ...    SalesforceAPI.Verify Related Record Exists    ${soql}
    IF    not ${found}
        Log    No assets ${first_wait} after activating ${order_id}; requesting assetization directly.    WARN
        ${requested}    ${detail}=    Run Keyword And Ignore Error    SalesforceAPI.Assetize Order Via API    ${order_id}
        IF    "${requested}" == "FAIL"
            Log    Direct assetization was refused (needs Assetize Order, granted via RLM_PSL): ${detail}    WARN
        END
        Wait Until Keyword Succeeds    ${ASYNC_TIMEOUT}    ${ASYNC_POLL_INTERVAL}
        ...    SalesforceAPI.Verify Related Record Exists    ${soql}
    END

_Order Asset Source Soql
    [Documentation]    Internal keyword — SOQL for an asset action whose source is one of
    ...    ${order_id}'s order products (validated by the caller).
    [Arguments]    ${order_id}
    RETURN    SELECT Id FROM AssetActionSource WHERE ReferenceEntityItemId IN (SELECT Id FROM OrderItem WHERE OrderId = '${order_id}') LIMIT 1

Verify Renewal Opportunity Includes Product
    [Documentation]    Asserts the renewal Opportunity produced on order activation carries a
    ...    line for ${product_name}. Polls, because the flow is asynchronous.
    ...
    ...    ⚠ THIS is the assertion that detects issue #63 — the Order status does NOT.
    ...    The renewal is created by `RLM_CreateUpdateRenewalOpportunities`, whose TriggerType is
    ...    **PlatformEvent**. When it fails, the Order still reaches Activated, no error toast
    ...    appears, and no AsyncApexJob is marked Failed — the only observable is that the flow's
    ...    output never arrives. A test that stops at "Order is Activated" therefore PASSES while
    ...    #63 is live, which is precisely how #63 survived.
    ...
    ...    Live evidence 2026-07-28: activation at 20:07:54 produced 6 assets at 20:07:57 and the
    ...    renewal Opportunity at 20:08:00 with 5 lines including Software Maintenance @ 5400.
    ...    The preceding run, whose order had no maintenance line, produced 4 (28,500 vs 33,900 —
    ...    a difference of exactly 5,400).
    ...
    ...    Scoped to `Opportunity.Type = 'Existing Business'` — the `RenewalOpportunityType`
    ...    constant `RLM_CreateUpdateRenewalOpportunities` sets on the Opportunity it creates (its
    ...    Name comes from a formula of account name and end date, so it isn't a fixed value to
    ...    match) — and to Opportunities other than ${source_opportunity_id}, the one the Quote
    ...    was created from. Without this, the query would also match an OpportunityLineItem
    ...    synced onto the SOURCE Opportunity from the Quote (standard Quote-Opportunity line
    ...    sync), which would pass this assertion even if the renewal flow never fired —
    ...    defeating the point of the check.
    ...
    ...    ⚠ Reset Test Account does NOT remove earlier renewal Opportunities. Live 2026-10-13: the
    ...    contract-first test's renewal (ContractId set) survived the next run's reset, and the
    ...    next no-contract test matched it before its own flow had fired, failing on
    ...    ContractId 800… != None. So the query also requires the renewal Opportunity to have been
    ...    created at or after ${order_id}'s ActivatedDate (server time, so local clock skew can't
    ...    matter): only the renewal this activation produced can satisfy it.
    ...
    ...    Then checks the fields the flow copies onto the Opportunity it creates: ContractId and
    ...    CurrencyIsoCode must equal ${order_id}'s (in the no-contract test both ContractIds are
    ...    blank; ``Quote To Order With Contract`` gives the order a real one), and the Name must
    ...    contain ` - Renewal - `, the OpportunityName constant as RenewalOpportunityNameFormula
    ...    places it.
    [Arguments]    ${account_id}    ${product_name}    ${source_opportunity_id}    ${order_id}
    SalesforceAPI.Validate Salesforce Id    ${account_id}
    SalesforceAPI.Validate Salesforce Id    ${source_opportunity_id}
    SalesforceAPI.Validate Salesforce Id    ${order_id}
    ${product_id}=    SalesforceAPI.Find Product By Name    ${product_name}
    SalesforceAPI.Validate Salesforce Id    ${product_id}
    ${activated}=    SalesforceAPI.Query Record By Id    Order    ${order_id}    fields=ActivatedDate
    Should Be True    $activated['ActivatedDate']
    ...    msg=Order ${order_id} has no ActivatedDate, so its renewal can't be told apart from an earlier one.
    ${since}=    Evaluate    $activated['ActivatedDate'][:19] + 'Z'
    Should Match Regexp    ${since}    ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$
    ...    msg=Order ${order_id} ActivatedDate isn't a timestamp: ${activated}[ActivatedDate]
    ${line_id}=    Wait For Related Record Via API
    ...    SELECT Id FROM OpportunityLineItem WHERE Opportunity.AccountId = '${account_id}' AND Opportunity.Type = 'Existing Business' AND OpportunityId != '${source_opportunity_id}' AND Opportunity.CreatedDate >= ${since} AND Product2Id = '${product_id}' ORDER BY CreatedDate DESC LIMIT 1
    Log    Renewal opportunity line for ${product_name}: ${line_id}
    ${line}=    SalesforceAPI.Query Record By Id    OpportunityLineItem    ${line_id}    fields=OpportunityId
    ${renewal}=    SalesforceAPI.Query Record By Id    Opportunity    ${line}[OpportunityId]
    ...    fields=Name,ContractId,CurrencyIsoCode
    ${order}=    SalesforceAPI.Query Record By Id    Order    ${order_id}    fields=ContractId,CurrencyIsoCode
    Log    Renewal opportunity ${line}[OpportunityId]: ${renewal}[Name], contract ${renewal}[ContractId], currency ${renewal}[CurrencyIsoCode]
    Should Be Equal    ${renewal}[ContractId]    ${order}[ContractId]
    ...    msg=Renewal Opportunity.ContractId should be the order's ContractId.
    Should Be Equal    ${renewal}[CurrencyIsoCode]    ${order}[CurrencyIsoCode]
    ...    msg=Renewal Opportunity.CurrencyIsoCode should be the order's CurrencyIsoCode.
    Should Contain    ${renewal}[Name]    ${SPACE}- Renewal -${SPACE}
    ...    msg=Renewal Opportunity.Name should come from RenewalOpportunityNameFormula.
    RETURN    ${line_id}
