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
# Shared shadow-DOM traversal helper prepended to Execute JavaScript blocks that need findEl.
${_JS_FIND_EL}    function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }

*** Test Cases ***
Configure Product Discovery Default Catalog
    [Documentation]    Navigates to Product Discovery Settings and sets the Default Catalog
    ...    to the value specified by ${DEFAULT_CATALOG}. Skips if the catalog is already set
    ...    to the correct value. Reloads the page after setting to confirm server-side persistence.
    Open Product Discovery Settings Page
    Set Default Catalog    ${DEFAULT_CATALOG}
    Dismiss Toast If Present
    Capture Page Screenshot
    # Reload and re-verify to confirm the value was saved server-side.
    # Open Setup Page sleeps 2s for generic Lightning rendering, but the
    # Product Discovery Settings LWC + its [data-id="selectedCatalog"]
    # pill take longer than that to wire on the post-reload visit. Without
    # a retry the read returns 'not_set' even when the catalog is genuinely
    # persisted server-side. Wait Until Keyword Succeeds polls
    # _Read Default Catalog State (which treats 'not_set' as a retry signal)
    # until the pill renders.
    Open Product Discovery Settings Page
    ${verified}=    Wait Until Keyword Succeeds    30s    2s    _Read Default Catalog State
    Should Be Equal    ${verified}    ${DEFAULT_CATALOG}
    ...    msg=Default Catalog not persisted after page reload: expected "${DEFAULT_CATALOG}", got "${verified}"
    Log    Product Discovery Settings: Default Catalog confirmed as "${DEFAULT_CATALOG}" after reload.

*** Keywords ***
Open Product Discovery Settings Page
    [Documentation]    Opens the Product Discovery Settings setup page using sf org open
    ...    when ORG_ALIAS is set, or falls back to PRODUCT_DISCOVERY_URL.
    ${path}=    Set Variable    /lightning/setup/ProductDiscoverySettings/home
    IF    """${ORG_ALIAS}""" != ""
        Open Setup Page    ${path}
    ELSE IF    """${PRODUCT_DISCOVERY_URL}""" != ""
        Open Setup Page    url=${PRODUCT_DISCOVERY_URL}
    ELSE
        Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or PRODUCT_DISCOVERY_URL
    END

Set Default Catalog
    [Documentation]    Sets the "Select Default Catalog" combobox via JavaScript, piercing the
    ...    nested LWC shadow DOMs (lightning-combobox → lightning-base-combobox → button, with
    ...    option text read from lightning-base-combobox-item shadow roots). Clears any existing
    ...    selection first if a different catalog is already selected. Auto-saves on selection.
    ...
    ...    Wraps the entire open+select cycle in Wait Until Keyword Succeeds so that
    ...    transient mid-render LWC states retry the whole sequence — not just the
    ...    state check. The previous structure failed terminally on `not_found:[]`
    ...    (combobox opened but options hadn't loaded yet because the LWC's parent
    ...    was still server-fetching). Each retry now closes any open dropdown
    ...    (Escape) before re-checking state, so the second pass either sees the
    ...    pill (already_set) or gets a freshly-clicked combobox with populated
    ...    options.
    [Arguments]    ${target_value}
    Wait Until Keyword Succeeds    90s    5s    _Try Set Default Catalog    ${target_value}

_Try Set Default Catalog
    [Documentation]    One attempt at configuring the Default Catalog. Returns
    ...    normally on success or already_set; fails (triggering the outer
    ...    Wait Until Keyword Succeeds retry) on any transient mid-render state.
    ...    Closes any open dropdown with Escape before the outer retry re-invokes
    ...    so the next attempt starts from a clean state.
    [Arguments]    ${target_value}
    # Step 1: check current state; clear wrong selection; open dropdown
    ${open_result}=    _Open Default Catalog Combobox    ${target_value}
    IF    "${open_result}" == "already_set"
        Log    Default Catalog already set to "${target_value}". No change needed.
        RETURN
    END
    # If a selection was cleared, give the pill-removal re-render a beat then re-open
    IF    "${open_result}" == "cleared"
        Sleep    2s    reason=Allow pill removal to settle before re-opening
        ${open_result}=    _Open Default Catalog Dropdown
    END
    Should Be Equal    ${open_result}    opened
    ...    msg=Could not prepare/open Default Catalog combobox: ${open_result}
    Sleep    1s    reason=Allow dropdown options to populate
    # Step 2: click the matching option (text is inside each option's shadow root)
    ${select_result}=    Execute JavaScript
    ...    return (function(targetValue) {
    ...        function findAll(root, sel, d, acc) {
    ...            if (d > 6) return;
    ...            root.querySelectorAll(sel).forEach(function(el){acc.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,sel,d+1,acc);});
    ...        }
    ...        var opts = []; findAll(document, '[role="option"]', 0, opts);
    ...        for (var i=0;i<opts.length;i++) {
    ...            var text = opts[i].shadowRoot ? opts[i].shadowRoot.textContent.trim() : '';
    ...            if (text === targetValue) { opts[i].click(); return 'clicked'; }
    ...        }
    ...        return 'not_found:[' + opts.map(function(o){return o.shadowRoot?o.shadowRoot.textContent.trim():'?';}).join(',') + ']';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${target_value}
    IF    "${select_result}" == "clicked"
        Sleep    2s    reason=Allow selection to auto-save
        Log    Default Catalog set to "${target_value}".
        RETURN
    END
    # Empty / unmatched dropdown — close it (Esc) and let the outer retry try again.
    # Most commonly empty: LWC parent's options-fetch hasn't completed yet, so the
    # opened dropdown rendered zero options. By the next retry the parent should
    # have either fully loaded (giving us a populated dropdown OR already_set pill).
    _Close Default Catalog Dropdown
    Fail    msg=Default Catalog dropdown returned "${select_result}"; closing and retrying open+select cycle...

_Close Default Catalog Dropdown
    [Documentation]    Dispatches Escape on document.body to close any open
    ...    lightning-combobox dropdown. Used between retry attempts in
    ...    _Try Set Default Catalog so a stale-open dropdown doesn't interfere
    ...    with the next state check.
    Execute JavaScript
    ...    document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true}));
    Sleep    0.5s    reason=Allow dropdown close animation to complete

