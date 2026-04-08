*** Settings ***
Documentation     Configure Billing Email Delivery Settings: cycle the "Configure Email
...               Delivery Settings" toggle via the UI to trigger auto-creation of the
...               default invoice email template. The Metadata API toggle cycling in
...               prepare_billing (steps 9→10) sets the boolean but does not trigger the
...               Salesforce backend logic that auto-creates and sets the default email
...               template. A UI toggle cycle (off then on) is required. Must run after
...               deploy_billing_template_settings.
Resource          ../../resources/SetupToggles.robot
Suite Setup       _Open Headed Browser For Billing
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
    ...    The Disable/Enable keywords check current toggle state before clicking,
    ...    so re-running is safe (the backend template creation is idempotent).
    Open Billing Settings Page
    Capture Page Screenshot
    _Cycle Email Delivery Toggle
    Capture Page Screenshot
    Log    Configure Email Delivery Settings cycled. Default invoice email template should now be created.

*** Keywords ***
_Open Headed Browser For Billing
    [Documentation]    Opens Chrome in headed (visible) mode. Required for Billing Settings
    ...    toggle cycling: the LWC dispatches an Apex call on toggle that only completes
    ...    when Chrome is running headed. Headless mode suppresses this backend event.
    ${path}=    WebDriverManager.Get Chrome Driver Path
    ${options}=    Get Headed Chrome Options
    IF    """${path}""" != "None" and """${path}""" != ""
        ${service}=    Evaluate    selenium.webdriver.chrome.service.Service(executable_path=$path)    selenium.webdriver.chrome.service
        Create Webdriver    Chrome    service=${service}    options=${options}
    ELSE
        Create Webdriver    Chrome    options=${options}
    END
    Go To    about:blank
    Maximize Browser Window

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

_Cycle Email Delivery Toggle
    [Documentation]    Turns "Configure Email Delivery Settings" toggle OFF then ON to
    ...    trigger the Salesforce backend that auto-creates the default invoice email
    ...    template and sets it as the BillingSettings.defaultEmailTemplate. A sleep
    ...    after re-enabling allows async template creation to complete.
    Disable Toggle By Label    Configure Email Delivery Settings
    Sleep    2s    reason=Allow toggle-off state to register before cycling back on
    Enable Toggle By Label    Configure Email Delivery Settings
    Sleep    5s    reason=Allow Salesforce to auto-create the default invoice email template
