#!/bin/bash
# Shared helpers for Docker scripts.
# Source this file from scripts under docker/.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}" >&2
}

err_exit() {
    local code=${1:-1}
    local line=${2:-unknown}
    print_error "Error at line ${line} (exit ${code})"
    exit "${code}"
}

compose_cmd() {
    local project_args=()
    if [ -n "${DOCKER_COMPOSE_PROJECT:-}" ]; then
        project_args=(-p "${DOCKER_COMPOSE_PROJECT}")
    fi
    if docker compose version >/dev/null 2>&1; then
        docker compose "${project_args[@]}" "$@"
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose "${project_args[@]}" "$@"
    else
        print_error "Error: neither 'docker compose' nor 'docker-compose' is available."
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

init_docker_context() {
    local purpose="${1:-docker}"
    local repo_slug run_slug devhub_suffix
    repo_slug="$(sanitize_slug "$(basename "$(pwd)")")"
    if [ -z "${repo_slug}" ]; then
        repo_slug="rlm-base"
    fi

    export DOCKER_RUN_ID="${DOCKER_RUN_ID:-$(make_run_id)}"
    run_slug="$(sanitize_slug "${DOCKER_RUN_ID}")"
    if [ -z "${run_slug}" ]; then
        run_slug="$(make_run_id)"
    fi

    export DOCKER_RUN_ROOT="${DOCKER_RUN_ROOT:-./.docker/runs/${DOCKER_RUN_ID}}"
    export DOCKER_STATE_ROOT="${DOCKER_STATE_ROOT:-${DOCKER_RUN_ROOT}/state}"
    export DOCKER_COMPOSE_PROJECT="${DOCKER_COMPOSE_PROJECT:-${repo_slug}-${run_slug}}"
    devhub_suffix="$(printf "%s" "${run_slug}" | cut -c1-18)"
    export DOCKER_DEVHUB_ALIAS="${DOCKER_DEVHUB_ALIAS:-dockerDevHub-${devhub_suffix}}"

    mkdir -p \
        "${DOCKER_STATE_ROOT}/cumulusci" \
        "${DOCKER_STATE_ROOT}/sf" \
        "${DOCKER_STATE_ROOT}/sfdx" \
        "${DOCKER_RUN_ROOT}/artifacts"

    cat > "${DOCKER_RUN_ROOT}/run.env" <<EOF
PURPOSE=${purpose}
DOCKER_RUN_ID=${DOCKER_RUN_ID}
DOCKER_RUN_ROOT=${DOCKER_RUN_ROOT}
DOCKER_STATE_ROOT=${DOCKER_STATE_ROOT}
DOCKER_COMPOSE_PROJECT=${DOCKER_COMPOSE_PROJECT}
DOCKER_DEVHUB_ALIAS=${DOCKER_DEVHUB_ALIAS}
EOF
}

ensure_no_host_auth_mounts() {
    if rg -n '(\$\{HOME\}|~|/Users/[^:]+)/(\\.sf|\\.sfdx|\\.cumulusci):' \
        docker-compose.yml docker-compose.ci.yml >/dev/null 2>&1; then
        print_error "Forbidden host auth mount detected in compose files (~/.sf, ~/.sfdx, ~/.cumulusci)."
        print_error "Use repo-local ./.docker paths to avoid AuthDecryptError and host auth corruption."
        exit 1
    fi
}

resolve_cci_project_root() {
    local common_dir
    common_dir="$(git rev-parse --git-common-dir 2>/dev/null || true)"
    if [ -n "${common_dir}" ] && [ -d "${common_dir}" ]; then
        (cd "${common_dir}/.." && pwd)
        return 0
    fi
    pwd
}

run_cci_in_project() {
    local cci_root
    cci_root="$(resolve_cci_project_root)"
    (cd "${cci_root}" && cci "$@")
}
