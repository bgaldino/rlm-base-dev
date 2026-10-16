*** Variables ***
# Test data — override via command line: robot -v TEST_CATALOG_NAME:"My Catalog" ...
${TEST_CATALOG_NAME}        QuantumBit Software
${TEST_PRODUCT_NAME}        QuantumBit Complete Solution
${TEST_PRODUCT_QUANTITY}    1
${TEST_ACCOUNT_NAME}        Global Media

# Bundle configurator — the optional component selected on the bundle PARENT.
# Software Maintenance is non-default (IsDefaultComponent=false), so it is only ever on the
# quote if the configurator was actually driven. It is also the product from issue #63.
${TEST_BUNDLE_OPTION_NAME}  Software Maintenance
${TEST_BUNDLE_OPTION_TAB}   Maintenance & Support

# Async operation timeouts
${ASYNC_TIMEOUT}            180s
${ASYNC_POLL_INTERVAL}      10s

# Browser mode
${HEADED}                   false
${PAUSE_FOR_RECORDING}      false

# Feature flags (passed by CCI task wrapper; default to true for QB core)
${QB}                       true
${BILLING}                  true
${CONSTRAINTS}              false
${DRO}                      false
${CLM}                      false
${RATING}                   false
