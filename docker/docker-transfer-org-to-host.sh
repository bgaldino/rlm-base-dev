#!/bin/bash
# Safely transfer a Docker-created org into host sf + CCI.
# This script is intentionally conservative:
# - Refuses to overwrite existing host sf aliases
# - Refuses to overwrite existing host CCI org names
# - Never sets host defaults

set -euo pipefail
DEFAULT_DOCKER_DEVHUB_ALIAS="dockerDevHub"
trap 'err_exit $? $LINENO' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=docker/docker-lib.sh
. "$SCRIPT_DIR/docker-lib.sh"

usage() {
    cat <<'EOF'
Usage:
  ./docker/docker-transfer-org-to-host.sh <docker-org-alias> [--host-sf-alias <alias>] [--host-cci-org <name>]

Options:
  <docker-org-alias> Required positional alias/username of org in Docker state
  --host-sf-alias  New host sf alias to create (must not exist; optional)
  --host-cci-org   New host CCI org name to create (must not exist; optional)
  -h, --help       Show help

Notes:
  - Host alias/org names auto-generate when omitted.
  - This script never sets default org/dev hub on host.
  - The auth URL is treated as sensitive and stored in a secure temp file only.
EOF
}

DOCKER_ALIAS="${1:-}"
HOST_SF_ALIAS=""
HOST_CCI_ORG=""

if [ "${DOCKER_ALIAS:-}" = "-h" ] || [ "${DOCKER_ALIAS:-}" = "--help" ]; then
    usage
    exit 0
fi

if [ -n "${DOCKER_ALIAS:-}" ]; then
    shift
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --host-sf-alias)
            HOST_SF_ALIAS="${2:-}"
            shift 2
            ;;
        --host-cci-org)
            HOST_CCI_ORG="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}" >&2
            usage
            exit 1
            ;;
    esac
done

if [ -z "$DOCKER_ALIAS" ]; then
    echo -e "${RED}Missing required positional argument: <docker-org-alias>${NC}" >&2
    usage
    exit 1
fi

for cmd in sf cci python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${RED}Required command not found: $cmd${NC}" >&2
        exit 1
    fi
done

if [ ! -f "./docker-cci.sh" ]; then
    echo -e "${RED}Run this script from repository root (docker-cci.sh not found).${NC}" >&2
    exit 1
fi

LIST_JSON="$(mktemp)"
cleanup() {
    rm -f "${ORG_JSON:-}" "${AUTH_FILE:-}" "${LIST_JSON:-}"
}
trap cleanup EXIT
chmod 600 "$LIST_JSON"

SAFE_DOCKER_ALIAS="$(printf "%s" "$DOCKER_ALIAS" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-')"
SAFE_DOCKER_ALIAS="${SAFE_DOCKER_ALIAS#-}"
SAFE_DOCKER_ALIAS="${SAFE_DOCKER_ALIAS%-}"
if [ -z "$SAFE_DOCKER_ALIAS" ]; then
    SAFE_DOCKER_ALIAS="docker-org"
fi
TS="$(date +%Y%m%d%H%M%S)"

if [ -z "$HOST_SF_ALIAS" ]; then
    HOST_SF_ALIAS="dock-xfer-${SAFE_DOCKER_ALIAS}-${TS}"
    echo -e "${BLUE}No --host-sf-alias provided. Generated: ${HOST_SF_ALIAS}${NC}"
fi

if [ -z "$HOST_CCI_ORG" ]; then
    HOST_CCI_ORG="$(printf "%s" "$HOST_SF_ALIAS" | tr '-' '_')"
    echo -e "${BLUE}No --host-cci-org provided. Generated: ${HOST_CCI_ORG}${NC}"
fi

if [ "$HOST_SF_ALIAS" = "$DOCKER_ALIAS" ] || [ "$HOST_CCI_ORG" = "$DOCKER_ALIAS" ]; then
    echo -e "${YELLOW}Warning: reusing Docker alias as host identifier increases collision risk.${NC}" >&2
fi

echo -e "${BLUE}Preflight: checking for host sf alias collision...${NC}"
sf org list --all --json > "$LIST_JSON"
if python3 - "$LIST_JSON" "$HOST_SF_ALIAS" <<'PY'
import json
import sys

json_path = sys.argv[1]
target = sys.argv[2]
data = json.load(open(json_path, "r", encoding="utf-8"))

orgs = []
for key in ("nonScratchOrgs", "scratchOrgs", "devHubs", "sandboxes", "other"):
    orgs.extend(data.get("result", {}).get(key, []) or [])

aliases = {o.get("alias") for o in orgs if o.get("alias")}
sys.exit(0 if target in aliases else 1)
PY
then
    echo -e "${RED}Host sf alias already exists: ${HOST_SF_ALIAS}${NC}" >&2
    echo -e "${RED}Stop: choose a unique alias to avoid touching existing host auth.${NC}" >&2
    exit 1
fi

echo -e "${BLUE}Preflight: checking for host CCI org collision...${NC}"
if cci org info "$HOST_CCI_ORG" >/dev/null 2>&1; then
    echo -e "${RED}Host CCI org name already exists: ${HOST_CCI_ORG}${NC}" >&2
    echo -e "${RED}Stop: choose a unique CCI org name to avoid mutating existing config.${NC}" >&2
    exit 1
fi

ORG_JSON="$(mktemp)"
AUTH_FILE="$(mktemp)"
chmod 600 "$ORG_JSON" "$AUTH_FILE"

echo -e "${BLUE}Exporting auth URL from Docker org: ${DOCKER_ALIAS}${NC}"
compose_cmd run --rm cci-robot bash -lc "set -euo pipefail; org_alias=\"\$1\"; tmp=\$(mktemp); printf \"%s\" \"\$SFDX_AUTH_URL\" > \"\$tmp\"; sf org login sfdx-url -f \"\$tmp\" -a \"\${DOCKER_DEVHUB_ALIAS:-${DEFAULT_DOCKER_DEVHUB_ALIAS}}\" -d >/dev/null; rm -f \"\$tmp\"; sf org display --target-org \"\$org_alias\" --verbose --json" _ "$DOCKER_ALIAS" > "$ORG_JSON"

python3 - "$ORG_JSON" "$AUTH_FILE" <<'PY'
import json
import sys

org_json_path = sys.argv[1]
auth_file_path = sys.argv[2]

with open(org_json_path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

url = (data.get("result") or {}).get("sfdxAuthUrl")
if not url:
    raise SystemExit("No sfdxAuthUrl returned. Re-auth org with a supported flow, then retry.")

with open(auth_file_path, "w", encoding="utf-8") as fh:
    fh.write(url)
PY

echo -e "${BLUE}Importing org into host sf alias (no defaults): ${HOST_SF_ALIAS}${NC}"
sf org login sfdx-url --sfdx-url-file "$AUTH_FILE" --alias "$HOST_SF_ALIAS"

echo -e "${BLUE}Importing alias into host CCI org: ${HOST_CCI_ORG}${NC}"
cci org import "$HOST_SF_ALIAS" "$HOST_CCI_ORG"

echo -e "${GREEN}Transfer complete.${NC}"
echo -e "${GREEN}Host sf alias: ${HOST_SF_ALIAS}${NC}"
echo -e "${GREEN}Host CCI org: ${HOST_CCI_ORG}${NC}"
echo -e "${GREEN}Verify with: sf org display --target-org ${HOST_SF_ALIAS} && cci org info ${HOST_CCI_ORG}${NC}"