_Read Default Catalog State
    [Documentation]    Reads the current selected catalog text from [data-id="selectedCatalog"]
    ...    after a Product Discovery Settings reload. Returns the catalog name when the pill
    ...    has rendered, or fails with 'not_set' to drive Wait Until Keyword Succeeds retry —
    ...    the LWC routinely takes longer than Open Setup Page's 2s default sleep to wire on
    ...    the post-reload visit. Caller asserts the final state.
    ${state}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return findEl(document, '[data-id="selectedCatalog"]', 0)?.textContent.trim() || 'not_set'
    Should Not Be Equal    ${state}    not_set
    ...    msg=Default Catalog pill not yet rendered post-reload; retrying...
    RETURN    ${state}

_Open Default Catalog Dropdown
    [Documentation]    Re-opens the Default Catalog combobox after a pill clear. Used by
    ...    Set Default Catalog when the cleared-path needs to wait for the LWC to re-render
    ...    the combobox button (pill removal is asynchronous and can take longer than the
    ...    fixed sleep). Returns 'page_not_ready' for any transient render miss
    ...    (combobox / lightning-base-combobox / button not yet present) so
    ...    Wait Until Keyword Succeeds retries until the re-render settles —
    ...    canonical pattern matching configure_core_pricing_setup.robot.
    ${result}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return (function() {
    ...        var lc = findEl(document, 'lightning-combobox[data-id="defaultCatalog"]', 0);
    ...        if (!lc) return 'page_not_ready';
    ...        var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
    ...        if (!lbc) return 'page_not_ready';
    ...        var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
    ...        if (!btn) return 'page_not_ready';
    ...        btn.click();
    ...        return 'opened';
    ...    })()
    Should Be Equal    ${result}    opened
    ...    msg=Default Catalog combobox not yet re-rendered after clear; retrying... (got: ${result})
    RETURN    ${result}

_Open Default Catalog Combobox
    [Documentation]    Runs the state-check JS for Set Default Catalog.
    ...    Returns 'opened' (combobox clicked open), 'already_set' (correct value present),
    ...    'cleared' (wrong pill removed), 'remove_btn_not_found' (terminal — fails caller
    ...    assertion), or 'page_not_ready' (any transient render miss — combobox /
    ...    lightning-base-combobox / button not yet present, OR the LWC has a saved value
    ...    that hasn't been swapped to a pill yet). Salesforce background processing after
    ...    reconfigure_pricing_discovery delays LWC render; Wait Until Keyword Succeeds
    ...    retries on the page_not_ready sentinel — canonical pattern matching
    ...    configure_core_pricing_setup.robot.
    ...
    ...    When the LWC has a saved value (e.g. on a re-run where Default Catalog is already
    ...    set), it briefly renders the empty-state combobox before swapping to the pill.
    ...    The JS used to misinterpret that mid-render window as "no value set" and click
    ...    the (empty) dropdown. We now sniff the lightning-combobox's `value` property
    ...    before deciding: if it's non-empty and the pill hasn't rendered yet, treat as
    ...    page_not_ready so we wait for the pill to land.
    [Arguments]    ${target_value}
    ${result}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return (function(targetValue) {
    ...        var selEl = findEl(document, '[data-id="selectedCatalog"]', 0);
    ...        if (selEl && selEl.textContent.trim() === targetValue) return 'already_set';
    ...        if (selEl) {
    ...            var removeBtn = findEl(document, 'button.slds-pill__remove', 0);
    ...            if (!removeBtn) return 'remove_btn_not_found';
    ...            removeBtn.click();
    ...            return 'cleared';
    ...        }
    ...        var lc = findEl(document, 'lightning-combobox[data-id="defaultCatalog"]', 0);
    ...        if (!lc) return 'page_not_ready';
    ...        if (lc.value) return 'page_not_ready';
    ...        var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
    ...        if (!lbc) return 'page_not_ready';
    ...        var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
    ...        if (!btn) return 'page_not_ready';
    ...        btn.click();
    ...        return 'opened';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${target_value}
    Should Not Be Equal    ${result}    page_not_ready
    ...    msg=Product Discovery combobox or inner shadow elements not yet rendered (or pill is pending render); retrying...
    RETURN    ${result}

Dismiss Toast If Present
    [Documentation]    Clicks the close button on any visible Salesforce toast messages.
    ${close_btns}=    Get WebElements    xpath=//button[contains(@class, 'toastClose') or (@title='Close' and ancestor::*[contains(@class, 'toast')])]
    FOR    ${btn}    IN    @{close_btns}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${btn}
        Run Keyword If    ${visible}    Click Element    ${btn}
    END
    Sleep    0.5s
