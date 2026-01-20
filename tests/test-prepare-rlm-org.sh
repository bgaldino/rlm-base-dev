#!/bin/bash
# Test script for prepare_rlm_org flow with dev scratch org
# This script will create a dev scratch org and run the prepare_rlm_org flow

set -e  # Exit on error

echo "=========================================="
echo "RLM Base - Testing prepare_rlm_org Flow"
echo "=========================================="
echo ""

# Configuration
SCRATCH_ORG_ALIAS="test-rlm-dev"
FLOW_NAME="prepare_rlm_org"
DAYS=1  # Short duration for testing

echo "Step 1: Creating dev scratch org..."
echo "  Alias: $SCRATCH_ORG_ALIAS"
echo "  Config: orgs/dev.json"
echo "  Duration: $DAYS day(s)"
echo ""

cci org scratch dev "$SCRATCH_ORG_ALIAS" --days "$DAYS" || {
    echo "ERROR: Failed to create scratch org"
    echo "Note: You may need to run: cci org scratch dev $SCRATCH_ORG_ALIAS --days $DAYS"
    exit 1
}

echo ""
echo "Step 2: Setting default org..."
cci org default "$SCRATCH_ORG_ALIAS" || {
    echo "ERROR: Failed to set default org"
    exit 1
}

echo ""
echo "Step 3: Running prepare_rlm_org flow..."
echo "  This may take a while and may fail due to license/permission issues"
echo "  Expected failures: Permission Set License assignments, missing licenses"
echo ""

# Run the flow and capture output
cci flow run "$FLOW_NAME" --org "$SCRATCH_ORG_ALIAS" 2>&1 | tee flow-output.log || {
    echo ""
    echo "=========================================="
    echo "Flow execution completed with errors"
    echo "=========================================="
    echo ""
    echo "Review flow-output.log for details"
    echo ""
    echo "Common issues to check:"
    echo "  1. Permission Set Licenses - may not be available in dev org"
    echo "  2. Missing feature licenses (tso, qbrix, etc.)"
    echo "  3. Missing dependencies or metadata"
    echo ""
    echo "To adjust custom flags, edit cumulusci.yml custom section:"
    echo "  - Set tso: false (if not Trialforce Source Org)"
    echo "  - Set qbrix: false (if xDO licenses not available)"
    echo ""
}

echo ""
echo "Step 4: Checking org info..."
cci org info "$SCRATCH_ORG_ALIAS" || echo "Could not get org info"

echo ""
echo "=========================================="
echo "Test completed"
echo "=========================================="
echo ""
echo "To delete the scratch org:"
echo "  cci org scratch_delete $SCRATCH_ORG_ALIAS"
echo ""
echo "To view flow output:"
echo "  cat flow-output.log"
echo ""
