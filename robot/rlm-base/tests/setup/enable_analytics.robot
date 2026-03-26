*** Settings ***
Documentation     Enable the "Enable Data Sync and Connections" checkbox (enableWaveReplication) on the Analytics Settings page. Required for the rating data processing engine. Does not require enabling the full CRM Analytics feature.
Library           ../../resources/AnalyticsSetupHelper.py
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
# Set ORG_ALIAS to use sf org open --url-only for authenticated login (recommended).
${ORG_ALIAS}                   ${EMPTY}
${ANALYTICS_GETTING_STARTED_PATH}    /lightning/setup/InsightsSetupGettingStarted/home
${ANALYTICS_SETUP_PATH}        /lightning/setup/InsightsSetupSettings/home
${MANUAL_LOGIN_WAIT}           90s

*** Test Cases ***
Enable Data Sync And Connections Toggle
    [Documentation]    For TSO/gated orgs, first click "Enable CRM Analytics" on the Getting
    ...    Started page so Analytics setup options become available. Then enable the
    ...    "Enable Data Sync and Connections" checkbox in the Analytics Settings VF iframe
    ...    (waveSetupSettings.apexp). Idempotent for both steps.
    Open Setup Page    ${ANALYTICS_GETTING_STARTED_PATH}
    ${pre_result}=    Enable CRM Analytics Via Getting Started Page
    Log    Enable CRM Analytics pre-step: ${pre_result}
    Open Setup Page    ${ANALYTICS_SETUP_PATH}
    ${result}=    Enable Data Sync And Connections Via VF Iframe
    Log    Enable Data Sync and Connections (enableWaveReplication): ${result}
