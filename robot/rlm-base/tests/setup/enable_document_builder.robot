*** Settings ***
Documentation     Enable Document Generation toggles: Document Builder on Revenue Settings, then Design Document Templates in Salesforce and Document Templates Export on General Settings (in that order — Design is a prerequisite for Export). Required for prepare_docgen when the org does not have these enabled via metadata.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
# Set ORG_ALIAS to use sf org open --url-only for authenticated login (recommended). Example: robot -v ORG_ALIAS:my-scratch ...
${ORG_ALIAS}             ${EMPTY}
${REVENUE_SETTINGS_URL}   https://river-playground-9279.scratch.my.salesforce-setup.com/lightning/setup/RevenueSettings/home
${MANUAL_LOGIN_WAIT}      90s
# Set to a label (e.g. Revenue Management) to enable that toggle first; set to ${EMPTY} when prerequisites are already on.
${DOCUMENT_BUILDER_PREREQUISITE_LABEL}    ${EMPTY}
${DOCUMENT_BUILDER_TOGGLE_LABEL}          Document Builder
${GENERAL_SETTINGS_PATH}                  /lightning/setup/GeneralSettings/home
${DOC_TEMPLATES_EXPORT_LABEL}             Document Templates Export
${DESIGN_DOC_TEMPLATES_LABEL}             Design Document Templates in Salesforce

*** Test Cases ***
Enable Document Builder Toggle On Revenue Settings
    [Documentation]    Navigate to Revenue Settings and turn on the Document Builder toggle so Doc Gen (prepare_docgen) can deploy. Enables prerequisite (e.g. Revenue Management) first if set.
    Open Revenue Settings Page
    Run Keyword If    """${DOCUMENT_BUILDER_PREREQUISITE_LABEL}""" != ""    Enable Prerequisite Then Document Builder
    Run Keyword If    """${DOCUMENT_BUILDER_PREREQUISITE_LABEL}""" == ""    Enable Toggle By Label    ${DOCUMENT_BUILDER_TOGGLE_LABEL}
    Log    Document Builder toggle enabled. You can now run prepare_docgen.

Enable Design Document Templates On General Settings
    [Documentation]    Navigate to General Settings (Document Generation) and enable Design Document Templates in Salesforce.
    ...    This must run before Enable Document Templates Export — Salesforce renders the Document Templates Export
    ...    toggle as disabled until Design Document Templates is enabled.
    Open Setup Page    ${GENERAL_SETTINGS_PATH}
    Enable Toggle By Label    ${DESIGN_DOC_TEMPLATES_LABEL}
    Log    Design Document Templates in Salesforce toggle enabled.

Enable Document Templates Export On General Settings
    [Documentation]    Reload General Settings and enable Document Templates Export.
    ...    Requires Design Document Templates to be enabled first (see previous test case).
    ...    The page is reopened so Salesforce reflects the updated prerequisite state before the click.
    ...    Note: this toggle is a plain input[type="checkbox"] (data-name="MetadataPreference") inside
    ...    an LWC shadow root (setup_industries_docgen-preference-toggle). Enable Toggle By Label
    ...    cannot reach it because document.createTreeWalker and querySelectorAll do not pierce
    ...    shadow roots. Instead, we use findEl (recursive shadow-DOM traversal) to click directly —
    ...    the same approach used in configure_core_pricing_setup and configure_product_discovery.
    ...    Sleep 5s ensures the save handler is wired before the click fires. After clicking,
    ...    the page is reloaded to confirm server-side persistence before the suite exits.
    Open Setup Page    ${GENERAL_SETTINGS_PATH}
    Sleep    5s    reason=Allow setup_industries_docgen-preference-toggle LWC to fully wire save handler
    ${click_result}=    Wait Until Keyword Succeeds    20s    3s
    ...    _Click Document Templates Export Toggle
    IF    "${click_result}" == "already_on"
        Log    Document Templates Export already enabled. No change needed.
    ELSE
        Should Be Equal    ${click_result}    clicked
        ...    msg=Document Templates Export could not be clicked (got: ${click_result})
    END
    Sleep    3s    reason=Allow toggle change to reach Salesforce server
    # Reload and re-verify server-side persistence
    Open Setup Page    ${GENERAL_SETTINGS_PATH}
    ${verified}=    Execute JavaScript
    ...    return (function() {
    ...        function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }
    ...        var pi = findEl(document, 'input[data-name="MetadataPreference"]', 0);
    ...        if (!pi) return 'not_found';
    ...        return pi.checked ? 'on' : 'off';
    ...    })()
    Should Be Equal    ${verified}    on
    ...    msg=Document Templates Export toggle not persisted after page reload (got: ${verified})
    Log    Document Templates Export toggle enabled and confirmed.

*** Keywords ***
_Click Document Templates Export Toggle
    [Documentation]    Directly clicks input[data-name="MetadataPreference"] inside
    ...    setup_industries_docgen-preference-toggle's shadow root, bypassing Enable Toggle By Label
    ...    which uses querySelectorAll / createTreeWalker (neither pierce shadow DOM). Returns
    ...    'clicked', 'already_on', or fails with 'not_found' to trigger Wait Until Keyword Succeeds retry.
    ${result}=    Execute JavaScript
    ...    return (function() {
    ...        function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }
    ...        var pi = findEl(document, 'input[data-name="MetadataPreference"]', 0);
    ...        if (!pi) return 'not_found';
    ...        if (pi.checked) return 'already_on';
    ...        pi.click();
    ...        return 'clicked';
    ...    })()
    Should Not Be Equal    ${result}    not_found
    ...    msg=Document Templates Export input[data-name="MetadataPreference"] not yet rendered; retrying...
    RETURN    ${result}

Enable Prerequisite Then Document Builder
    [Documentation]    Enable the prerequisite toggle (e.g. Revenue Management) so Document Builder becomes enabled, then enable Document Builder.
    Enable Toggle By Label    ${DOCUMENT_BUILDER_PREREQUISITE_LABEL}
    Sleep    2s    reason=Allow Document Builder toggle to become enabled after prerequisite
    Enable Toggle By Label    ${DOCUMENT_BUILDER_TOGGLE_LABEL}
