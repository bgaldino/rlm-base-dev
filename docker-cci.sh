#!/bin/bash
# Wrapper script to run CumulusCI, SF CLI, or Robot Framework commands in Docker container
# Usage: ./docker-cci.sh <command>
# Examples:
#   ./docker-cci.sh cci org list
#   ./docker-cci.sh sf org list
#   ./docker-cci.sh robot --version
#   ./docker-cci.sh bash  # Interactive shell

set -euo pipefail
DEFAULT_DOCKER_DEVHUB_ALIAS="dockerDevHub"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        docker compose "$@"
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        echo -e "${RED}Error: neither 'docker compose' nor 'docker-compose' is available.${NC}" >&2
        exit 1
    fi
}

preflight() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}Error: docker is not installed or not in PATH.${NC}" >&2
        exit 1
    fi

    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Error: docker-compose.yml not found. Run this from repository root.${NC}" >&2
        exit 1
    fi

    mkdir -p ./.docker/state/cumulusci ./.docker/state/sf ./.docker/state/sfdx

    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Warning: .env not found. Copy .env.example and set SFDX_AUTH_URL.${NC}"
    elif ! grep -q "^SFDX_AUTH_URL=force://" .env; then
        echo -e "${YELLOW}Warning: SFDX_AUTH_URL is not configured in .env.${NC}"
        echo -e "${YELLOW}Docker CCI/SF commands that need org auth may fail until this is set.${NC}"
    fi
}

preflight

if [ $# -eq 0 ]; then
    echo -e "${BLUE}Starting interactive shell in rlm-base Docker container...${NC}"
    compose_cmd run --rm cci-robot bash -lc "set -euo pipefail; if [ -n \"\${SFDX_AUTH_URL:-}\" ]; then tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; if ! sf org login sfdx-url -f \"\$tmp\" -a \"\${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}}\" -d >/dev/null 2>&1; then echo \"Warning: Docker Dev Hub bootstrap login failed. Commands requiring org auth may fail.\" >&2; fi; rm -f \"\$tmp\"; fi; exec bash"
else
    echo -e "${GREEN}Running in Docker: $@${NC}"
    compose_cmd run --rm cci-robot bash -lc "set -euo pipefail; if [ -n \"\${SFDX_AUTH_URL:-}\" ]; then tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; if ! sf org login sfdx-url -f \"\$tmp\" -a \"\${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}}\" -d >/dev/null 2>&1; then echo \"Warning: Docker Dev Hub bootstrap login failed. Commands requiring org auth may fail.\" >&2; fi; rm -f \"\$tmp\"; fi; exec \"\$@\"" _ "$@"
fi
