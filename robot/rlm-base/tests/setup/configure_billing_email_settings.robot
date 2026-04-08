*** Settings ***
Documentation     Configure Billing Email Delivery Settings: cycle the "Configure Email
...               Delivery Settings" toggle via the UI to trigger auto-creation of the
...               default invoice email template. The Metadata API toggle cycling in
...               prepare_billing (steps 9→10) sets the boolean but does not trigger the
...               Salesforce backend logic that auto-creates and sets the default email
...               template. A UI toggle cycle (off then on) is required. Must run after
...               deploy_billing_template_settings.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}                  ${EMPTY}
${BILLING_SETTINGS_URL}       ${EMPTY}
${MANUAL_LOGIN_WAIT}          90s

*** Test Cases ***
Configure Billing Email Delivery Settings
    [Documentation]    Navigates to Billing Settings and cycles the "Configure Email
    ...    Delivery Settings" toggle off then on via the UI to trigger the Salesforce
    ...    backend that auto-creates and sets the default invoice email template.
    ...    Skips if the template is already present (idempotent).
    ${template_exists}=    _Check Default Email Template Exists
    IF    "${template_exists}" == "true"
        Log    Default Invoice Email Template already exists. Cycling not needed.
    ELSE
        Open Billing Settings Page
        Capture Page Screenshot
        _Cycle Email Delivery Toggle
        Capture Page Screenshot
        Log    Configure Email Delivery Settings cycled. Default invoice email template should now be created.
    END

*** Keywords ***
Open Billing Settings Page
    [Documentation]    Opens the Billing Settings setup page using sf org open when
    ...    ORG_ALIAS is set, or falls back to BILLING_SETTINGS_URL.
    ${path}=    Set Variable    /lightning/setup/BillingSettings/home
    IF    """${ORG_ALIAS}""" != ""
        Open Setup Page    ${path}
    ELSE IF    """${BILLING_SETTINGS_URL}""" != ""
        Open Setup Page    url=${BILLING_SETTINGS_URL}
    ELSE
        Fail    msg=Set ORG_ALIAS (e.g. -v ORG_ALIAS:my-scratch) or BILLING_SETTINGS_URL
    END

_Check Default Email Template Exists
    [Documentation]    Returns 'true' if the Default Invoice Email Template record
    ...    already exists in the org (idempotency guard). Returns 'false' when
    ...    ORG_ALIAS is not set (browser-only mode — cannot query without sf CLI).
    Run Keyword If    """${ORG_ALIAS}""" == ""    RETURN    false
    ${result}=    Run Process    sf    data    query
    ...    -q    SELECT Id FROM EmailTemplate WHERE Name = 'Default Invoice Email Template' ORDER BY CreatedDate DESC LIMIT 1
    ...    --json    -o    ${ORG_ALIAS}    shell=False
    ${has_record}=    Run Keyword And Return Status    Should Contain    ${result.stdout}    "totalSize": 1
    ${exists}=    Set Variable If    ${has_record}    true    false
    Log    Default Invoice Email Template exists check: ${exists}
    RETURN    ${exists}

_Cycle Email Delivery Toggle
    [Documentation]    Turns "Configure Email Delivery Settings" toggle OFF then ON to
    ...    trigger the Salesforce backend that auto-creates the default invoice email
    ...    template and sets it as the BillingSettings.defaultEmailTemplate. A sleep
    ...    after re-enabling allows async template creation to complete.
    Disable Toggle By Label    Configure Email Delivery Settings
    Sleep    2s    reason=Allow toggle-off state to register before cycling back on
    Enable Toggle By Label    Configure Email Delivery Settings
    Sleep    5s    reason=Allow Salesforce to auto-create the default invoice email template
