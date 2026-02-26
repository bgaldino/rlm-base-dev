#!/bin/bash
# Wrapper script to run CumulusCI, SF CLI, or Robot Framework commands in Docker container
# Usage: ./docker-cci.sh <command>
# Examples:
#   ./docker-cci.sh cci org list
#   ./docker-cci.sh sf org list
#   ./docker-cci.sh robot --version
#   ./docker-cci.sh bash  # Interactive shell

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure directories exist on host
mkdir -p ~/.cumulusci ~/.sf ~/.sfdx

if [ $# -eq 0 ]; then
    echo -e "${BLUE}Starting interactive shell in rlm-base Docker container...${NC}"
    docker-compose run --rm cci-robot bash
else
    echo -e "${GREEN}Running in Docker: $@${NC}"
    docker-compose run --rm cci-robot "$@"
fi
