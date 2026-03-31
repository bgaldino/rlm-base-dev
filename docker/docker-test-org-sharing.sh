#!/bin/bash
# Test script to verify Docker scratch creation and host visibility.
#
# This script:
# 1. Creates a scratch org in Docker via SF CLI using SFDX_AUTH_URL.
# 2. Safely transfers auth to new host sf/CCI names.
# 3. Verifies host CCI can resolve the imported org.
# 4. Cleans up only ephemeral test aliases and scratch org.
#
# Usage: ./docker/docker-test-org-sharing.sh

set -euo pipefail
CLEANUP_FAILED=false
DEFAULT_DOCKER_DEVHUB_ALIAS="dockerDevHub"
trap 'err_exit $? $LINENO' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=docker/docker-lib.sh
. "$SCRIPT_DIR/docker-lib.sh"

preflight() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}❌ Error: docker is not installed${NC}"
        exit 1
    fi

    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}❌ Error: docker-compose.yml not found (run from repo root)${NC}"
        exit 1
    fi

    mkdir -p ./.docker/state/cumulusci ./.docker/state/sf ./.docker/state/sfdx
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker Org Sharing Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

preflight

# Check if SFDX_AUTH_URL is set in .env file
if [ -f .env ]; then
    if grep -q "^SFDX_AUTH_URL=force://" .env; then
        echo -e "${GREEN}✅ SFDX_AUTH_URL is configured in .env${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: SFDX_AUTH_URL is not set in .env file${NC}"
        echo -e "${YELLOW}   Scratch org creation from Dev Hub will fail${NC}"
        echo ""
        echo -e "To fix:"
        echo "  1. Get auth URL: sf org display --verbose -o <DevHubAlias> | grep \"Sfdx Auth Url\""
        echo "  2. Add to .env: SFDX_AUTH_URL=force://PlatformCLI::..."
        echo "  3. Re-run this test"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Warning: No .env file found${NC}"
    echo -e "${YELLOW}   You need to set SFDX_AUTH_URL for Docker auth${NC}"
    echo ""
    echo -e "To set up:"
    echo "  1. cp .env.example .env"
    echo "  2. Add SFDX_AUTH_URL from your Dev Hub"
    echo "  3. Re-run this script"
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

# Generate random names to avoid collisions
TEST_ORG_NAME="test-sharing-$(date +%s)"
HOST_SF_ALIAS="dock-xfer-${TEST_ORG_NAME}"
HOST_CCI_ORG="dock_xfer_${TEST_ORG_NAME//-/_}"

echo -e "${BLUE}Step 1: Creating test scratch org in container...${NC}"
echo -e "Org name: ${YELLOW}${TEST_ORG_NAME}${NC}"
echo ""

if compose_cmd run --rm cci-robot bash -lc "set -euo pipefail; tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; sf org login sfdx-url -f \"\$tmp\" -a \"\${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}}\" -d >/dev/null; rm -f \"\$tmp\"; sf org create scratch --definition-file orgs/dev.json --alias ${TEST_ORG_NAME} --duration-days 1 --target-dev-hub \"\${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}}\" --json >/dev/null"; then
    echo ""
    echo -e "${GREEN}✅ Scratch org created successfully in container${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed to create scratch org in container${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 2: Safely transferring org to host sf + CCI...${NC}"

if [ "$HOST_CCI_AVAILABLE" = true ]; then
    if ./docker/docker-transfer-org-to-host.sh \
        "${TEST_ORG_NAME}" \
        --host-sf-alias "${HOST_SF_ALIAS}" \
        --host-cci-org "${HOST_CCI_ORG}"; then
        echo -e "${GREEN}✅ Org transferred safely to host${NC}"
        echo ""
        echo -e "${GREEN}Org details from host:${NC}"
        cci org info "${HOST_CCI_ORG}" || true
    else
        echo -e "${RED}❌ Safe host transfer failed${NC}"
        echo ""
        echo -e "${YELLOW}Troubleshooting:${NC}"
        echo "1. Confirm Docker org exists: ./docker-cci.sh sf org list"
        echo "2. Ensure no host collisions:"
        echo "   sf org list --all | rg ${HOST_SF_ALIAS}"
        echo "   cci org list | rg ${HOST_CCI_ORG}"
        echo "3. Retry transfer for detailed output:"
        echo "   ./docker/docker-transfer-org-to-host.sh ${TEST_ORG_NAME} --host-sf-alias ${HOST_SF_ALIAS} --host-cci-org ${HOST_CCI_ORG}"
        CLEANUP_FAILED=true
    fi
else
    echo -e "${YELLOW}⚠️  Skipping host verification (CCI not installed on host)${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Cleaning up test org...${NC}"

# Cleanup Docker scratch org.
if compose_cmd run --rm cci-robot bash -lc "sf org delete scratch --target-org ${TEST_ORG_NAME} --no-prompt >/dev/null"; then
    # Remove only host entities created by this test run.
    cci org remove "${HOST_CCI_ORG}" >/dev/null 2>&1 || true
    sf org logout --target-org "${HOST_SF_ALIAS}" --no-prompt >/dev/null 2>&1 || true
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
    echo -e "Orgs created in Docker can be imported to host sf/CCI without touching existing host aliases."
fi
