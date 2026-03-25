*** Settings ***
Documentation     Reorders the App Launcher so that a priority list of apps appears first.
...
...               Background: the Metadata API cannot deploy an AppSwitcher that references
...               managed ConnectedApp or Network entries (present on Trialforce-based scratch
...               orgs). AppMenuItem.SortOrder is also read-only via Tooling API, REST, and Apex.
...
...               This test opens the Lightning home page, clicks the App Launcher waffle icon,
...               opens the full App Launcher modal via "View All", reads all app tile IDs from
...               the shadow DOM, and calls the Salesforce Aura AppLauncherController/saveOrder
...               action directly — no drag required. The Aura CSRF token is read from
...               window.aura.clientService, and the framework UID (fwuid) is read from
...               window.$A.getContext().
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

*** Test Cases ***
Reorder App Launcher
    [Documentation]
    ...    Navigates to the Lightning home page, opens the full App Launcher modal, and
    ...    reorders apps so that PRIORITY_APP_LABELS (comma-separated display labels) appear
    ...    first, in the given order. Remaining apps follow in their current relative order.
    ...    Best-effort: logs a warning and exits without failing if tiles are not found or
    ...    the page structure is unrecognised.
    Set Window Size    1920    1080
    Open Setup Page    ${HOME_PATH}
    Sleep    3s    reason=Allow Lightning to fully initialise
    Open App Launcher Modal
    ${tile_count}=    Wait For App Launcher Tiles
    IF    ${tile_count} == 0
        Log    WARNING: App Launcher tiles not found — skipping reorder.    WARN
        RETURN
    END
    ${result}=    Call Save Order With Priority List    ${PRIORITY_APP_LABELS}
    Log    saveOrder result: ${result}
    IF    "${result}" == "no_tiles"
        Log    WARNING: No tiles found when calling saveOrder — timing issue?    WARN
    ELSE IF    "${result}".startswith("SUCCESS")
        Log    App Launcher reordered: priority order applied successfully.
    ELSE
        Log    WARNING: Unexpected saveOrder result: ${result}    WARN
    END
    Capture Page Screenshot

*** Keywords ***
Open App Launcher Modal
    [Documentation]    Clicks the App Launcher waffle button via JS (handles shadow DOM),
    ...                then clicks "View All" to open the full draggable modal.
    Execute JavaScript
    ...    (function() {
    ...        function traverseShadow(root, selector) {
    ...            var results = [];
    ...            function traverse(node) {
    ...                if (!node) return;
    ...                node.querySelectorAll(selector).forEach(function(el) { results.push(el); });
    ...                node.querySelectorAll('*').forEach(function(el) {
    ...                    if (el.shadowRoot) traverse(el.shadowRoot);
    ...                });
    ...            }
    ...            traverse(root);
    ...            return results;
    ...        }
    ...        var btns = traverseShadow(document, 'button[title="App Launcher"]');
    ...        if (btns.length > 0) { btns[0].click(); return 'clicked'; }
    ...        var btn = document.querySelector('button.slds-context-bar__button');
    ...        if (btn) { btn.click(); return 'clicked_fallback'; }
    ...        return 'not_found';
    ...    })()
    Sleep    2s    reason=Allow compact App Launcher dropdown to open
    Execute JavaScript
    ...    (function() {
    ...        function traverseShadow(root, selector) {
    ...            var results = [];
    ...            function traverse(node) {
    ...                if (!node) return;
    ...                node.querySelectorAll(selector).forEach(function(el) { results.push(el); });
    ...                node.querySelectorAll('*').forEach(function(el) {
    ...                    if (el.shadowRoot) traverse(el.shadowRoot);
    ...                });
    ...            }
    ...            traverse(root);
    ...            return results;
    ...        }
    ...        var links = traverseShadow(document, 'a.slds-button');
    ...        for (var i = 0; i < links.length; i++) {
    ...            if (links[i].textContent.trim() === 'View All') { links[i].click(); return 'view_all_clicked'; }
    ...        }
    ...        var all = traverseShadow(document, 'one-app-launcher-menu');
    ...        if (all.length > 0) { return 'menu_open_no_view_all'; }
    ...        return 'view_all_not_found';
    ...    })()
    Sleep    3s    reason=Allow full App Launcher modal to open and render tiles

