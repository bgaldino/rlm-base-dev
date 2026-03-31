#!/bin/bash
# Wrapper script to run CumulusCI, SF CLI, or Robot Framework commands in Docker container
# Usage: ./docker-cci.sh <command>
# Examples:
#   ./docker-cci.sh cci org list
#   ./docker-cci.sh sf org list
#   ./docker-cci.sh robot --version
#   ./docker-cci.sh bash  # Interactive shell

set -euo pipefail

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

    mkdir -p "${HOME}/.cumulusci" "${HOME}/.sf" "${HOME}/.sfdx"

    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Warning: .env not found. Copy .env.example to enable org sharing key config.${NC}"
    fi
}

preflight

if [ $# -eq 0 ]; then
    echo -e "${BLUE}Starting interactive shell in rlm-base Docker container...${NC}"
    compose_cmd run --rm cci-robot bash
else
    echo -e "${GREEN}Running in Docker: $@${NC}"
    compose_cmd run --rm cci-robot "$@"
fi
