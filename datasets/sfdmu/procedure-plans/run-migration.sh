#!/usr/bin/env bash
# Run SFDMU procedure-plans migration non-interactively.
# Pipes instance URL twice (for each object set's production prompt) then "y" (for Continue? when missing parents).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCE_URL="${SFDMU_INSTANCE_URL:-storm-94ed5fe2303cf1.my.salesforce.com}"
USERNAME="${SFDMU_USERNAME:-storm.94ed5fe2303cf1@salesforce.com}"

( echo "$INSTANCE_URL"; sleep 5; echo "$INSTANCE_URL"; sleep 1; echo 'y'; ) | sf sfdmu run -s csvfile -u "$USERNAME" -p "$SCRIPT_DIR" "$@"