Wait For App Launcher Tiles
    [Documentation]    Polls until one-app-launcher-app-tile elements appear in the shadow DOM.
    ...                Returns the tile count (0 if timeout).
    FOR    ${i}    IN RANGE    15
        ${count}=    Execute JavaScript
        ...    return (function() {
        ...        var results = [];
        ...        function traverse(node) {
        ...            if (!node) return;
        ...            node.querySelectorAll('one-app-launcher-app-tile').forEach(function(m) { results.push(m); });
        ...            node.querySelectorAll('*').forEach(function(el) {
        ...                if (el.shadowRoot) traverse(el.shadowRoot);
        ...            });
        ...        }
        ...        traverse(document);
        ...        return results.length;
        ...    })()
        IF    ${count} > 0
            Log    App Launcher tiles loaded: ${count} tiles found.
            RETURN    ${count}
        END
        Sleep    2s
    END
    Log    WARNING: App Launcher tiles not found after 30 seconds.    WARN
    RETURN    ${0}

Call Save Order With Priority List
    [Documentation]    Reads all app tile IDs from the shadow DOM, builds an ordered list
    ...                where PRIORITY_LABELS (comma-separated display labels) come first in
    ...                the given order, followed by all remaining tiles in their current order.
    ...                Then calls the Aura AppLauncherController/saveOrder action synchronously.
    ...                Returns: 'no_tiles', 'SUCCESS:<n> apps ordered', or error string.
    [Arguments]    ${priority_labels}
    ${result}=    Execute JavaScript
    ...    return (function(priorityLabelsStr) {
    ...        var priorityLabels = priorityLabelsStr.split(',').map(function(s) { return s.trim(); }).filter(function(s) { return s.length > 0; });
    ...        function queryShadowAll(root, selector) {
    ...            var results = [];
    ...            function traverse(node) {
    ...                if (!node) return;
    ...                node.querySelectorAll(selector).forEach(function(m) { results.push(m); });
    ...                node.querySelectorAll('*').forEach(function(el) {
    ...                    if (el.shadowRoot) traverse(el.shadowRoot);
    ...                });
    ...            }
    ...            traverse(root);
    ...            return results;
    ...        }
    ...        var tiles = queryShadowAll(document, 'one-app-launcher-app-tile');
    ...        if (tiles.length === 0) return 'no_tiles';
    ...        var tileData = [];
    ...        for (var i = 0; i < tiles.length; i++) {
    ...            var t = tiles[i];
    ...            var name = t.getAttribute('data-name') || '';
    ...            var inner = t.shadowRoot ? t.shadowRoot.querySelector('[draggable="true"]') : null;
    ...            var id = inner ? (inner.getAttribute('data-id') || '') : '';
    ...            tileData.push({name: name, id: id});
    ...        }
    ...        var priorityMap = {};
    ...        for (var p = 0; p < priorityLabels.length; p++) {
    ...            priorityMap[priorityLabels[p]] = p;
    ...        }
    ...        var priorityIds = new Array(priorityLabels.length).fill(null);
    ...        var remainingIds = [];
    ...        for (var j = 0; j < tileData.length; j++) {
    ...            if (!tileData[j].id) continue;
    ...            var idx = priorityMap[tileData[j].name];
    ...            if (idx !== undefined) {
    ...                priorityIds[idx] = tileData[j].id;
    ...            } else {
    ...                remainingIds.push(tileData[j].id);
    ...            }
    ...        }
    ...        var orderedIds = priorityIds.filter(function(id) { return id !== null; }).concat(remainingIds);
    ...        var ids = orderedIds.join(',');
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
    ...                mode: ctx.getMode(),
    ...                app: ctx.getApp(),
    ...                pathPrefix: ctx.getPathPrefix(),
    ...                fwuid: fwuid,
    ...                loaded: ctx.getLoaded()
    ...            });
    ...            var cs = window.aura.clientService;
    ...            var token = cs.Ac;
    ...            if (!token) {
    ...                var csKeys = Object.keys(cs);
    ...                for (var k = 0; k < csKeys.length; k++) {
    ...                    var v = cs[csKeys[k]];
    ...                    if (typeof v === 'string' && v.length > 50 && v.length < 500 && v.indexOf('eyJ') === 0) {
    ...                        token = v; break;
    ...                    }
    ...                }
    ...            }
    ...            if (!token) return 'ERROR:aura_token_not_found';
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
    ...            if (resp.indexOf('"state":"SUCCESS"') >= 0) return 'SUCCESS:' + orderedIds.length + ' apps ordered';
    ...            return 'FAIL:' + resp.substring(0, 300);
    ...        } catch(e) {
    ...            return 'ERROR:' + String(e.message).substring(0, 200);
    ...        }
    ...    })(arguments[0])
    ...    ARGUMENTS    ${priority_labels}
    RETURN    ${result}
