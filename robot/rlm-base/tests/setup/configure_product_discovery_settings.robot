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
# Shared shadow-DOM traversal helper prepended to each Execute JavaScript block.
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
    # Reload and re-verify to confirm the value was saved server-side
    Open Product Discovery Settings Page
    ${verified}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return findEl(document, '[data-id="selectedCatalog"]', 0)?.textContent.trim() || 'not_set'
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
    [Arguments]    ${target_value}
    # Step 1: check current state; clear wrong selection; open dropdown
    ${open_result}=    Execute JavaScript
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
    ...        if (!lc) return 'combobox_not_found';
    ...        var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
    ...        if (!lbc) return 'lbc_not_found';
    ...        var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
    ...        if (!btn) return 'btn_not_found';
    ...        btn.click();
    ...        return 'opened';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${target_value}
    IF    "${open_result}" == "already_set"
        Log    Default Catalog already set to "${target_value}". No change needed.
        RETURN
    END
    # If a selection was cleared, wait for the combobox to reappear then re-open it
    IF    "${open_result}" == "cleared"
        Sleep    2s    reason=Allow pill removal to complete and combobox to reappear
        ${open_result}=    Execute JavaScript
        ...    ${_JS_FIND_EL}
        ...    return (function() {
        ...        var lc = findEl(document, 'lightning-combobox[data-id="defaultCatalog"]', 0);
        ...        if (!lc) return 'combobox_not_found';
        ...        var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
        ...        if (!lbc) return 'lbc_not_found';
        ...        var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
        ...        if (!btn) return 'btn_not_found';
        ...        btn.click();
        ...        return 'opened';
        ...    })()
    END
    Should Be Equal    ${open_result}    opened    msg=Could not open Default Catalog combobox: ${open_result}
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
    Should Be Equal    ${select_result}    clicked
    ...    msg=Option "${target_value}" not found in dropdown. ${select_result}
    Sleep    2s    reason=Allow selection to auto-save
    Log    Default Catalog set to "${target_value}".

Dismiss Toast If Present
    [Documentation]    Clicks the close button on any visible Salesforce toast messages.
    ${close_btns}=    Get WebElements    xpath=//button[contains(@class, 'toastClose') or (@title='Close' and ancestor::*[contains(@class, 'toast')])]
    FOR    ${btn}    IN    @{close_btns}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${btn}
        Run Keyword If    ${visible}    Click Element    ${btn}
    END
    Sleep    0.5s
