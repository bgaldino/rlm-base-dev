*** Settings ***
Documentation     Enable CRM Analytics via the Analytics Getting Started page
...               (InsightsSetupGettingStarted/home). Required for the rating data
...               processing engine in Release 262+. The old InsightsSetupSettings VF
...               iframe page was removed in Summer '26; full CRM Analytics enablement
...               is now the required step. Idempotent: if already enabled, skips the click.
Library           ../../resources/AnalyticsSetupHelper.py
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
# Set ORG_ALIAS to use sf org open --url-only for authenticated login (recommended).
${ORG_ALIAS}                   ${EMPTY}
${ANALYTICS_SETUP_PATH}        /lightning/setup/InsightsSetupGettingStarted/home

*** Test Cases ***
Enable CRM Analytics
    [Documentation]    Click the "Enable CRM Analytics" button on the CRM Analytics Getting
    ...    Started page. Idempotent: if the button is absent (already enabled), returns
    ...    'already_enabled' without clicking. No VF iframe involved — standard Lightning DOM.
    Open Setup Page    ${ANALYTICS_SETUP_PATH}
    ${result}=    Enable CRM Analytics Via Getting Started Page
    Log    Enable CRM Analytics: ${result}
