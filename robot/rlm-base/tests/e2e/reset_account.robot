*** Settings ***
Documentation     Resets the test Account by running the RLM_Reset_Account QuickAction.
...
...               Clears transactional data (Opportunities, Quotes, Orders, Assets)
...               before re-running E2E tests.
...
...               Run via CCI:
...                 cci task run robot_reset_account --org beta
Resource          ../../resources/E2ECommon.robot
Resource          ../../variables/E2EVariables.robot
Suite Setup       Setup Reset Account
Suite Teardown    Teardown Reset Account

*** Variables ***
${ORG_ALIAS}            ${EMPTY}
${ACCOUNT_ID}           ${EMPTY}

*** Test Cases ***

Reset Account
    [Documentation]    Runs the Reset Account QuickAction on the test Account.
    [Tags]    e2e    maintenance
    Pause For Recording If Enabled    Paused on Account page before Reset.
    Reset Test Account    ${ACCOUNT_ID}
    # Verify account page reloaded
    Navigate To Account    ${ACCOUNT_ID}
    Sleep    3s    reason=Allow page to load after reset
    Capture Step Screenshot    account_after_reset
    Log    Reset Account completed successfully.

*** Keywords ***

Setup Reset Account
    [Documentation]    Opens browser and looks up the test Account.
    Open Browser For E2E
    Lookup Test Account

Teardown Reset Account
    [Documentation]    Closes the browser.
    Run Keyword And Ignore Error    Close Browser For E2E
