*** Settings ***
Documentation     Resets the test Account and creates an Opportunity and Quote.
...
...               Part 1 of the Quote-to-Order flow. Can be run standalone to prepare
...               a Quote for other tests (e.g., order_from_quote, pricing validation).
...
...               Requires a fully provisioned org (run prepare_rlm_org first).
...
...               Run via CCI:
...                 cci task run robot_setup_quote --org beta
Resource          ../../resources/E2ECommon.robot
Resource          ../../variables/E2EVariables.robot
Suite Setup       Setup Quote Test
Suite Teardown    Teardown Quote Test

*** Variables ***
${ORG_ALIAS}            ${EMPTY}
${ACCOUNT_ID}           ${EMPTY}
${OPPORTUNITY_ID}       ${EMPTY}
${QUOTE_ID}             ${EMPTY}

*** Test Cases ***

Setup Quote
    [Documentation]    Resets Account, creates Opportunity and Quote.
    ...    Sets OPPORTUNITY_ID and QUOTE_ID as suite variables for downstream tests.
    [Tags]    e2e    requires_qb
    Skip If    "${QB}" == "false"    Requires qb=true for QuantumBit product catalog

    # Navigate to Revenue Cloud app
    Navigate To App    Revenue Cloud
    Capture Step Screenshot    00_revenue_cloud_app

    # Reset Account to clear transactional data
    Pause For Recording If Enabled    About to Reset Account.
    Reset Test Account    ${ACCOUNT_ID}

    # Create Opportunity
    Pause For Recording If Enabled    Account reset complete. About to Create Opportunity.
    ${opp_id}=    Create Opportunity From Account    ${ACCOUNT_ID}
    Set Suite Variable    ${OPPORTUNITY_ID}    ${opp_id}
    Capture Step Screenshot    01_opportunity_created

    # Create Quote
    Pause For Recording If Enabled    Opportunity created. About to Create Quote.
    ${q_id}=    Create Quote From Opportunity    ${OPPORTUNITY_ID}
    Set Suite Variable    ${QUOTE_ID}    ${q_id}
    Capture Step Screenshot    02_quote_created
    Pause For Recording If Enabled    Quote created. Setup complete.

*** Keywords ***

Setup Quote Test
    [Documentation]    Opens browser and looks up the test Account.
    Open Browser For E2E
    Lookup Test Account

Teardown Quote Test
    [Documentation]    Closes the browser. Records are left for downstream tests.
    Run Keyword And Ignore Error    Close Browser For E2E
