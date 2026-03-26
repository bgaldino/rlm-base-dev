*** Settings ***
Documentation     Reorders the App Launcher so that a priority list of apps appears first.
...
...               Background: the Metadata API cannot deploy an AppSwitcher that references
...               managed ConnectedApp or Network entries. AppMenuItem.SortOrder is also
...               read-only via Tooling API, REST, and Apex. The only reliable path is
...               the Aura AppLauncherController/saveOrder API called from browser JS.
...
...               This test navigates to the Lightning home page, queries all AppMenuItem
...               records via the Salesforce REST API (no modal or DOM scraping needed),
...               builds a priority-ordered ID list, and calls Aura saveOrder directly.
...
...               IMPORTANT: JavaScript blocks must not contain // comments — Robot Framework
...               joins continuation lines with spaces, which causes // to comment out
...               everything that follows on the joined logical line.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}              ${EMPTY}
${HOME_PATH}              /lightning/page/home
${PRIORITY_APP_LABELS}    Revenue Cloud
${API_VERSION}            67.0

*** Test Cases ***
Reorder App Launcher
    [Documentation]
    ...    Navigates to the Lightning home page and reorders the App Launcher so that
    ...    PRIORITY_APP_LABELS (comma-separated display labels) appear first, in the given
    ...    order. Remaining apps follow in their current relative order.
    ...    App IDs are fetched via SOQL REST API — no modal or DOM scraping required.
    Set Window Size    1920    1080
    Open Setup Page    ${HOME_PATH}
    Sleep    3s    reason=Allow Lightning to fully initialise
    ${result}=    Call Save Order With Priority List    ${PRIORITY_APP_LABELS}    ${API_VERSION}
    Log    saveOrder result: ${result}
    IF    "${result}".startswith("SUCCESS")
        Log    App Launcher reordered: priority order applied successfully.
    ELSE
        Log    WARNING: Unexpected saveOrder result: ${result}    WARN
    END

*** Keywords ***
Call Save Order With Priority List
    [Documentation]    Fetches all AppMenuItem records via SOQL REST API, builds an ordered
    ...                list where PRIORITY_LABELS (comma-separated display labels) come first
    ...                in the given order, followed by remaining apps in their current order.
    ...                Then calls the Aura AppLauncherController/saveOrder action.
    ...                Returns: 'SUCCESS:<n> apps ordered', 'ERROR:<msg>', or 'FAIL:<resp>'.
    [Arguments]    ${priority_labels}    ${api_version}
    ${result}=    Execute JavaScript
    ...    return (function(priorityLabelsStr, apiVersion) {
    ...        var priorityLabels = priorityLabelsStr.split(',').map(function(s) { return s.trim(); }).filter(function(s) { return s.length > 0; });
    ...        var soql = 'SELECT+ApplicationId,Label,SortOrder+FROM+AppMenuItem+WHERE+IsVisible=true+ORDER+BY+SortOrder';
    ...        var qXhr = new XMLHttpRequest();
    ...        qXhr.open('GET', '/services/data/v' + apiVersion + '/query?q=' + soql, false);
    ...        qXhr.setRequestHeader('Accept', 'application/json');
    ...        qXhr.send();
    ...        if (qXhr.status !== 200) { return 'ERROR:soql status ' + qXhr.status + ' ' + qXhr.responseText.substring(0, 200); }
    ...        var qData;
    ...        try { qData = JSON.parse(qXhr.responseText); } catch(e) { return 'ERROR:parse ' + e.message; }
    ...        var records = qData.records || [];
    ...        if (!records.length) { return 'no_apps_from_soql'; }
    ...        var priorityMap = {};
    ...        for (var p = 0; p < priorityLabels.length; p++) { priorityMap[priorityLabels[p]] = p; }
    ...        var priorityIds = new Array(priorityLabels.length).fill(null);
    ...        var remainingIds = [];
    ...        for (var j = 0; j < records.length; j++) {
    ...            var label = records[j].Label || '';
    ...            var id = records[j].ApplicationId || '';
    ...            if (!id) continue;
    ...            var idx = priorityMap[label];
    ...            if (idx !== undefined) { priorityIds[idx] = id; } else { remainingIds.push(id); }
    ...        }
    ...        var orderedIds = priorityIds.filter(function(id) { return id !== null; }).concat(remainingIds);
    ...        if (!orderedIds.length) { return 'no_ids_found'; }
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
    ...            var token = cs.Ac;
    ...            if (!token) {
    ...                var csKeys = Object.keys(cs);
    ...                for (var k = 0; k < csKeys.length; k++) {
    ...                    var v = cs[csKeys[k]];
    ...                    if (typeof v === 'string' && v.length > 50 && v.length < 500 && v.indexOf('eyJ') === 0) { token = v; break; }
    ...                }
    ...            }
    ...            if (!token) { return 'ERROR:aura_token_not_found'; }
    ...            var ids = orderedIds.join(',');
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
    ...            if (resp.indexOf('"state":"SUCCESS"') >= 0) { return 'SUCCESS:' + orderedIds.length + ' apps ordered'; }
    ...            return 'FAIL:' + resp.substring(0, 300);
    ...        } catch(e) {
    ...            return 'ERROR:' + String(e.message).substring(0, 200);
    ...        }
    ...    })(arguments[0], arguments[1])
    ...    ARGUMENTS    ${priority_labels}    ${api_version}
    RETURN    ${result}
