*** Settings ***
Documentation     Adds products to a Quote, creates and activates an Order, and verifies Assets.
...
...               Part 2 of the Quote-to-Order flow. Expects a Quote to already exist on
...               the test Account (run setup_quote first). To reuse an existing Quote by ID,
...               run Robot directly and pass QUOTE_ID with: --variable QUOTE_ID:<id>
...
...               If QUOTE_ID is not provided (or left empty when run via CCI wrapper),
...               this suite creates a fresh Quote via setup_quote steps.
...
...               Requires a fully provisioned org with qb=true (run prepare_rlm_org first).
...
...               Run via CCI (no QUOTE_ID override; will create a new Quote if needed):
...                 cci task run robot_order_from_quote --org beta
...               Run Robot directly with an existing Quote:
...                 robot --variable QUOTE_ID:<id> robot/rlm-base/tests/e2e/order_from_quote.robot
Resource          ../../resources/E2ECommon.robot
Resource          ../../variables/E2EVariables.robot
Suite Setup       Setup Order From Quote Test
Suite Teardown    Teardown Order From Quote Test

*** Variables ***
${ORG_ALIAS}            ${EMPTY}
${ACCOUNT_ID}           ${EMPTY}
${QUOTE_ID}             ${EMPTY}
${ORDER_ID}             ${EMPTY}

*** Test Cases ***

Order From Quote
    [Documentation]    Adds products via Browse Catalogs, creates and activates an Order,
    ...    then verifies Assets exist on the Account.
    [Tags]    e2e    requires_qb
    Skip If    "${QB}" == "false"    Requires qb=true for QuantumBit product catalog

    # If no Quote was passed in, create one (reset + opp + quote)
    IF    "${QUOTE_ID}" == "${EMPTY}"
        Navigate To App    Revenue Cloud
        Reset Test Account    ${ACCOUNT_ID}
        ${opp_id}=    Create Opportunity From Account    ${ACCOUNT_ID}
        ${q_id}=    Create Quote From Opportunity    ${opp_id}
        Set Suite Variable    ${QUOTE_ID}    ${q_id}
    END

    # Add products via Browse Catalogs
    Pause For Recording If Enabled    About to Browse Catalogs and add products.
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
    Pause For Recording If Enabled    Assets verified. Order-from-Quote complete.
    Log    Order-from-Quote E2E test PASSED.

*** Keywords ***

Setup Order From Quote Test
    [Documentation]    Opens browser and looks up the test Account.
    Open Browser For E2E
    Lookup Test Account

Teardown Order From Quote Test
    [Documentation]    Closes the browser. Transactional records are left for inspection.
    Run Keyword And Ignore Error    Close Browser For E2E
