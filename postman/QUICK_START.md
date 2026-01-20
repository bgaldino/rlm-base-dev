# Postman Collections Quick Start Guide

**Last Updated:** 2026-01-19
**Status:** ✅ Ready to Use

---

## Prerequisites

✅ **Newman CLI Installed**
```bash
newman --version
# Output: 6.2.2 ✓

which newman-reporter-htmlextra
# Output: /Users/bgaldino/.nvm/versions/node/v24.12.0/bin/newman-reporter-htmlextra ✓
```

---

## Quick Test (Without Live Org)

Test that collections are structurally valid:

```bash
cd postman/

# Validate RLM collection
newman run RLM.postman_collection.json --bail --dry-run

# Validate RCA collection
newman run "RCA APIs - Winter'25 (258) Latest.postman_collection.json" --bail --dry-run
```

**Expected:** No errors (collections are valid JSON)

---

## Test Against Live Org

### Step 1: Set Up Environment Variables

Create a test environment file or use one of the existing ones:

```bash
# Option A: Use existing environment
cp "RLM QuantumBit Default Environment.postman_environment.json" my-test-env.json

# Option B: Create new environment from scratch
cat > my-test-env.json << 'EOF'
{
  "name": "My Test Org",
  "values": [
    {"key": "_endpoint", "value": "https://YOUR_ORG.my.salesforce.com", "enabled": true},
    {"key": "clientId", "value": "YOUR_OAUTH_CLIENT_ID", "enabled": true},
    {"key": "clientSecret", "value": "YOUR_OAUTH_CLIENT_SECRET", "enabled": true}
  ]
}
EOF
```

**Required Variables:**
- `_endpoint` - Your Salesforce org URL
- `clientId` - OAuth2 Connected App client ID
- `clientSecret` - OAuth2 Connected App client secret

### Step 2: Run Setup (Version Detection)

This runs the "Set Environment Variables (Runner)" folder to detect API version and query default entities:

```bash
# RLM Collection
newman run RLM.postman_collection.json \
  -e my-test-env.json \
  --folder "Set Environment Variables (Runner)" \
  --reporters cli

# Expected output:
# API Version detected: 66.0
# ✓ Base URL extracted and set to _endpoint
# ✓ defaultAccountId set
# ✓ standardPricebookId set
# etc.
```

### Step 3: Run Full Collection

Once setup completes, run the full collection:

```bash
# RLM Collection with CLI reporter
newman run RLM.postman_collection.json \
  -e my-test-env.json \
  --reporters cli

# RCA Collection with CLI reporter
newman run "RCA APIs - Winter'25 (258) Latest.postman_collection.json" \
  -e my-test-env.json \
  --reporters cli
```

### Step 4: Generate HTML Report

For better visibility, use the htmlextra reporter:

```bash
# Create results directory
mkdir -p results

# Run with HTML report
newman run RLM.postman_collection.json \
  -e my-test-env.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export results/rlm-test-report.html

# Open report in browser
open results/rlm-test-report.html
```

---

## Run Specific Folder

Test a specific API area:

```bash
# Test only Product Catalog Management
newman run RLM.postman_collection.json \
  -e my-test-env.json \
  --folder "Product Catalog Management" \
  --reporters cli

# Test only Billing APIs (RCA collection)
newman run "RCA APIs - Winter'25 (258) Latest.postman_collection.json" \
  -e my-test-env.json \
  --folder "Billing" \
  --reporters cli
```

---

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--bail` | Stop on first failure | `newman run ... --bail` |
| `--delay-request 500` | Delay 500ms between requests | Avoid rate limits |
| `--timeout-request 30000` | Request timeout (30 sec) | Slow API responses |
| `--iteration-count 3` | Run collection 3 times | Load testing |
| `--env-var "key=value"` | Override env variable | Force specific version |
| `--verbose` | Detailed output | Debugging |
| `--color off` | Disable colors | CI/CD logs |

---

## CumulusCI Integration

### Option 1: Manual Newman Task

Add to `cumulusci.yml`:

```yaml
tasks:
  run_rlm_api_tests:
    description: Run RLM API tests with Newman
    class_path: cumulusci.tasks.command.Command
    options:
      command: >
        newman run postman/RLM.postman_collection.json
        --env-var "_endpoint={{org.instance_url}}"
        --env-var "clientId={{org.config.client_id}}"
        --env-var "clientSecret={{org.config.client_secret}}"
        --reporters cli,htmlextra
        --reporter-htmlextra-export results/api-test-report.html
        --bail
```

Run via CumulusCI:
```bash
cci task run run_rlm_api_tests --org dev
```

### Option 2: Custom Python Task (Advanced)

See `POSTMAN_ANALYSIS_REPORT.md` for detailed implementation guide.

---

## Troubleshooting

### Error: "Could not get any response"

**Cause:** Wrong endpoint URL or org authentication failure

**Solution:**
```bash
# Verify endpoint
echo $YOUR_ORG_URL

# Test authentication manually
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$YOUR_CLIENT_ID" \
  -d "client_secret=$YOUR_CLIENT_SECRET"
```

### Error: "Invalid API version"

**Cause:** Version variable not set

**Solution:**
1. Run "Set Environment Variables (Runner)" folder first
2. Or manually set version:
```bash
newman run ... --env-var "version=66.0"
```

### Error: "getaddrinfo ENOTFOUND"

**Cause:** Invalid org URL in `_endpoint`

**Solution:**
- Ensure URL format: `https://yourorg.my.salesforce.com` (no trailing slash)
- For sandboxes: `https://yourorg--sandbox.sandbox.my.salesforce.com`

### Rate Limit Errors (429)

**Cause:** Too many requests too quickly

**Solution:**
```bash
# Add delay between requests
newman run ... --delay-request 1000
```

---

## Next Steps

1. ✅ Newman installed
2. ⏭️ Set up environment variables (see Step 1 above)
3. ⏭️ Run setup folder to detect version
4. ⏭️ Test individual folders
5. ⏭️ Run full collection
6. ⏭️ Generate HTML reports
7. ⏭️ Integrate with CumulusCI

---

## Additional Resources

- **Full Analysis:** `POSTMAN_ANALYSIS_REPORT.md`
- **Version Details:** `VERSION_UPDATES.md`
- **Test Results:** `TEST_VALIDATION_REPORT.txt`
- **Newman Docs:** https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/

---

**Document Version:** 1.0
**Author:** Postman Collections Setup
**Status:** ✅ Ready for testing
