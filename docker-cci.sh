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
RUN_ID=""
RUN_ROOT=""
STATE_ROOT=""
ARTIFACT_ROOT=""
COMPOSE_PROJECT_NAME_EFFECTIVE=""
RUN_DEVHUB_ALIAS=""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        docker compose -p "${COMPOSE_PROJECT_NAME_EFFECTIVE}" "$@"
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose -p "${COMPOSE_PROJECT_NAME_EFFECTIVE}" "$@"
    else
        echo -e "${RED}Error: neither 'docker compose' nor 'docker-compose' is available.${NC}" >&2
        exit 1
    fi
}

sanitize_slug() {
    local raw="$1"
    printf "%s" "${raw}" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed -e 's/^-*//' -e 's/-*$//'
}

make_run_id() {
    local stamp rand
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    rand="$(printf "%04x" "$((RANDOM % 65536))")"
    echo "run-${stamp}-${rand}"
}

init_context() {
    local repo_slug run_slug devhub_suffix
    repo_slug="$(sanitize_slug "$(basename "$(pwd)")")"
    if [ -z "${repo_slug}" ]; then
        repo_slug="rlm-base"
    fi

    RUN_ID="${DOCKER_RUN_ID:-$(make_run_id)}"
    run_slug="$(sanitize_slug "${RUN_ID}")"
    if [ -z "${run_slug}" ]; then
        run_slug="$(make_run_id)"
    fi

    RUN_ROOT="${DOCKER_RUN_ROOT:-./.docker/runs/${RUN_ID}}"
    STATE_ROOT="${DOCKER_STATE_ROOT:-${RUN_ROOT}/state}"
    ARTIFACT_ROOT="${RUN_ROOT}/artifacts"
    COMPOSE_PROJECT_NAME_EFFECTIVE="${DOCKER_COMPOSE_PROJECT:-${repo_slug}-${run_slug}}"
    devhub_suffix="$(printf "%s" "${run_slug}" | cut -c1-18)"
    RUN_DEVHUB_ALIAS="${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}-${devhub_suffix}}"

    mkdir -p \
        "${STATE_ROOT}/cumulusci" \
        "${STATE_ROOT}/sf" \
        "${STATE_ROOT}/sfdx" \
        "${ARTIFACT_ROOT}"

    cat > "${RUN_ROOT}/run.env" <<EOF
DOCKER_RUN_ID=${RUN_ID}
DOCKER_RUN_ROOT=${RUN_ROOT}
DOCKER_STATE_ROOT=${STATE_ROOT}
DOCKER_COMPOSE_PROJECT=${COMPOSE_PROJECT_NAME_EFFECTIVE}
DOCKER_DEVHUB_ALIAS=${RUN_DEVHUB_ALIAS}
EOF
}

contains_host_auth_mounts() {
    if rg -n '(\$\{HOME\}|~|/Users/[^:]+)/(\\.sf|\\.sfdx|\\.cumulusci):' \
        docker-compose.yml docker-compose.ci.yml >/dev/null 2>&1; then
        return 0
    fi
    return 1
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

    if contains_host_auth_mounts; then
        echo -e "${RED}Error: docker compose files contain forbidden host auth mounts (~/.sf, ~/.sfdx, ~/.cumulusci).${NC}" >&2
        echo -e "${RED}This can reintroduce AuthDecryptError and host auth corruption. Use ./.docker/... state paths only.${NC}" >&2
        exit 1
    fi

    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Warning: .env not found. Copy .env.example and set SFDX_AUTH_URL.${NC}"
    elif ! grep -q "^SFDX_AUTH_URL=force://" .env; then
        echo -e "${YELLOW}Warning: SFDX_AUTH_URL is not configured in .env.${NC}"
        echo -e "${YELLOW}Docker CCI/SF commands that need org auth may fail until this is set.${NC}"
    fi
}

