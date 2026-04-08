*** Settings ***
Documentation     Configure Salesforce Pricing Setup page (CorePricingSetup): set the default
...               Pricing Procedure. Must run after all data and metadata has been deployed
...               (the Pricing Procedure expression set must be active) and before any
...               automated pricing transactions are tested.
...
...               The "Select a Pricing Procedure" combobox (lightning-combobox.procedure-combobox)
...               is present when no value is set. After selection it is replaced by a pill that
...               persists across reloads — no explicit Save button is needed.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}              ${EMPTY}
${MANUAL_LOGIN_WAIT}      90s
${PRICING_PROCEDURE}      RLM Revenue Management Default Pricing Procedure
# Shared shadow-DOM traversal helper prepended to each Execute JavaScript block.
${_JS_FIND_EL}    function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }

*** Test Cases ***
Configure Core Pricing Setup
    [Documentation]    Navigates to Salesforce Pricing Setup (CorePricingSetup) and sets
    ...    the default Pricing Procedure if it is not already configured. Reloads the page
    ...    after setting to confirm server-side persistence.
    Open Setup Page    /lightning/setup/CorePricingSetup/home
    Set Core Pricing Procedure    ${PRICING_PROCEDURE}
    Capture Page Screenshot
    # Reload and re-verify to confirm the value was saved server-side
    Open Setup Page    /lightning/setup/CorePricingSetup/home
    ${verified}=    Execute JavaScript
    ...    return (function(targetValue) {
    ...        var pills = [];
    ...        (function findAll(root, d) {
    ...            if (d > 6) return;
    ...            root.querySelectorAll('.slds-pill__label').forEach(function(el){pills.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,d+1);});
    ...        })(document, 0);
    ...        for (var i=0; i<pills.length; i++) {
    ...            if (pills[i].textContent.trim() === targetValue) return targetValue;
    ...        }
    ...        return 'not_set';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${PRICING_PROCEDURE}
    Should Be Equal    ${verified}    ${PRICING_PROCEDURE}
    ...    msg=Pricing Procedure not persisted after page reload: expected "${PRICING_PROCEDURE}", got "${verified}"
    Log    CorePricingSetup: Pricing Procedure confirmed as "${PRICING_PROCEDURE}" after reload.

*** Keywords ***
Set Core Pricing Procedure
    [Documentation]    Sets the "Select a Pricing Procedure" combobox on CorePricingSetup
    ...    via JavaScript, piercing nested LWC shadow DOMs
    ...    (lightning-combobox.procedure-combobox > lightning-base-combobox > button, with
    ...    option text read from lightning-base-combobox-item shadow roots).
    ...
    ...    When a value is already set, lightning-combobox is replaced by a pill — this
    ...    keyword detects that state and skips if the pill matches the target value.
    [Arguments]    ${target_value}
    # Retry until LWC components have rendered (page_not_ready causes retry)
    ${open_result}=    Wait Until Keyword Succeeds    20s    3s
    ...    _Open Pricing Procedure Combobox    ${target_value}
    IF    "${open_result}" == "already_set"
        Log    Pricing Procedure already set to "${target_value}". No change needed.
        RETURN
    END
    Should Be Equal    ${open_result}    opened
    ...    msg=Could not open Pricing Procedure combobox: ${open_result}
    Sleep    1s    reason=Allow dropdown options to populate
    # Click the matching option (text is inside each option's shadow root)
    ${select_result}=    Execute JavaScript
    ...    return (function(targetValue) {
    ...        function findAll(root, sel, d, acc) {
    ...            if (d > 6) return;
    ...            root.querySelectorAll(sel).forEach(function(el){acc.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,sel,d+1,acc);});
    ...        }
    ...        var opts = []; findAll(document, '[role="option"]', 0, opts);
    ...        for (var i=0; i<opts.length; i++) {
    ...            var text = opts[i].shadowRoot ? opts[i].shadowRoot.textContent.trim() : opts[i].textContent.trim();
    ...            if (text === targetValue) { opts[i].click(); return 'clicked'; }
    ...        }
    ...        return 'not_found:[' + opts.map(function(o){return o.shadowRoot?o.shadowRoot.textContent.trim():'?';}).join(',') + ']';
    ...    })(arguments[0])
    ...    ARGUMENTS    ${target_value}
    Should Be Equal    ${select_result}    clicked
    ...    msg=Option "${target_value}" not found in dropdown. ${select_result}
    Sleep    2s    reason=Allow selection to auto-save
    Log    Pricing Procedure set to "${target_value}".

_Open Pricing Procedure Combobox
    [Documentation]    Runs the state-check JS for Set Core Pricing Procedure.
    ...    Returns 'opened' (combobox clicked open), 'already_set' (correct pill present),
    ...    or a wrong_value:... string (wrong pill). Fails with page_not_ready when neither
    ...    the combobox nor any pill is found yet — triggering Wait Until Keyword Succeeds.
    [Arguments]    ${target_value}
    ${result}=    Execute JavaScript
    ...    ${_JS_FIND_EL}
    ...    return (function(targetValue) {
    ...        var lc = findEl(document, 'lightning-combobox.procedure-combobox', 0);
    ...        if (lc) {
    ...            var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
    ...            if (!lbc) return 'lbc_not_found';
    ...            var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
    ...            if (!btn) return 'btn_not_found';
    ...            btn.click();
    ...            return 'opened';
    ...        }
    ...        var pills = [];
    ...        (function findAll(root, d) {
    ...            if (d > 6) return;
    ...            root.querySelectorAll('.slds-pill__label').forEach(function(el){pills.push(el);});
    ...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,d+1);});
    ...        })(document, 0);
    ...        for (var i=0; i<pills.length; i++) {
    ...            if (pills[i].textContent.trim() === targetValue) return 'already_set';
    ...        }
    ...        if (pills.length === 0) return 'page_not_ready';
    ...        return 'wrong_value:' + pills.map(function(p){return p.textContent.trim();}).join('|');
    ...    })(arguments[0])
    ...    ARGUMENTS    ${target_value}
    Should Not Be Equal    ${result}    page_not_ready
    ...    msg=Page LWC components not yet rendered; retrying...
    RETURN    ${result}
