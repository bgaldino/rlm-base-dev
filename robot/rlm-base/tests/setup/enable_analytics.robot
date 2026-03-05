*** Settings ***
Documentation     Enable the "Enable Data Sync and Connections" checkbox (enableWaveReplication) on the Analytics Settings page. Required for the rating data processing engine. Does not require enabling the full CRM Analytics feature.
Library           ../../resources/AnalyticsSetupHelper.py
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
# Set ORG_ALIAS to use sf org open --url-only for authenticated login (recommended).
${ORG_ALIAS}                   ${EMPTY}
${ANALYTICS_SETUP_PATH}        /lightning/setup/InsightsSetupSettings/home
${MANUAL_LOGIN_WAIT}           90s

*** Test Cases ***
Enable Data Sync And Connections Toggle
    [Documentation]    Enable the "Enable Data Sync and Connections" checkbox in the CRM Analytics
    ...    Settings Visualforce iframe (waveSetupSettings.apexp). The setting lives inside a VF
    ...    child frame — the Lightning Web Security proxy blocks all standard DOM queries on the
    ...    outer shell, but Selenium can access the VF page directly after switching frames.
    ...    Idempotent: if already enabled, returns 'already_enabled' without clicking Save.
    ...    No explicit sleep is needed — the keyword polls for the iframe and checkboxes.
    Open Setup Page    ${ANALYTICS_SETUP_PATH}
    ${result}=    Enable Data Sync And Connections Via VF Iframe
    Log    Enable Data Sync and Connections (enableWaveReplication): ${result}
