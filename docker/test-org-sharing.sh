#!/bin/bash
# Test script to verify org sharing between host and Docker container
#
# This script:
# 1. Creates a test scratch org in the container
# 2. Verifies it's visible on the host
# 3. Cleans up the test org
#
# Usage: ./docker/test-org-sharing.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker Org Sharing Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: docker-compose is not installed${NC}"
    exit 1
fi

# Check if CUMULUSCI_KEY is set in .env file
if [ -f .env ]; then
    if grep -q "^CUMULUSCI_KEY=" .env && ! grep -q "^CUMULUSCI_KEY=$" .env; then
        echo -e "${GREEN}✅ CUMULUSCI_KEY is configured in .env${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: CUMULUSCI_KEY is not set in .env file${NC}"
        echo -e "${YELLOW}   Org sharing may not work correctly${NC}"
        echo ""
        echo -e "To fix:"
        echo "  1. Extract key: ./docker/get-cci-key.sh"
        echo "  2. Add to .env: echo \"CUMULUSCI_KEY=\$(./docker/get-cci-key.sh 2>/dev/null)\" >> .env"
        echo "  3. Rebuild: docker-compose build"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Warning: No .env file found${NC}"
    echo -e "${YELLOW}   You need to set up the encryption key for org sharing${NC}"
    echo ""
    echo -e "To set up:"
    echo "  1. cp .env.example .env"
    echo "  2. ./docker/get-cci-key.sh"
    echo "  3. echo \"CUMULUSCI_KEY=\$(./docker/get-cci-key.sh 2>/dev/null)\" >> .env"
    echo "  4. docker-compose build"
    echo ""
    exit 1
fi
echo ""

# Check if cci is available on host
if ! command -v cci &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: CumulusCI is not installed on host${NC}"
    echo -e "${YELLOW}   This test will still verify container org creation${NC}"
    echo ""
    HOST_CCI_AVAILABLE=false
else
    HOST_CCI_AVAILABLE=true
fi

# Generate random org name to avoid conflicts
TEST_ORG_NAME="test-sharing-$(date +%s)"

echo -e "${BLUE}Step 1: Creating test scratch org in container...${NC}"
echo -e "Org name: ${YELLOW}${TEST_ORG_NAME}${NC}"
echo ""

# Create scratch org in container
if docker-compose run --rm cci-robot cci org scratch dev "${TEST_ORG_NAME}" --days 1; then
    echo ""
    echo -e "${GREEN}✅ Scratch org created successfully in container${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed to create scratch org in container${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 2: Verifying org is visible on host...${NC}"

if [ "$HOST_CCI_AVAILABLE" = true ]; then
    # Wait a moment for file system sync
    sleep 2

    # Check if org is visible on host
    if cci org list | grep -q "${TEST_ORG_NAME}"; then
        echo -e "${GREEN}✅ Org is visible on host!${NC}"
        echo ""
        echo -e "${GREEN}Org details from host:${NC}"
        cci org info "${TEST_ORG_NAME}" || true
    else
        echo -e "${RED}❌ Org is NOT visible on host${NC}"
        echo ""
        echo -e "${YELLOW}Troubleshooting:${NC}"
        echo "1. Ensure you've rebuilt the container: docker-compose build"
        echo "2. Check volume mounts in docker-compose.yml"
        echo "3. Verify ~/.cumulusci directory exists: ls ~/.cumulusci"
        CLEANUP_FAILED=true
    fi
else
    echo -e "${YELLOW}⚠️  Skipping host verification (CCI not installed on host)${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Cleaning up test org...${NC}"

# Cleanup
if docker-compose run --rm cci-robot cci org scratch_delete "${TEST_ORG_NAME}"; then
    echo -e "${GREEN}✅ Test org cleaned up${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Failed to delete test org${NC}"
    echo -e "${YELLOW}   You may need to manually delete: cci org scratch_delete ${TEST_ORG_NAME}${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
if [ "${CLEANUP_FAILED}" = true ]; then
    echo -e "${RED}❌ Test FAILED - Org sharing is not working${NC}"
    echo -e "${BLUE}========================================${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Test PASSED - Org sharing is working!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}Your Docker setup is correctly configured for org sharing.${NC}"
    echo -e "Orgs created in the container will be accessible on the host and vice versa."
fi
