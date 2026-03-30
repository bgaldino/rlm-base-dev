*** Settings ***
Documentation     End-to-end Quote-to-Order flow combining setup_quote and order_from_quote.
...
...               Runs the full sales workflow in a single browser session:
...               Reset Account → Create Opportunity → Create Quote →
...               Browse Catalogs → Add Products → Create Order → Activate Order → Verify Assets.
...
...               Requires a fully provisioned org with qb=true (run prepare_rlm_org first).
...
...               Run via CCI:
...                 cci task run robot_e2e --org beta
...                 cci task run robot_e2e_debug --org beta   (headed + CDP debug)
Resource          ../../resources/E2ECommon.robot
Resource          ../../variables/E2EVariables.robot
Suite Setup       Setup Quote To Order Test
Suite Teardown    Teardown Quote To Order Test

*** Variables ***
${ORG_ALIAS}            ${EMPTY}
${ACCOUNT_ID}           ${EMPTY}
${OPPORTUNITY_ID}       ${EMPTY}
${QUOTE_ID}             ${EMPTY}
${ORDER_ID}             ${EMPTY}

*** Test Cases ***

Quote To Order
    [Documentation]    Complete Quote-to-Order flow using Browse Catalogs UI.
    ...    Resets the Account, creates Opportunity → Quote → adds products via
    ...    Browse Catalogs → creates and activates an Order → verifies Assets.
    [Tags]    e2e    requires_qb
    Skip If    "${QB}" == "false"    Requires qb=true for QuantumBit product catalog

    # --- Part 1: Setup Quote ---

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

    # --- Part 2: Order From Quote ---

    # Add products via Browse Catalogs
    Pause For Recording If Enabled    Quote created. About to Browse Catalogs and add products.
    Add Products Via Browse Catalogs    ${QUOTE_ID}    ${TEST_CATALOG_NAME}    ${TEST_PRODUCT_NAME}
    Capture Step Screenshot    03_products_added

    # Create Order
    Pause For Recording If Enabled    Products added. About to Create Order.
    ${order_id}=    Create Order From Quote    ${QUOTE_ID}
    Set Suite Variable    ${ORDER_ID}    ${order_id}
    Capture Step Screenshot    04_order_created

    # Activate Order
    Pause For Recording If Enabled    Order created. About to Activate Order.
    Activate Order    ${ORDER_ID}

    # Verify assets (async — poll until at least 1 asset exists)
    Wait Until Keyword Succeeds    ${ASYNC_TIMEOUT}    ${ASYNC_POLL_INTERVAL}
    ...    Verify Assets Exist On Account    ${ACCOUNT_ID}
    Navigate To Account    ${ACCOUNT_ID}
    Click Record Page Tab    Assets
    Capture Step Screenshot    05_assets_tab
    Pause For Recording If Enabled    Assets verified. Quote-to-Order complete.
    Log    Quote-to-Order E2E test PASSED.

*** Keywords ***

Setup Quote To Order Test
    [Documentation]    Opens browser and looks up the test Account.
    Open Browser For E2E
    Lookup Test Account

Teardown Quote To Order Test
    [Documentation]    Closes the browser. Transactional records are left for inspection.
    Run Keyword And Ignore Error    Close Browser For E2E
