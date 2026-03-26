*** Settings ***
Documentation     Reorders the App Launcher using the Aura AppLauncherController/saveOrder API.
...
...               Background: the Metadata API cannot deploy an AppSwitcher that references
...               managed ConnectedApp or Network entries. AppMenuItem.SortOrder is also
...               read-only via Tooling API, REST, and Apex.
...
...               The Python task (rlm_reorder_app_launcher.py) queries AppMenuItem via the
...               Salesforce REST API (authenticated), computes the priority-ordered
...               ApplicationId list, and passes it here as ORDERED_APP_IDS. This test
...               navigates to the Lightning home page and calls Aura saveOrder directly
...               via synchronous XHR — no modal, no DOM scraping required.
...
...               IMPORTANT: JavaScript blocks must not contain // comments — Robot Framework
...               joins continuation lines with spaces, which causes // to comment out
...               everything that follows on the joined logical line.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}          ${EMPTY}
${HOME_PATH}          /lightning/page/home
${ORDERED_APP_IDS}    ${EMPTY}

*** Test Cases ***
Reorder App Launcher
    [Documentation]
    ...    Navigates to the Lightning home page and calls Aura saveOrder with the
    ...    pre-computed ORDERED_APP_IDS (built by the Python task from SOQL). No modal
    ...    or DOM scraping required.
    Set Window Size    1920    1080
    Open Setup Page    ${HOME_PATH}
    Wait Until Keyword Succeeds    30s    2s    Aura Context Should Be Ready
    ${result}=    Call Save Order    ${ORDERED_APP_IDS}
    Log    saveOrder result: ${result}
    IF    $result.startswith("SUCCESS")
        Log    App Launcher reordered: priority order applied successfully.
    ELSE
        Fail    Unexpected saveOrder result: ${result}
    END

*** Keywords ***
Call Save Order
    [Documentation]    Calls the Aura AppLauncherController/saveOrder action with the
    ...                pre-computed ordered ApplicationId string. Reads the Aura context
    ...                (fwuid, token) from window.$A. Returns 'SUCCESS:<n> apps ordered',
    ...                'ERROR:<msg>', or 'FAIL:<resp>'.
    [Arguments]    ${ordered_ids}
    ${result}=    Execute JavaScript
    ...    return (function(ids) {
    ...        if (!ids || ids.length === 0) { return 'ERROR:no_ids_provided'; }
    ...        try {
    ...            var ctx = window.$A.getContext();
    ...            var fwuid = ctx.Vr;
    ...            if (!fwuid) {
    ...                var scripts = document.querySelectorAll('script');
    ...                for (var s = 0; s < scripts.length; s++) {
    ...                    var m = scripts[s].textContent.match(/"fwuid":"([^"]+)"/);
    ...                    if (m) { fwuid = m[1]; break; }
    ...                }
    ...            }
    ...            var auraContext = JSON.stringify({
    ...                mode: ctx.getMode(), app: ctx.getApp(), pathPrefix: ctx.getPathPrefix(),
    ...                fwuid: fwuid, loaded: ctx.getLoaded()
    ...            });
    ...            var cs = window.aura.clientService;
    ...            var token = (window.$A && typeof window.$A.getToken === 'function') ? window.$A.getToken() : null;
    ...            if (!token) { token = cs.Ac; }
    ...            if (!token) {
    ...                var csKeys = Object.keys(cs);
    ...                for (var k = 0; k < csKeys.length; k++) {
    ...                    var v = cs[csKeys[k]];
    ...                    if (typeof v === 'string' && v.length > 50 && v.length < 500 && v.indexOf('eyJ') === 0) { token = v; break; }
    ...                }
    ...            }
    ...            if (!token) { return 'ERROR:aura_token_not_found'; }
    ...            var idCount = ids.split(',').filter(function(s) { return s.length > 0; }).length;
    ...            var msgObj = {actions: [{id: '1;a', descriptor: 'serviceComponent://ui.global.components.one.appLauncher.AppLauncherController/ACTION$saveOrder', callingDescriptor: 'UNKNOWN', params: {applicationIds: ids}}]};
    ...            var body = 'message=' + encodeURIComponent(JSON.stringify(msgObj)) +
    ...                '&aura.context=' + encodeURIComponent(auraContext) +
    ...                '&aura.pageURI=' + encodeURIComponent(window.location.pathname) +
    ...                '&aura.token=' + encodeURIComponent(token);
    ...            var xhr = new XMLHttpRequest();
    ...            xhr.open('POST', '/aura', false);
    ...            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    ...            xhr.send(body);
    ...            var resp = xhr.responseText || '';
    ...            if (resp.indexOf('"state":"SUCCESS"') >= 0) { return 'SUCCESS:' + idCount + ' apps ordered'; }
    ...            return 'FAIL:' + resp.substring(0, 300);
    ...        } catch(e) {
    ...            return 'ERROR:' + String(e.message).substring(0, 200);
    ...        }
    ...    })(arguments[0])
    ...    ARGUMENTS    ${ordered_ids}
    RETURN    ${result}

Aura Context Should Be Ready
    [Documentation]    Verifies that window.$A is initialised and getContext() is callable.
    ...                Used with Wait Until Keyword Succeeds in place of an unconditional sleep.
    ${ready}=    Execute JavaScript
    ...    return (typeof window.$A !== 'undefined' && window.$A !== null && typeof window.$A.getContext === 'function')
    Should Be True    ${ready}    Aura framework not yet initialised