command_requires_auth() {
    if [ "${DOCKER_REQUIRE_AUTH:-}" = "1" ] || [ "${DOCKER_REQUIRE_AUTH:-}" = "true" ]; then
        return 0
    fi

    if [ $# -lt 1 ]; then
        return 1
    fi

    case "$1" in
        cci)
            case "${2:-}" in
                org|flow|task) return 0 ;;
            esac
            ;;
        sf)
            case "${2:-}" in
                org|data|apex) return 0 ;;
            esac
            ;;
    esac
    return 1
}

run_in_container() {
    local require_auth="$1"
    shift

    export DOCKER_STATE_ROOT="${STATE_ROOT}"
    export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME_EFFECTIVE}"

    if [ $# -eq 0 ]; then
        compose_cmd run --rm \
            -e DOCKER_RUN_ID="${RUN_ID}" \
            -e DOCKER_RUN_ROOT="/workspace/.docker/runs/${RUN_ID}" \
            -e DOCKER_DEVHUB_ALIAS="${RUN_DEVHUB_ALIAS}" \
            cci-robot bash -lc "set -euo pipefail; auth_ok=0; if [ -n \"\${SFDX_AUTH_URL:-}\" ]; then tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; if sf org login sfdx-url -f \"\$tmp\" -a \"${RUN_DEVHUB_ALIAS}\" -d >/dev/null 2>&1; then auth_ok=1; else echo \"Warning: Docker Dev Hub bootstrap login failed.\" >&2; fi; rm -f \"\$tmp\"; fi; if [ \"${require_auth}\" = \"1\" ] && [ \"\$auth_ok\" != \"1\" ]; then echo \"Error: auth-required command blocked because bootstrap login failed. Check SFDX_AUTH_URL/DOCKER_DEVHUB_ALIAS.\" >&2; exit 2; fi; exec bash"
    else
        compose_cmd run --rm \
            -e DOCKER_RUN_ID="${RUN_ID}" \
            -e DOCKER_RUN_ROOT="/workspace/.docker/runs/${RUN_ID}" \
            -e DOCKER_DEVHUB_ALIAS="${RUN_DEVHUB_ALIAS}" \
            cci-robot bash -lc "set -euo pipefail; auth_ok=0; if [ -n \"\${SFDX_AUTH_URL:-}\" ]; then tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; if sf org login sfdx-url -f \"\$tmp\" -a \"${RUN_DEVHUB_ALIAS}\" -d >/dev/null 2>&1; then auth_ok=1; else echo \"Warning: Docker Dev Hub bootstrap login failed.\" >&2; fi; rm -f \"\$tmp\"; fi; if [ \"${require_auth}\" = \"1\" ] && [ \"\$auth_ok\" != \"1\" ]; then echo \"Error: auth-required command blocked because bootstrap login failed. Check SFDX_AUTH_URL/DOCKER_DEVHUB_ALIAS.\" >&2; exit 2; fi; exec \"\$@\"" _ "$@"
    fi
}

init_context
preflight

if [ $# -eq 0 ]; then
    echo -e "${BLUE}Starting interactive shell in rlm-base Docker container...${NC}"
    echo -e "${BLUE}Run ID: ${RUN_ID}${NC}"
    echo -e "${BLUE}Compose project: ${COMPOSE_PROJECT_NAME_EFFECTIVE}${NC}"
    echo -e "${BLUE}State root: ${STATE_ROOT}${NC}"
    run_in_container 0
else
    echo -e "${GREEN}Running in Docker: $@${NC}"
    echo -e "${GREEN}Run ID: ${RUN_ID}${NC}"
    echo -e "${GREEN}Compose project: ${COMPOSE_PROJECT_NAME_EFFECTIVE}${NC}"
    echo -e "${GREEN}State root: ${STATE_ROOT}${NC}"
    if command_requires_auth "$@"; then
        run_in_container 1 "$@"
    else
        run_in_container 0 "$@"
    fi
fi
