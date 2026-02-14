*** Settings ***
Documentation     Enable the Document Builder toggle on Revenue Settings. Required for prepare_docgen (Service Document / Doc Gen) when the org does not have it enabled via metadata. Run after logging into the scratch org in a browser, or ensure REVENUE_SETTINGS_URL is reachable in an authenticated session.
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

*** Test Cases ***
Enable Document Builder Toggle On Revenue Settings
    [Documentation]    Navigate to Revenue Settings and turn on the Document Builder toggle so Doc Gen (prepare_docgen) can deploy. Enables prerequisite (e.g. Revenue Management) first if set.
    Open Revenue Settings Page
    Run Keyword If    """${DOCUMENT_BUILDER_PREREQUISITE_LABEL}""" != ""    Enable Prerequisite Then Document Builder
    Run Keyword If    """${DOCUMENT_BUILDER_PREREQUISITE_LABEL}""" == ""    Enable Toggle By Label    ${DOCUMENT_BUILDER_TOGGLE_LABEL}
    Log    Document Builder toggle enabled. You can now run prepare_docgen.

*** Keywords ***
Enable Prerequisite Then Document Builder
    [Documentation]    Enable the prerequisite toggle (e.g. Revenue Management) so Document Builder becomes enabled, then enable Document Builder.
    Enable Toggle By Label    ${DOCUMENT_BUILDER_PREREQUISITE_LABEL}
    Sleep    2s    reason=Allow Document Builder toggle to become enabled after prerequisite
    Enable Toggle By Label    ${DOCUMENT_BUILDER_TOGGLE_LABEL}
