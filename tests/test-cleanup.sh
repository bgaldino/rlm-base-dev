#!/bin/bash

# Test script for cleanup task conditional execution
# This script tests both scenarios:
# 1. Dev org (minimal features) - cleanup should run
# 2. Enterprise org (full features) - cleanup should have fewer removals

set -eo pipefail

ORG_ALIAS_DEV="test-cleanup-dev"
ORG_ALIAS_ENT="test-cleanup-ent"
LOG_FILE="cleanup-test.log"

echo "========================================="
echo "Testing Cleanup Task - Conditional Execution"
echo "========================================="
echo ""

# Clean up any existing test orgs
echo "Cleaning up any existing test orgs..."
cci org scratch_delete "$ORG_ALIAS_DEV" --no-prompt 2>/dev/null || true
cci org scratch_delete "$ORG_ALIAS_ENT" --no-prompt 2>/dev/null || true

echo ""
echo "========================================="
echo "Test 1: Dev Org (Minimal Features)"
echo "========================================="
echo "Expected: Cleanup should REMOVE fields/PSLs"
echo ""

echo "Creating dev scratch org with alias: $ORG_ALIAS_DEV"
cci org scratch dev "$ORG_ALIAS_DEV" --days 1

echo "Running prepare_rlm_org flow (up to cleanup step)..."
cci flow run prepare_rlm_org --org "$ORG_ALIAS_DEV" 2>&1 | tee "$LOG_FILE"
grep -E "(cleanup|Removed|Skipping|Success|Failed)" "$LOG_FILE" || true

echo ""
echo "Checking what was removed in dev org..."
if grep -q "Removed .* from" "$LOG_FILE"; then
    echo "✅ Cleanup ran - fields/PSLs were removed"
else
    echo "⚠️  No removals found - check if cleanup ran"
fi

echo ""
echo "========================================="
echo "Test 2: Enterprise Org (Full Features)"
echo "========================================="
echo "Expected: Cleanup should have fewer removals than dev"
echo ""

echo "Creating ent scratch org with alias: $ORG_ALIAS_ENT"
cci org scratch ent "$ORG_ALIAS_ENT" --days 1

LOG_FILE_ENT="cleanup-test-ent.log"
echo "Running prepare_rlm_org flow (up to cleanup step)..."
cci flow run prepare_rlm_org --org "$ORG_ALIAS_ENT" 2>&1 | tee "$LOG_FILE_ENT"
grep -E "(cleanup|Removed|Skipping|Success|Failed)" "$LOG_FILE_ENT" || true

echo ""
echo "Checking cleanup behavior in enterprise org..."
if grep -q "Removed .* from" "$LOG_FILE_ENT"; then
    echo "⚠️  Cleanup ran - compare removal count with dev org (should be fewer)"
else
    echo "✅ No removals in enterprise org"
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
echo "Logs saved to: $LOG_FILE (dev), $LOG_FILE_ENT (ent)"
echo ""
echo "Note: The cleanup task runs conditionally based on org_config.scratch"
echo "Both orgs are scratch orgs, so cleanup will run for both."
echo "The difference is in which fields/PSLs are available in each org type."
echo ""
echo "To verify conditional execution based on features, you may need to:"
echo "1. Check if certain fields deploy successfully in enterprise org"
echo "2. Compare deployment errors between the two orgs"
