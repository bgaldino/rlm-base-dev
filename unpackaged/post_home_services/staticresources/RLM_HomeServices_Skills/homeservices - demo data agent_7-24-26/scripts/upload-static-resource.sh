#!/usr/bin/env bash
# upload-static-resource.sh
# Uploads a local image file as a Salesforce Static Resource via REST API.
#
# Usage:
#   bash scripts/upload-static-resource.sh <imagePath> <resourceName>
#
# Arguments:
#   imagePath    - Absolute or relative path to the local image file (PNG recommended).
#                  In Cursor, use the absolute path returned by GenerateImage.
#   resourceName - Salesforce static resource name (alphanumeric + underscores only,
#                  no spaces or hyphens — sanitize before calling this script)
#
# Requirements:
#   - sf CLI authenticated to the target org as default org
#   - python3 (standard on macOS/Linux)
#
# Why REST (not sf project deploy start --metadata):
#   The metadata deploy path requires an SFDX project scaffold (sfdx-project.json +
#   force-app/...) and does not reliably package binary files ("Required field is
#   missing: content"). This REST approach needs no project scaffold and is idempotent.
#
# Why Python (not curl):
#   curl fails for large images because the base64-encoded body exceeds shell
#   argument length limits. Python handles the payload in-process.

set -euo pipefail

IMAGE_PATH="${1:?Usage: $0 <imagePath> <resourceName>}"
RESOURCE_NAME="${2:?Usage: $0 <imagePath> <resourceName>}"

if [[ ! "$RESOURCE_NAME" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "ERROR: Resource name '$RESOURCE_NAME' contains invalid characters." >&2
  echo "       Use alphanumeric characters and underscores only." >&2
  exit 1
fi

if [[ ! -f "$IMAGE_PATH" ]]; then
  echo "ERROR: Image file not found: $IMAGE_PATH" >&2
  exit 1
fi

EXT="${IMAGE_PATH##*.}"
EXT_LOWER=$(printf '%s' "$EXT" | tr '[:upper:]' '[:lower:]')
case "$EXT_LOWER" in
  png)       CONTENT_TYPE="image/png" ;;
  jpg|jpeg)  CONTENT_TYPE="image/jpeg" ;;
  gif)       CONTENT_TYPE="image/gif" ;;
  svg)       CONTENT_TYPE="image/svg+xml" ;;
  *)         CONTENT_TYPE="application/octet-stream" ;;
esac

echo "Fetching org credentials..."
ORG_JSON=$(sf org display --json 2>/dev/null)
INSTANCE_URL=$(echo "$ORG_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['instanceUrl'])")
ACCESS_TOKEN=$(echo "$ORG_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['accessToken'])")
API_VERSION=$(echo "$ORG_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'].get('apiVersion','66.0'))")

if [[ -z "$INSTANCE_URL" || -z "$ACCESS_TOKEN" ]]; then
  echo "ERROR: Could not retrieve org credentials. Authenticate with: sf org login web --set-default" >&2
  exit 1
fi

echo "Org: $INSTANCE_URL"
echo "Uploading static resource: $RESOURCE_NAME ($CONTENT_TYPE)"

python3 - "$IMAGE_PATH" "$RESOURCE_NAME" "$CONTENT_TYPE" "$INSTANCE_URL" "$ACCESS_TOKEN" "$API_VERSION" <<'PYEOF'
import base64, json, sys, urllib.request, urllib.error, urllib.parse

img_path, resource_name, content_type, instance_url, access_token, api_version = sys.argv[1:]

# Idempotent: skip if a static resource with this name already exists
check_url = f"{instance_url}/services/data/v{api_version}/query?q=" + \
    urllib.parse.quote(f"SELECT Id FROM StaticResource WHERE Name='{resource_name}'")
req = urllib.request.Request(check_url, headers={"Authorization": f"Bearer {access_token}"})
with urllib.request.urlopen(req) as r:
    result = json.loads(r.read())
    if result["totalSize"] > 0:
        print(f"Static resource '{resource_name}' already exists (ID: {result['records'][0]['Id']}). Skipping.")
        sys.exit(0)

with open(img_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

payload = json.dumps({
    "Name": resource_name,
    "Body": encoded,
    "ContentType": content_type,
    "CacheControl": "Public",
}).encode("utf-8")

post_url = f"{instance_url}/services/data/v{api_version}/sobjects/StaticResource"
req = urllib.request.Request(post_url, data=payload, method="POST",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        if result.get("success"):
            print(f"SUCCESS: '{resource_name}' uploaded (ID: {result['id']})")
            print(f"         Access via: /resource/{resource_name}")
        else:
            print(f"ERROR: {result}", file=sys.stderr)
            sys.exit(1)
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
    sys.exit(1)
PYEOF
