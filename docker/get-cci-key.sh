#!/bin/bash
# Extract CumulusCI encryption key from system keyring
#
# This script retrieves the encryption key that CumulusCI uses to encrypt
# org credential files. The key is needed for Docker containers to read/write
# encrypted org files that are compatible with your host CumulusCI installation.
#
# The key is stored in your system keyring:
# - macOS: Keychain (via security command)
# - Linux: keyring (via python keyring library)
#
# Usage:
#   ./docker/get-cci-key.sh
#
# Output:
#   Base64-encoded encryption key (or error message)

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to try macOS Keychain extraction
extract_macos_key() {
    # Try to find the CumulusCI service in Keychain
    # The service name is "cumulusci" and account is typically the project name or a UUID
    local key=$(security find-generic-password -s "cumulusci" -w 2>/dev/null)
    if [ -n "$key" ]; then
        echo "$key"
        return 0
    fi
    return 1
}

# Function to try Python keyring extraction
extract_python_key() {
    python3 <<'EOF'
import sys
try:
    import keyring
    # Try to get the key from keyring
    key = keyring.get_password("cumulusci", "cumulusci")
    if key:
        print(key)
        sys.exit(0)
    sys.exit(1)
except Exception as e:
    sys.exit(1)
EOF
}

# Main extraction logic
echo -e "${YELLOW}Attempting to extract CumulusCI encryption key...${NC}" >&2
echo "" >&2

# Detect OS and try appropriate method
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}Detected macOS - trying Keychain...${NC}" >&2
    if KEY=$(extract_macos_key); then
        echo -e "${GREEN}✅ Successfully extracted key from macOS Keychain${NC}" >&2
        echo "$KEY"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Key not found in Keychain, trying Python keyring...${NC}" >&2
    fi
fi

# Try Python keyring (works on both macOS and Linux)
echo -e "${YELLOW}Trying Python keyring...${NC}" >&2
if KEY=$(extract_python_key); then
    echo -e "${GREEN}✅ Successfully extracted key from Python keyring${NC}" >&2
    echo "$KEY"
    exit 0
fi

# If we get here, extraction failed
echo "" >&2
echo -e "${RED}❌ Unable to extract CumulusCI encryption key${NC}" >&2
echo "" >&2
echo -e "${YELLOW}This could mean:${NC}" >&2
echo "  1. CumulusCI hasn't been used on this host yet (no key generated)" >&2
echo "  2. The keyring is locked or inaccessible" >&2
echo "  3. CumulusCI is using a different keyring service name" >&2
echo "" >&2
echo -e "${YELLOW}Solutions:${NC}" >&2
echo "" >&2
echo -e "${GREEN}Option 1: Generate a new key (simplest)${NC}" >&2
echo "  Run this command to generate a new encryption key:" >&2
echo "" >&2
echo "    python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'" >&2
echo "" >&2
echo "  Then add it to your .env file:" >&2
echo "    echo 'CUMULUSCI_KEY=<your_key>' >> .env" >&2
echo "" >&2
echo "  Note: You'll need to re-authenticate all your orgs." >&2
echo "" >&2
echo -e "${GREEN}Option 2: Use debug logging to find existing key${NC}" >&2
echo "  Run CumulusCI with verbose logging and look for the key:" >&2
echo "    CUMULUSCI_DEBUG=1 cci org list 2>&1 | grep -i key" >&2
echo "" >&2
echo -e "${GREEN}Option 3: Skip encryption (less secure)${NC}" >&2
echo "  Set CUMULUSCI_KEYCHAIN_CLASS to use unencrypted storage:" >&2
echo "    echo 'CUMULUSCI_KEYCHAIN_CLASS=cumulusci.core.keychain.BaseProjectKeychain' >> .env" >&2
echo "" >&2

exit 1
