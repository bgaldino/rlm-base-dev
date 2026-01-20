# Postman Collection Testing Guide - v260 Endpoints

**Date:** 2026-01-20
**Collections:** RLM & RCA APIs v66.0 (Winter '26 Release)
**Status:** Ready for Testing

---

## 🎯 Testing Objectives

This guide will help you test the newly implemented v260 API endpoints in the RCA collection to ensure:
1. ✅ API version detection works correctly
2. ✅ All endpoints have proper URL structure
3. ✅ Authentication is configured properly
4. ✅ Request/response formats are valid
5. ✅ New v260 features work as expected

---

## 📋 Pre-Testing Checklist

### 1. Postman Environment Setup

You'll need to configure the following essential variables in your Postman environment:

#### Essential Variables (Required for ALL requests)
```
_endpoint      : Your Salesforce org URL (e.g., https://yourorg.my.salesforce.com)
version        : Will be auto-detected (e.g., 66.0)
apiVersion     : Will be auto-detected (e.g., v66.0)
```

#### OAuth2 Authentication Variables
```
clientId       : Your Connected App Consumer Key
clientSecret   : Your Connected App Consumer Secret
username       : Your Salesforce username
password       : Your Salesforce password + security token
```

### 2. Salesforce Org Requirements

Your test org must have:
- ✅ Revenue Lifecycle Management (RLM) package installed
- ✅ Revenue Cloud APIs enabled
- ✅ API version 66.0 (Winter '26) or higher
- ✅ Connected App configured with OAuth2
- ✅ User permissions for Revenue Cloud features

### 3. Connected App Setup

1. **Create Connected App** in Salesforce Setup:
   - Enable OAuth Settings: ✅
   - Callback URL: `https://oauth.pstmn.io/v1/callback`
   - Selected OAuth Scopes:
     - Full access (full)
     - Perform requests at any time (refresh_token, offline_access)
     - Access and manage your data (api)

2. **Configure OAuth Policy**:
   - Permitted Users: All users may self-authorize
   - IP Relaxation: Relax IP restrictions
   - Refresh Token Policy: Refresh token is valid until revoked

---

## 🚀 Testing Phases

### Phase 1: Authentication & Version Detection

#### Test 1.1: Get API Version
**Collection:** RLM or RCA
**Folder:** Setup / Pre-Request
**Expected Result:** Sets `version` and `apiVersion` environment variables

```javascript
// Pre-request script should set:
pm.environment.set("version", "66.0");
pm.environment.set("apiVersion", "v66.0");
```

**Validation:**
- Check Environment tab in Postman
- Verify `version` = `66.0` or higher
- Verify `apiVersion` = `v66.0` or higher

#### Test 1.2: OAuth2 Authentication
**Collection:** RLM or RCA
**Endpoint:** Any GET request (e.g., Get Products)
**Expected Result:** 200 OK with valid Bearer token

**Troubleshooting:**
- 401 Unauthorized → Check Connected App credentials
- 400 Bad Request → Verify username/password/security token
- SSL Error → Update _endpoint to use https://

---

### Phase 2: Test Core v260 Features (P0 Critical)

#### Test 2.1: Invoice Schedulers
**Folder:** Invoice Schedulers (v260)

**Test Sequence:**
1. **Create Invoice Scheduler** → Should return 201 Created with scheduler ID
2. **Get Invoice Scheduler** → Should return 200 OK with scheduler details
3. **Update Invoice Scheduler** → Should return 200 OK with updated data
4. **Delete Invoice Scheduler** → Should return 204 No Content

**Sample Variables Needed:**
```
accountId: <valid Account ID from your org>
invoiceSchedulerId: <captured from Create response>
```

**Expected Flow:**
```
POST /services/data/v66.0/commerce/invoicing/invoice-schedulers
→ Capture response ID → Set as {{invoiceSchedulerId}}
→ Use in subsequent GET/PATCH/DELETE requests
```

#### Test 2.2: Payment Schedulers
**Folder:** Payment Schedulers (v260)

**Test Sequence:**
1. **Create Payment Scheduler** → 201 Created
2. **Get Payment Scheduler** → 200 OK
3. **Update Payment Scheduler** → 200 OK
4. **Delete Payment Scheduler** → 204 No Content

**Sample Variables Needed:**
```
accountId: <valid Account ID>
paymentSchedulerId: <captured from Create response>
```

#### Test 2.3: Product Configurator
**Folder:** Product Configurator (v260)

**Test Sequence:**
1. **Configure Product** → Returns session ID
2. **Add Configuration Nodes** → Adds child products
3. **Set Product Quantity** → Updates quantity
4. **Get Configuration Instance** → Retrieves current state
5. **Save Configuration Instance** → Saves for later
6. **Get Saved Configuration** → Retrieves saved config

**Sample Variables Needed:**
```
productId: <valid Product2 ID with configuration enabled>
configSessionId: <captured from Configure Product response>
childProductId: <valid child product ID>
savedConfigurationId: <captured from Save response>
```

#### Test 2.4: Invoicing Actions
**Folder:** Invoicing Actions (v260)

**Test Key Endpoints:**
1. **Create Billing Schedule** → Creates schedule for order item
2. **Generate Invoices** → Generates draft invoices
3. **Preview Invoice** → Preview before posting
4. **Post Invoices** → Posts invoices to AR

**Sample Variables Needed:**
```
accountId: <valid Account ID>
orderItemId: <valid Order Item ID>
billingScheduleId: <captured from Create response>
invoiceId: <captured from Generate response>
```

---

### Phase 3: Test Enhanced Features (P1 High Priority)

#### Test 3.1: PCM Index Management
**Folder:** PCM Index Management (v260)

**Test Sequence:**
1. **Get Index Configurations** → Lists current index fields
2. **Get Index Settings** → Shows auto-indexing status
3. **Update Index Settings** → Modifies settings
4. **Get Index Snapshots** → Shows index health
5. **Get Index Errors** → Shows any indexing errors

**Variables Needed:** None (read-only operations)

#### Test 3.2: PCM Enhancements
**Folder:** PCM Enhancements (v260)

**Test Sequence:**
1. **Deep Clone Product** → Clones product with related records
2. **Get Unit of Measure Info** → Retrieves UoM metadata
3. **Calculate Rounded UoM Data** → Tests UoM rounding

**Sample Variables Needed:**
```
productId: <valid Product2 ID to clone>
```

#### Test 3.3: Billing Actions
**Folder:** Billing Actions (v260)

**Test Sequence:**
1. **Apply Payment** → Applies payment to invoice
2. **Unapply Payment Line** → Reverses payment application
3. **Apply Refund** → Processes refund
4. **Void Credit Memo** → Voids a credit memo

**Sample Variables Needed:**
```
paymentId: <valid Payment record ID>
invoiceId: <valid Invoice ID>
refundId: <valid Refund ID>
creditMemoId: <valid Credit Memo ID>
```

---

### Phase 4: Test Advanced Features (P2 Medium Priority)

#### Test 4.1: Revenue Management
**Folder:** Revenue Management (v260)

**Test Ramp Deals:**
1. **Create Ramp Deal** → Creates ramped pricing schedule
2. **View Ramp Deal** → Retrieves ramp details
3. **Update Ramp Deal** → Modifies percentages
4. **Delete Ramp Deal** → Removes ramp deal

**Test Asset Lifecycle:**
1. **Amend Asset** → Modifies existing asset
2. **Renew Asset** → Renews subscription
3. **Cancel Asset** → Cancels subscription

**Sample Variables Needed:**
```
salesTransactionContextId: <valid STC ID>
rampDealId: <captured from Create response>
assetId: <valid Asset ID>
```

#### Test 4.2: Decision Explainer
**Folder:** Decision Explainer (v260)

**Test Debug Endpoints:**
1. **Get Action Logs by Context** → Retrieves decision logs
2. **Get DRO Decomposition Logs** → Debug DRO rules
3. **Get Pricing Decision Logs** → Debug pricing decisions

**Sample Variables Needed:**
```
contextCode: <valid context code>
droId: <valid DRO ID>
pricingId: <valid pricing execution ID>
```

#### Test 4.3: Usage Details
**Folder:** Usage Details (v260)

**Test Usage Tracking:**
1. **Get Asset Usage Details** → Retrieves usage for asset
2. **Get Quote Line Item Usage Details** → Usage on quote
3. **Trace Usage Consumption** → Debug usage rating
4. **Validate Usage Products** → Validates usage config

**Sample Variables Needed:**
```
assetId: <valid Asset ID with usage>
quoteLineItemId: <valid Quote Line Item ID>
usageProductId: <valid Usage Product ID>
```

---

## 🧪 Newman CLI Testing (Automated)

For automated testing using Newman CLI:

### Basic Newman Test
```bash
newman run "RCA APIs - Winter'25 (258) Latest.postman_collection.json" \
  --environment "RCA APIs - Composable MQ25 Latest.postman_environment.json" \
  --folder "Invoice Schedulers (v260)" \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export ./test-results/v260-invoice-schedulers.html
```

### Test All v260 Folders
```bash
#!/bin/bash

FOLDERS=(
  "Invoice Schedulers (v260)"
  "Payment Schedulers (v260)"
  "Product Configurator (v260)"
  "Invoicing Actions (v260)"
  "PCM Index Management (v260)"
  "PCM Enhancements (v260)"
  "Billing Actions (v260)"
  "Revenue Management (v260)"
  "Decision Explainer (v260)"
  "Usage Details (v260)"
)

for folder in "${FOLDERS[@]}"; do
  echo "Testing: $folder"
  newman run "RCA APIs - Winter'25 (258) Latest.postman_collection.json" \
    --environment "RCA APIs - Composable MQ25 Latest.postman_environment.json" \
    --folder "$folder" \
    --reporters cli,htmlextra \
    --reporter-htmlextra-export "./test-results/${folder// /-}.html"
done
```

---

## ✅ Test Validation Checklist

After testing each endpoint, verify:

- [ ] **HTTP Status Code**: 200 OK, 201 Created, or 204 No Content (not 4xx/5xx)
- [ ] **Response Format**: Valid JSON structure
- [ ] **Required Fields**: All expected fields present in response
- [ ] **Variable Substitution**: All {{variables}} resolved correctly
- [ ] **Error Handling**: Appropriate error messages for invalid input
- [ ] **Side Effects**: Changes reflected in Salesforce org (if applicable)

---

## 🐛 Common Issues & Troubleshooting

### Issue 1: "Invalid Session ID" or 401 Unauthorized
**Cause:** OAuth token expired or invalid
**Solution:**
1. Re-authenticate using OAuth2
2. Check Connected App credentials
3. Verify IP restrictions are relaxed

### Issue 2: "Unknown API version: v{{version}}"
**Cause:** Version variable not set
**Solution:**
1. Run version detection script first
2. Manually set version = "66.0" in environment
3. Check pre-request scripts are enabled

### Issue 3: "Required field missing: productId"
**Cause:** Environment variable not set
**Solution:**
1. Create sample data in Salesforce org
2. Copy record IDs to environment variables
3. Use Postman Console to debug variable values

### Issue 4: "Feature not enabled: Product Configurator"
**Cause:** Feature not activated in org
**Solution:**
1. Verify RLM package includes configurator
2. Enable feature in Salesforce Setup
3. Assign proper user permissions

### Issue 5: 404 Not Found on v260 Endpoints
**Cause:** Org API version is older than v66.0
**Solution:**
1. Upgrade org to Winter '26 (v66.0) release
2. Check API version using: `GET /services/data/`
3. Verify endpoint paths match v260 specification

---

## 📊 Test Results Documentation

Create a test report with:

1. **Tested Endpoints Count**: X / 63
2. **Pass Rate**: X%
3. **Failed Tests**: List with error details
4. **Skipped Tests**: List with reasons
5. **Environment Info**:
   - Org Edition
   - API Version
   - RLM Package Version
   - Test Date

### Sample Test Report Template
```markdown
# v260 Endpoint Test Report

**Date:** 2026-01-XX
**Tester:** Your Name
**Org:** Production/Sandbox/Developer

## Summary
- Total Endpoints: 63
- Tested: XX
- Passed: XX
- Failed: XX
- Skipped: XX
- Pass Rate: XX%

## Test Results by Priority

### P0 Critical (31 endpoints)
- ✅ Invoice Schedulers: 4/4 passed
- ✅ Payment Schedulers: 4/4 passed
- ⚠️ Product Configurator: 9/11 passed (2 failed)
- ✅ Invoicing Actions: 12/12 passed

### P1 High Priority (13 endpoints)
- ✅ PCM Index Management: 6/6 passed
- ✅ PCM Enhancements: 3/3 passed
- ✅ Billing Actions: 4/4 passed

### P2 Medium Priority (19 endpoints)
- ⏭️ Revenue Management: Skipped (no test data)
- ✅ Decision Explainer: 5/5 passed
- ✅ Usage Details: 6/6 passed

## Failed Tests
1. **Configure Product - Add Nodes**
   - Error: "Invalid product hierarchy"
   - Root Cause: Child product not compatible
   - Fix: Update test data with valid child products

## Recommendations
- All critical (P0) endpoints working correctly
- Ready for CumulusCI integration
- Need sample data setup for Revenue Management tests
```

---

## 🎓 Best Practices

1. **Test in Sandbox First**: Never test destructive operations in production
2. **Use Test Data**: Create dedicated test accounts, products, and orders
3. **Clean Up**: Delete test records after testing
4. **Version Control**: Keep environment files out of git (use .gitignore)
5. **Document Findings**: Record any issues or deviations from expected behavior
6. **Automate**: Create Newman scripts for regression testing
7. **Monitor Limits**: Watch API call limits during testing

---

## 📚 Additional Resources

- [Salesforce Revenue Lifecycle Management Developer Guide (v260)](revenue_lifecycle_management_dev_guide_260.pdf)
- [V260 API Comparison Report](V260_API_COMPARISON.md)
- [Version Updates Documentation](VERSION_UPDATES.md)
- [Quick Start Guide](QUICK_START.md)
- [Newman CLI Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)

---

## 🤝 Support

If you encounter issues during testing:
1. Check Postman Console for detailed request/response logs
2. Review Salesforce debug logs
3. Consult V260_API_COMPARISON.md for endpoint specifications
4. Verify environment variables are set correctly
5. Test with simpler endpoints first (GET requests)

Good luck with your testing! 🚀
