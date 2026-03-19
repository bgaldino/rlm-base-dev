# Release 262 (Summer '26) Upgrade Plan

**Branch:** `262-test`
**Target API Version:** 67.0
**Status:** In Progress

This document tracks all work required to certify this repository against Salesforce Release 262 (Summer '26). Check off items as they are completed.

---

## 1. Infrastructure & Tooling

- [x] Create `262-test` branch from `main`
- [x] Update `sfdx-project.json` → `sourceApiVersion: 67.0`
- [x] Update `cumulusci.yml` → `api_version: 67.0`
- [x] Update `sfdcLoginUrl` to internal test pod (`login.test1.my.pc-rnd.salesforce.com`)
- [x] Bulk-update all `<apiVersion>` in `-meta.xml` files to 67.0
- [x] Bulk-update all `"apiVersion"` in SFDMU `export.json` files to 67.0
- [x] Update `manifest/package.xml` version to 67.0
- [x] Update Python task API version fallback defaults to 67.0
- [x] Update Apex scripts (`createTaxEngine.apex`) API version string to v67.0
- [ ] Configure Dev Hub org for Release 262 / Summer '26 preview
- [ ] Verify `sf CLI` version supports API 67.0
- [ ] Verify `CumulusCI` version is compatible with 67.0
- [ ] Verify `SFDMU` plugin version is compatible with 67.0

---

## 2. Scratch Org Definitions (`orgs/`)

- [ ] Review all scratch org definition files for 262-incompatible features or settings
- [ ] Verify all `features` entries are still valid in 262 (check for renamed/removed features)
- [ ] Check for new 262 features to add (e.g. new Revenue Cloud capabilities)
- [ ] Update `dev_preview.json` (`"release": "preview"`) — confirm it targets 262 preview pod
- [ ] Test scratch org creation succeeds against the 262 dev hub

---

## 3. Schema Changes

Verify SObjects and fields used across data plans and metadata against the 262 schema. Check for added, renamed, removed, or type-changed fields.

### Revenue Lifecycle Management Objects
- [ ] `Product2` — verify all fields used in `qb-pcm` plan still exist
- [ ] `ProductCatalog`, `ProductCategory`, `ProductCategoryProduct` — PCM objects
- [ ] `Pricebook2`, `PricebookEntry` — pricing plan objects
- [ ] `PriceAdjustmentSchedule`, `PriceAdjustmentTier` — pricing adjustment objects
- [ ] `ProductSellingModel`, `ProductSellingModelOption` — selling model objects
- [ ] `ProductUsageResource` (PUR), `ProductUsageResourcePricing` (PURP), `ProductUsageGroup` (PUG) — rating objects
- [ ] `RateCard`, `RateCardEntry`, `RateCardEntryAdjTier` — rates objects
- [ ] `BillingPolicy`, `BillingTreatment`, `BillingTreatmentItem` — billing objects
- [ ] `PaymentTerm` — billing plan
- [ ] `TaxPolicy`, `TaxTreatment`, `TaxTreatmentItem` — tax objects
- [ ] `ApprovalAlertContentDef` — approvals object
- [ ] `FulfillmentStepDefinition` — DRO object
- [ ] `TransactionProcessingType` — transaction processing object
- [ ] `ExpressionSet`, `ExpressionSetDefinition` — expression set objects
- [ ] `DecisionTable`, `DecisionTableDatasetLink` — decision table objects

### Supporting Objects
- [ ] `User`, `Profile`, `PermissionSet`, `PermissionSetGroup` — persona/access objects
- [ ] `Network` (Experience Cloud) — PRM/payments objects
- [ ] `EmailTemplate` — approvals email templates

---

## 4. Metadata Format Changes

Review Salesforce release notes and metadata API changelog for 262.

### Flows
- [ ] Verify `.flow-meta.xml` schema is unchanged at API 67.0
- [ ] Check for deprecated flow element types used in existing flows
- [ ] Review any new flow capabilities relevant to RLM (e.g. new action types)

### Custom Metadata / Settings
- [ ] Verify `CustomSite` metadata schema (`allowGuestPaymentsApi` etc.) unchanged
- [ ] Verify `Network` metadata schema unchanged (PRM, payments webhook site)
- [ ] Verify `ExperienceBundle` schema unchanged for PRM bundle
- [ ] Check `PaymentsSettings` metadata type for 262 changes
- [ ] Review `SecuritySettings.sessionSettings` — investigate correct API for `enableSeparateSalesforceAndSiteLogin` (issue #76, still open)

### Profiles & Permission Sets
- [ ] Verify profile metadata schema unchanged at 67.0
- [ ] Check for new permission set API fields in 262

### Layouts
- [ ] Verify layout metadata schema unchanged
- [ ] Check for new layout components available in 262

### LWC & Aura
- [ ] Verify `rlmDocPreview` LWC (`post_docgen`) is compatible with 262

### AppMenu / App Launcher
- [ ] Verify `AppMenu` metadata type unchanged for `post_tso_appmenu`

---

## 5. Data Plan Validation

Run SFDMU v5 dataset compliance check after any schema-driven updates.

- [ ] Run `python scripts/validate_sfdmu_v5_datasets.py` — confirm zero violations
- [ ] Verify `qb-pcm` plan loads cleanly on a 262 scratch org
- [ ] Verify `qb-pricing` plan (price books, adjustments, tiers)
- [ ] Verify `qb-billing` plan (billing policies, treatments, payment terms)
- [ ] Verify `qb-tax` plan (tax policies and treatments)
- [ ] Verify `qb-rating` plan (PUR, PURP, PUG)
- [ ] Verify `qb-rates` plan (rate cards, entries, adjustment tiers)
- [ ] Verify `qb-clm` plan (contract lifecycle)
- [ ] Verify `qb-dro` plan (dynamic revenue orchestration)
- [ ] Verify `qb-guidedselling` plan
- [ ] Verify `qb-approvals` plan (approval alert content defs, email templates)
- [ ] Verify `qb-transactionprocessingtypes` plan
- [ ] Verify `mfg/*` plans
- [ ] Verify `q3/*` plans

---

## 6. Full Build Verification

- [ ] Run `cci flow run prepare_rlm_org` end-to-end on a 262 scratch org
- [ ] Verify all 28 flow steps pass (check `cumulusci.yml` flow definition)
- [ ] Verify `prepare_payments` sub-flow succeeds
- [ ] Verify `prepare_prm` sub-flow succeeds (when `prm=true`)
- [ ] Verify `prepare_approvals` sub-flow succeeds (when `approvals=true`)
- [ ] Verify Robot Framework tasks pass (`enable_document_builder_toggle`, `configure_revenue_settings`, `enable_constraints_settings`)
- [ ] Trigger GitHub Actions workflow (`prepare-rlm-org.yml`) on `262-test` branch

---

## 7. Feature Flag Review

Review `project__custom__*` flags in `cumulusci.yml` against 262 capabilities.

- [ ] Confirm existing flags are still relevant in 262
- [ ] Evaluate any new 262 Revenue Cloud capabilities that warrant a new feature flag
- [ ] Check if any flags can be retired (features now standard in 262)

---

## 8. Known Open Items

| # | Item | Status |
|---|------|--------|
| #76 | `enableSeparateSalesforceAndSiteLogin` — correct metadata API mechanism unknown; Security.settings-meta.xml approach invalid | Open |
| — | Dev Hub configuration for 262-test | Pending |

---

## References

- [Salesforce Release Notes — Summer '26](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)
- [Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)
- [Revenue Cloud Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/)
- [SFDMU v5 Notes](docs/sfdmu_composite_key_optimizations.md)
