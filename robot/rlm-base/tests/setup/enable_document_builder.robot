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
    Open Setup Page    ${GENERAL_SETTINGS_PATH}
    Enable Toggle By Label    ${DOC_TEMPLATES_EXPORT_LABEL}
    Log    Document Templates Export toggle enabled.

*** Keywords ***
Enable Prerequisite Then Document Builder
    [Documentation]    Enable the prerequisite toggle (e.g. Revenue Management) so Document Builder becomes enabled, then enable Document Builder.
    Enable Toggle By Label    ${DOCUMENT_BUILDER_PREREQUISITE_LABEL}
    Sleep    2s    reason=Allow Document Builder toggle to become enabled after prerequisite
    Enable Toggle By Label    ${DOCUMENT_BUILDER_TOGGLE_LABEL}
