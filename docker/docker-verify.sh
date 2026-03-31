#!/bin/bash
# Verify Docker setup for this repo.
# --quick: Non-destructive checks only
# --full: Quick checks + docker org sharing smoke test

set -euo pipefail
trap 'err_exit $? $LINENO' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=docker/docker-lib.sh
. "$SCRIPT_DIR/docker-lib.sh"

MODE="full"
for arg in "$@"; do
    case "$arg" in
        --quick) MODE="quick" ;;
        --full) MODE="full" ;;
        -h|--help)
            cat <<'EOF'
Usage:
  ./docker/docker-verify.sh --quick
  ./docker/docker-verify.sh --full

Modes:
  --quick  Run non-destructive environment/auth checks only
  --full   Run quick checks plus docker/docker-test-org-sharing.sh
EOF
            exit 0
            ;;
        *)
            print_error "Unknown argument: $arg"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

print_header "Docker Verification"
print_info "Mode: ${MODE}"
echo ""

if ! command -v docker >/dev/null 2>&1; then
    print_error "docker is not installed."
    exit 1
fi
if ! command -v sf >/dev/null 2>&1; then
    print_error "sf CLI is not installed."
    exit 1
fi
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Run from repository root."
    exit 1
fi

print_info "Checking Docker Compose availability..."
compose_cmd version >/dev/null
print_success "Docker Compose is available."

print_info "Checking local .env auth configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env not found. Copy .env.example and set SFDX_AUTH_URL."
elif ! grep -q "^SFDX_AUTH_URL=force://" .env; then
    print_warning "SFDX_AUTH_URL not set in .env; auth-required checks may fail."
else
    print_success "SFDX_AUTH_URL is configured."
fi

print_info "Running container CLI sanity checks..."
./docker-cci.sh cci version >/dev/null
./docker-cci.sh sf --version >/dev/null
print_success "Container cci/sf commands succeeded."

if [ "$MODE" = "quick" ]; then
    echo ""
    print_success "Quick verification passed."
    exit 0
fi

echo ""
print_info "Running full smoke test (creates and deletes test scratch org)..."
"$SCRIPT_DIR/docker-test-org-sharing.sh"
echo ""
print_success "Full verification passed."
