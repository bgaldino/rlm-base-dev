*** Settings ***
Documentation     End-to-end Quote-to-Order flow combining setup_quote and order_from_quote.
...
...               Runs the full sales workflow in a single browser session:
...               Reset Account → Create Opportunity → Create Quote →
...               Browse Catalogs → Add Products → Configure Bundle Line →
...               Create Order → Activate Order → Verify Assets →
...               Verify Renewal Opportunity Includes Product.
...               A second test runs the same flow contract-first (tag ``contract``).
...
...               Requires a fully provisioned org with qb=true (run prepare_rlm_org first).
...
...               Run via CCI (the robot_* tasks reject --org, issue #320 — select the org first):
...                 cci org default beta
...                 cci task run robot_e2e
...                 cci task run robot_e2e_debug -o pause_for_recording true   (headed + CDP debug)
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
${CONTRACT_ID}          ${EMPTY}

*** Test Cases ***

Quote To Order
    [Documentation]    Complete Quote-to-Order flow using Browse Catalogs UI.
    ...    Resets the Account, creates Opportunity → Quote → adds products via
    ...    Browse Catalogs → configures the bundle parent → creates and
    ...    activates an Order → verifies Assets → verifies the renewal
    ...    Opportunity includes the configured product. The Order has no
    ...    Contract, so the renewal Opportunity's ContractId stays blank.
    [Tags]    e2e    requires_qb
    Skip If    "${QB}" == "false"    Requires qb=true for QuantumBit product catalog
    Run Quote To Order Flow

Quote To Order With Contract
    [Documentation]    The same flow, contract-first: the Contract is created from the
    ...    Quote (its New Contract action, the RLM_CreateContractFromQuote flow) and
    ...    activated before the Order is
    ...    created, so the Order carries it. Verifies the renewal Opportunity's
    ...    ContractId equals the Order's, which the no-contract test can't, since
    ...    there both are blank.
    [Tags]    e2e    requires_qb    contract
    Skip If    "${QB}" == "false"    Requires qb=true for QuantumBit product catalog
    Run Quote To Order Flow    with_contract=${True}

*** Keywords ***

Run Quote To Order Flow
    [Documentation]    The Quote-to-Order steps shared by both test cases. With
    ...    ``with_contract``, the Contract is created from the Quote and activated
    ...    before the Order is created, and the Order is checked to carry it.
    [Arguments]    ${with_contract}=${False}

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

    # Configure the bundle PARENT and select the non-default maintenance component.
    # Adding the bundle alone does NOT reach the configurator, which is why issue #63 —
    # a Renewal Opportunity flow failure on a formerly derived-priced product — survived
    # this suite. See Configure Bundle Line for the DOM contract.
    Pause For Recording If Enabled    Products added. About to configure the bundle.
    Configure Bundle Line    ${QUOTE_ID}    ${TEST_PRODUCT_NAME}
    ...    ${TEST_BUNDLE_OPTION_NAME}    ${TEST_BUNDLE_OPTION_TAB}
    Capture Step Screenshot    03b_bundle_configured

    # Contract-first variant: create and activate the Contract from the Quote, so the
    # Order (and the renewal Opportunity the flow creates from it) carries a real ContractId.
    IF    ${with_contract}
        ${contract_id}=    Create Contract From Quote    ${QUOTE_ID}
        Set Suite Variable    ${CONTRACT_ID}    ${contract_id}
    END

    # Create Order
    Pause For Recording If Enabled    Products added. About to Create Order.
    ${order_id}=    Create Order From Quote    ${QUOTE_ID}
    Set Suite Variable    ${ORDER_ID}    ${order_id}
    IF    ${with_contract}
        # Without this, the renewal assertion's ContractId check would compare blank with blank.
        SalesforceAPI.Verify Field Value Via API    Order    ${ORDER_ID}    ContractId    ${CONTRACT_ID}
    END
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

    # ⚠ The issue-#63 detector. Must come AFTER activation, and it is not redundant with the
    # Order status: the renewal flow is PlatformEvent-triggered, so it fails silently and the
    # Order still reaches Activated. This assertion is the only thing here that can fail when
    # a configured bundle component breaks the renewal flow.
    Verify Renewal Opportunity Includes Product    ${ACCOUNT_ID}    ${TEST_BUNDLE_OPTION_NAME}    ${OPPORTUNITY_ID}    ${ORDER_ID}
    Capture Step Screenshot    06_renewal_opportunity_verified

    Pause For Recording If Enabled    Assets verified. Quote-to-Order complete.
    Log    Quote-to-Order E2E test PASSED.


Setup Quote To Order Test
    [Documentation]    Opens browser and looks up the test Account.
    Open Browser For E2E
    Lookup Test Account

Teardown Quote To Order Test
    [Documentation]    Closes the browser. Transactional records are left for inspection.
    Run Keyword And Ignore Error    Close Browser For E2E
