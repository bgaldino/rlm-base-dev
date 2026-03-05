*** Settings ***
Documentation     Enable the "Enable Data Sync and Connections" checkbox (enableWaveReplication) on the Analytics/Insights Settings page. Required for the rating data processing engine. Does not require enabling the full CRM Analytics feature.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
# Set ORG_ALIAS to use sf org open --url-only for authenticated login (recommended). Example: robot -v ORG_ALIAS:my-scratch ...
${ORG_ALIAS}                   ${EMPTY}
${ANALYTICS_SETUP_PATH}        /lightning/setup/InsightsSetupGettingStarted/home
${DATA_SYNC_TOGGLE_LABEL}      Enable Data Sync and Connections

*** Test Cases ***
Enable Data Sync And Connections Toggle
    [Documentation]    Navigate to Analytics/Insights Settings and enable the "Enable Data Sync and Connections" checkbox (enableWaveReplication). Required for the rating data processing engine flow.
    Open Setup Page    ${ANALYTICS_SETUP_PATH}
    Enable Toggle By Label    ${DATA_SYNC_TOGGLE_LABEL}
    Log    Enable Data Sync and Connections (enableWaveReplication) enabled.
