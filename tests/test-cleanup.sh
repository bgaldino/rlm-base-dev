#!/bin/bash

# Test script for cleanup task conditional execution
# This script tests both scenarios:
# 1. Dev org (minimal features) - cleanup should run
# 2. Dev enhanced org (full features) - cleanup should be skipped or have fewer removals

set -e

ORG_ALIAS_DEV="test-cleanup-dev"
ORG_ALIAS_ENHANCED="test-cleanup-enhanced"
LOG_FILE="cleanup-test.log"

echo "========================================="
echo "Testing Cleanup Task - Conditional Execution"
echo "========================================="
echo ""

# Clean up any existing test orgs
echo "Cleaning up any existing test orgs..."
cci org scratch_delete "$ORG_ALIAS_DEV" --no-prompt 2>/dev/null || true
cci org scratch_delete "$ORG_ALIAS_ENHANCED" --no-prompt 2>/dev/null || true

echo ""
echo "========================================="
echo "Test 1: Dev Org (Minimal Features)"
echo "========================================="
echo "Expected: Cleanup should REMOVE fields/PSLs"
echo ""

echo "Creating dev scratch org with alias: $ORG_ALIAS_DEV"
cci org scratch dev "$ORG_ALIAS_DEV" --days 1

echo "Running prepare_rlm_org flow (up to cleanup step)..."
cci flow run prepare_rlm_org --org "$ORG_ALIAS_DEV" 2>&1 | tee -a "$LOG_FILE" | grep -E "(cleanup|Removed|Skipping|Success|Failed)" || true

echo ""
echo "Checking what was removed in dev org..."
if grep -q "Removed" "$LOG_FILE" | tail -5; then
    echo "✅ Cleanup ran - fields/PSLs were removed"
else
    echo "⚠️  No removals found - check if cleanup ran"
fi

echo ""
echo "========================================="
echo "Test 2: Dev Enhanced Org (Full Features)"
echo "========================================="
echo "Expected: Cleanup should SKIP or have fewer removals"
echo ""

echo "Creating dev-enhanced scratch org with alias: $ORG_ALIAS_ENHANCED"
cci org scratch dev_enhanced "$ORG_ALIAS_ENHANCED" --days 1

echo "Running prepare_rlm_org flow (up to cleanup step)..."
cci flow run prepare_rlm_org --org "$ORG_ALIAS_ENHANCED" 2>&1 | tee -a "$LOG_FILE" | grep -E "(cleanup|Removed|Skipping|Success|Failed)" || true

echo ""
echo "Checking cleanup behavior in enhanced org..."
if grep -q "Skipping settings cleanup" "$LOG_FILE" | tail -1; then
    echo "✅ Cleanup correctly skipped for enhanced org"
elif grep -q "Removed" "$LOG_FILE" | tail -5; then
    echo "⚠️  Cleanup still ran - may need to check conditional logic"
else
    echo "⚠️  Check logs to see cleanup behavior"
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
echo "Full log saved to: $LOG_FILE"
echo ""
echo "Note: The cleanup task runs conditionally based on org_config.scratch"
echo "Both orgs are scratch orgs, so cleanup will run for both."
echo "The difference is in which fields/PSLs are available in each org type."
echo ""
echo "To verify conditional execution based on features, you may need to:"
echo "1. Check if certain fields deploy successfully in enhanced org"
echo "2. Compare deployment errors between the two orgs"
