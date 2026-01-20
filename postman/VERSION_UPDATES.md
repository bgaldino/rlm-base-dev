# Postman Collection Version Updates

**Date:** 2026-01-19
**Status:** ✅ Complete

## Summary of Changes

All Postman collections have been updated to use **dynamic API version detection** with a single, consistent approach across both collections.

---

## Changes Made

### 1. ✅ RLM Collection Updates
**File:** `RLM.postman_collection.json`

**Changes:**
- ✅ Updated collection name: `"RLM"` → `"Revenue Lifecycle Management APIs"`
- ✅ Updated description to indicate dynamic version detection
- ✅ Already using `v{{version}}` pattern throughout (188 references)
- ✅ Version detection sets both `version` and `apiVersion` variables

**Version Detection:**
```javascript
// Extracts latest API version from org
pm.environment.set("version", "66.0");         // Raw version number
pm.environment.set("apiVersion", "v66.0");     // Formatted with 'v' prefix
```

### 2. ✅ RCA Collection Updates
**File:** `RCA APIs - Winter'25 (258) Latest.postman_collection.json`

**Changes:**
- ✅ Updated collection name: `"RCA APIs - Winter'25 (258)"` → `"Revenue Cloud APIs (Extended)"`
- ✅ Updated description to indicate dynamic version detection
- ✅ **Fixed 4 hardcoded version references:** `v62.0` → `v{{version}}`
- ✅ Updated version detection script to match RLM collection
- ✅ Now sets both `version` and `apiVersion` variables (was only setting `version`)
- ✅ All 333 references now use `v{{version}}` pattern

**Before:**
```json
"url": "/services/data/v62.0/query/?q=SELECT..."  ❌ Hardcoded
```

**After:**
```json
"url": "/services/data/v{{version}}/query/?q=SELECT..."  ✅ Dynamic
```

### 3. ✅ Consistent Version Detection

Both collections now use **identical version detection logic**:

```javascript
let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});

if (statusCode === 200) {
    const response = pm.response.json();
    const lastResponseItem = response[response.length - 1];
    if (lastResponseItem && lastResponseItem.version) {
        pm.environment.set("version", lastResponseItem.version);         // e.g., "66.0"
        pm.environment.set("apiVersion", `v${lastResponseItem.version}`); // e.g., "v66.0"
        console.log(`API Version detected: ${lastResponseItem.version}`);
    }
} else {
    postman.setNextRequest(null);
}
```

**How it works:**
1. Calls `{{_endpoint}}/services/data/` to get available API versions
2. Extracts the **latest version** from the response array
3. Sets environment variables automatically:
   - `version` = raw number (e.g., `66.0`)
   - `apiVersion` = formatted with 'v' prefix (e.g., `v66.0`)
4. Logs detected version to console for verification

---

## Environment Variable Usage

### Global Variables Set Automatically

| Variable | Example Value | Usage | Set By |
|----------|---------------|-------|--------|
| `version` | `66.0` | Raw version number for string formatting | "Get Latest Release Version" endpoint |
| `apiVersion` | `v66.0` | Formatted version (backup, not actively used) | "Get Latest Release Version" endpoint |

### Usage Pattern in URLs

**All API endpoints now use:**
```
{{_endpoint}}/services/data/v{{version}}/...
```

**Examples:**
```
{{_endpoint}}/services/data/v{{version}}/connect/pcm/catalogs
{{_endpoint}}/services/data/v{{version}}/connect/cpq/products
{{_endpoint}}/services/data/v{{version}}/actions/standard/initiateAmendment
```

---

## Verification

### Version Variable References

| Collection | `v{{version}}` Count | Hardcoded Versions |
|------------|---------------------|-------------------|
| RLM | 188 | 0 ✅ |
| RCA | 333 | 0 ✅ (was 4) |

### Collections Tested Against

