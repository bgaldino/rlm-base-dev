#!/bin/bash
# Extract CumulusCI encryption key from host keychain/keyring.
# Supports:
# - Explicit env passthrough via CUMULUSCI_KEY
# - macOS Keychain via `security`
# - Linux via python keyring library
# - Linux Secret Service via `secret-tool`

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    printf '%b\n' "$1" >&2
}

extract_macos_key() {
    security find-generic-password -s "cumulusci" -w 2>/dev/null || return 1
}

extract_linux_secret_tool_key() {
    command -v secret-tool >/dev/null 2>&1 || return 1
    secret-tool lookup service cumulusci account cumulusci 2>/dev/null || return 1
}

extract_python_keyring_key() {
    command -v python3 >/dev/null 2>&1 || return 1
    python3 <<'EOF'
import sys
try:
    import keyring
except Exception:
    sys.exit(1)

for service, account in [
    ("cumulusci", "cumulusci"),
]:
    try:
        value = keyring.get_password(service, account)
        if value:
            print(value)
            sys.exit(0)
    except Exception:
        pass

sys.exit(1)
EOF
}

# Highest-priority path: explicit env key.
if [ -n "${CUMULUSCI_KEY:-}" ]; then
    log "${GREEN}Using CUMULUSCI_KEY from environment.${NC}"
    printf '%s\n' "${CUMULUSCI_KEY}"
    exit 0
fi

log "${YELLOW}Attempting to extract CumulusCI encryption key...${NC}"

if [[ "${OSTYPE:-}" == darwin* ]]; then
    log "${YELLOW}Detected macOS; trying Keychain service 'cumulusci'.${NC}"
    if KEY="$(extract_macos_key)"; then
        log "${GREEN}Found key in macOS Keychain.${NC}"
        printf '%s\n' "${KEY}"
        exit 0
    fi
fi

if [[ "${OSTYPE:-}" == linux* ]]; then
    log "${YELLOW}Detected Linux; trying Secret Service keyring.${NC}"
    if KEY="$(extract_linux_secret_tool_key)"; then
        log "${GREEN}Found key via secret-tool.${NC}"
        printf '%s\n' "${KEY}"
        exit 0
    fi
fi

log "${YELLOW}Trying Python keyring fallback...${NC}"
if KEY="$(extract_python_keyring_key)"; then
    log "${GREEN}Found key via python keyring.${NC}"
    printf '%s\n' "${KEY}"
    exit 0
fi

log ""
log "${RED}Unable to extract a CumulusCI encryption key automatically.${NC}"
log ""
log "${YELLOW}Next steps:${NC}"
log "1) If you already have the key, export it and retry:"
log "   export CUMULUSCI_KEY='<existing_key>'"
log "   ./docker/get-cci-key.sh"
log ""
log "2) Or generate a new key (requires re-auth in both host/container):"
log "   python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
log ""
log "3) Add the key to .env:"
log "   echo \"CUMULUSCI_KEY=<your_key>\" >> .env"

exit 1