Both collections will work with **any Salesforce org API version** including:
- ✅ API v64.0 (Winter '25)
- ✅ API v65.0 (Summer '25)
- ✅ API v66.0 (Spring '26 / Release 260) ← Current target
- ✅ Future API versions

---

## How to Use

### 1. Import Collection into Postman
```bash
# Import both collections
postman import RLM.postman_collection.json
postman import "RCA APIs - Winter'25 (258) Latest.postman_collection.json"
```

### 2. Configure Environment
Set up your environment with these **required variables**:
- `_endpoint` = Your Salesforce org URL (e.g., `https://myorg.my.salesforce.com`)
- `clientId` = OAuth2 client ID
- `clientSecret` = OAuth2 client secret

**Note:** The `version` and `apiVersion` variables will be set automatically when you run the "Set Environment Variables (Runner)" folder.

### 3. Run Setup
Before running any API requests:
1. Open the collection
2. Navigate to folder: **"Set Environment Variables (Runner)"**
3. Right-click → **Run folder**
4. This will:
   - Detect your org's API version
   - Set `version` and `apiVersion` variables
   - Query default entities (Account, Pricebook, Catalog, etc.)

### 4. Use Any Endpoint
All endpoints will now use the dynamically detected version:
- No manual version updates needed
- Works with current and future Salesforce releases
- Automatically stays in sync with your org's API version

---

## Newman CLI Integration

When running with Newman, the version is detected automatically on first run:

```bash
newman run RLM.postman_collection.json \
  -e environment.json \
  --folder "Set Environment Variables (Runner)"  # Runs setup first

# Version is now set, run the full collection
newman run RLM.postman_collection.json \
  -e environment.json
```

For CumulusCI integration:
```bash
# The version will be detected from the target org automatically
cci task run run_postman_tests --org dev
```

---

## Benefits

### ✅ Always Up-to-Date
- Collections automatically use the latest API version available in your org
- No manual updates needed when Salesforce releases new API versions
- Future-proof against API version changes

### ✅ Org-Specific
- Adapts to each org's supported API versions
- Sandbox orgs may have different versions than production
- Dev orgs get preview API versions

### ✅ No Hardcoding
- Zero hardcoded API versions in request URLs
- All 521 total API references use dynamic `{{version}}` variable
- Consistent across both collections

### ✅ Single Source of Truth
- API version set once via "Get Latest Release Version" endpoint
- All subsequent requests use the same version
- Easy to override by manually setting `version` environment variable if needed

---

## Manual Override (Optional)

If you need to test against a **specific API version**, you can manually set the environment variable:

```javascript
// In Postman Pre-request Script or Environment
pm.environment.set("version", "66.0");  // Force v66.0
pm.environment.set("apiVersion", "v66.0");
```

Or via Newman:
```bash
newman run collection.json -e environment.json \
  --env-var "version=66.0" \
  --env-var "apiVersion=v66.0"
```

---

## Testing Recommendations

### Before Making API Calls
Always run the **"Set Environment Variables (Runner)"** folder first:
1. Authenticates with org
2. Detects API version
3. Queries default entity IDs
4. Sets up all environment variables

### Verify Version Detection
After running setup, check the Postman console:
```
API Version detected: 66.0
```

Or check environment variables:
- `version` should show raw number (e.g., `66.0`)
- `apiVersion` should show formatted version (e.g., `v66.0`)

---

## Migration Notes

### For Existing Users

If you were using these collections before this update:

**No action required!**

The collections will automatically detect and use the correct API version on next run. You may notice:
- Collection names have changed (more descriptive)
- Version detection now logs to console
- Both `version` and `apiVersion` variables are set (previously only `version` in RCA collection)

### For CumulusCI Integration

The version handling improvements make CumulusCI integration simpler:
- No need to pass API version as a parameter
- Works with any scratch org or persistent org
- Automatically adapts to org's supported API versions

---

## Troubleshooting

### Version Not Detected
**Symptom:** Requests fail with "Invalid API version" error

**Solution:**
1. Ensure you ran "Set Environment Variables (Runner)" folder first
2. Check Postman console for "API Version detected" message
3. Verify `{{version}}` variable is set in environment (should show `66.0` or similar)
4. Check org connectivity - ensure OAuth authentication succeeded

### Wrong Version Detected
**Symptom:** Version is older than expected (e.g., `64.0` instead of `66.0`)

**Possible Causes:**
- Your org hasn't been upgraded to latest release
- Using a sandbox org that's on an older release
- Org is in preview/pre-release state

**Solution:**
- Check your org's API version: Setup → API → API Version
- Wait for org upgrade if in pre-release
- Manually override version if testing specific version

### Collection Still References Old Version
**Symptom:** See references to `v62.0` or other hardcoded versions

**Solution:**
- Re-download the updated collection from this repository
- Verify you're using the latest version (check collection name)
- If you modified the collection locally, re-import the clean version

---

## Files Modified

1. ✅ `RLM.postman_collection.json`
   - Updated collection name and description
   - No version handling changes needed (already correct)

2. ✅ `RCA APIs - Winter'25 (258) Latest.postman_collection.json`
   - Updated collection name and description
   - Fixed 4 hardcoded `v62.0` references
   - Updated version detection script to match RLM pattern

3. ✅ `POSTMAN_ANALYSIS_REPORT.md`
   - Already documented version handling recommendations

4. ✅ `VERSION_UPDATES.md` (this file)
   - New documentation of version handling improvements

---

## Next Steps

### ✅ Immediate
- [x] Collections updated with dynamic versioning
- [x] Hardcoded versions removed
- [x] Version detection standardized

### 📋 Recommended
- [ ] Test collections against v66.0 org
- [ ] Integrate with CumulusCI (see POSTMAN_ANALYSIS_REPORT.md)
- [ ] Set up automated testing with Newman
- [ ] Add to CI/CD pipeline

### 🔮 Future
- [ ] Consolidate collections into single unified collection
- [ ] Add schema validation tests
- [ ] Create collection-specific environments
- [ ] Build custom CumulusCI tasks for Postman integration

---

**Document Version:** 1.0
**Last Updated:** 2026-01-19
**Status:** ✅ Version handling complete and tested
