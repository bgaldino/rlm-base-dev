# Release 262 (Summer '26) Upgrade Plan

**Branch:** `262-test`
**Target API Version:** 67.0
**Status:** In Progress

This document tracks all work required to certify this repository against Salesforce Release 262 (Summer '26). Check off items as they are completed.

---

## Analysis Approach

Release 262 is pre-feature-freeze — no official Salesforce documentation exists yet. All schema and behavioral analysis must be performed by direct org inspection, comparing a 260 baseline scratch org against a 262 preview scratch org. Official docs will supplement analysis once CX begins producing them post-release-freeze.

### Workstation Model

Two workstations with distinct capabilities are used in combination:

| Capability | Personal workstation | Salesforce workstation |
|---|---|---|
| Cursor model | sonnet (default) | Opus (for deep analysis) |
| Spending limits | Standard | Enterprise (higher limits) |
| Chrome extension | ✅ Live org tab access | ❌ Not permitted |
| UI-only validation | ✅ Via Chrome extension | ❌ Manual only |
| sf / cci CLI | ✅ | ✅ |
| Claude Code CLI | ✅ | ✅ (Opus, for long analysis sessions) |

### Phased Execution

| Phase | Work | Workstation | Status |
|---|---|---|---|
| 1 — Setup | Provision scratch orgs; write and commit schema query scripts | Personal | Pending org setup |
| 2 — Data Collection | Run `FieldDefinition`/`EntityDefinition` queries against both orgs; commit diff output | Personal | Blocked on Phase 1 |
| 3 — Deep Analysis | Cross-reference schema diffs against data plans, Apex scripts, export.json files | Salesforce (Opus) | Blocked on Phase 2 |
| 4 — UI Validation | Validate UI-only settings and toggles in 262 org via Chrome extension | Personal | Parallel with Phase 3 |
| 5 — Implementation | Data plan fixes, Apex updates, build verification | Either | Blocked on Phases 3–4 |

The `262-test` branch and this document are the shared source of truth across both workstations. Pull before starting any phase; commit and push at the end of each phase before switching workstations.

### Org Setup Required Before Phase 1

New scratch orgs are needed rather than reusing any existing orgs:
- **260 baseline** — fresh scratch org on Release 260 (Spring '26) for pre-upgrade schema baseline
- **262 preview** — fresh scratch org on Release 262 (Summer '26) preview pod

See Section 1 (Infrastructure) and Section 2 (Scratch Org Definitions) for prerequisites.

---

## 1. Infrastructure & Tooling

- [x] Create `262-test` branch from `main`
- [x] Update `sfdx-project.json` → `sourceApiVersion: 67.0`
- [x] Update `cumulusci.yml` → `api_version: 67.0`
- [x] `sfdcLoginUrl`: set to internal test pod (`login.test1.pc-rnd.salesforce.com`) on `262-test` branch; set to `https://login.salesforce.com` on feature branches working against production orgs
- [x] Bulk-update all `<apiVersion>` in `-meta.xml` files to 67.0
- [x] Bulk-update all `"apiVersion"` in SFDMU `export.json` files to 67.0
- [x] Update `manifest/package.xml` version to 67.0
- [x] Update Python task API version fallback defaults to 67.0
- [x] Update Apex scripts (`createTaxEngine.apex`) API version string to v67.0
- [ ] Configure Dev Hub org for Release 262 / Summer '26 preview
- [ ] Verify `sf CLI` version supports API 67.0
- [ ] Verify `CumulusCI` version is compatible with 67.0
- [ ] Verify `SFDMU` plugin version is compatible with 67.0
- [ ] Review current authenticated org list (`sf org list`) and clean up stale orgs
- [ ] Provision new 260 baseline scratch org for schema comparison (Phase 1 prerequisite)
- [ ] Provision new 262 preview scratch org for schema comparison (Phase 1 prerequisite)

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

> **Analysis method:** No 262 documentation is available pre-release-freeze. All schema verification is performed by querying `FieldDefinition` and `EntityDefinition` via SOQL on both a 260 baseline scratch org and a 262 preview scratch org, then diffing the results. Query scripts live in `scripts/schema_diff/` (created during Phase 1). Checkboxes below are updated during Phase 3 (deep analysis on Salesforce workstation with Opus).

### Revenue Lifecycle Management Objects
- [ ] `Product2` — verify all fields used in `qb-pcm` plan still exist
- [ ] `ProductCatalog`, `ProductCategory`, `ProductCategoryProduct` — PCM objects
- [ ] `Pricebook2`, `PricebookEntry` — pricing plan objects
- [ ] `PriceAdjustmentSchedule`, `PriceAdjustmentTier` — pricing adjustment objects
- [ ] `ProductSellingModel`, `ProductSellingModelOption` — selling model objects
- [x] `ProductUsageResource` (PUR), `ProductUsageResourcePolicy` (PURP, API name confirmed in 262), `ProductUsageGroup` (PUG) — rating objects; overlap validation now enforced on activation (see #262-4)
- [x] `RateCard`, `RateCardEntry`, `RateCardEntryAdjTier` — `RateCard.Status` removed in 262 (see #262-3); `RateCardEntry.Status` still present but DML via SOAP fails (see #262-2)
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

Review Salesforce release notes and metadata API changelog for 262. UI-only settings (toggles with no metadata API equivalent) are validated via the Chrome extension on the personal workstation during Phase 4.

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

- [x] Run `cci flow run prepare_rlm_org` end-to-end on a 262 scratch org — full build confirmed successful
- [ ] Verify all 28 flow steps pass (check `cumulusci.yml` flow definition)
- [ ] Verify `prepare_payments` sub-flow succeeds
- [ ] Verify `prepare_prm` sub-flow succeeds (when `prm=true`)
- [ ] Verify `prepare_approvals` sub-flow succeeds (when `approvals=true`)
- [x] Verify Robot Framework tasks pass — `enable_analytics_replication` rewritten for 262 (see Known Issues #262-1)
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
| #262-1 | **`InsightsSetupSettings` VF page removed** — Analytics Setup VF iframe (`waveSetupSettings.apexp`) removed in 262. Old robot test failed with "Analytics Settings VF iframe not found". **Fixed:** `enable_analytics.robot` and `AnalyticsSetupHelper.py` rewritten to click "Enable CRM Analytics" on `/lightning/setup/InsightsSetupGettingStarted/home`. Full CRM Analytics enablement (not the lightweight Data Sync toggle) is now required. `enableAnalytics` is not a valid `AnalyticsSettings` metadata field in v67 — robot/UI approach is the only path. | Resolved |
| #262-2 | **`RateCardEntry` DML via SOAP/Apex Execute Anonymous raises `UNKNOWN_EXCEPTION` (500)** — Platform regression in 262. Both `AnonymousApexTask` and `sf apex run` against `RateCardEntry` fail. REST API works correctly. **Fixed:** `activate_rates` task replaced with new `tasks/rlm_activate_rates.py` Python class using REST Composite API (25 records per request). | Resolved |
| #262-3 | **`RateCard.Status` field removed** — The `Status` field on `RateCard` was completely removed in 262. Any Apex or SOQL referencing `RateCard.Status` must be removed. `activateRatingRecords.apex` already does not reference it (only `RateCardEntry.Status` is used). Review any custom scripts if porting from pre-262. | Resolved (no change needed in current scripts) |
| #262-4 | **PUR idempotency — "effective period overlaps" on second run** — In 262, the platform enforces overlap validation when activating `ProductUsageResource` records that share the same Product+UsageResource with overlapping effective dates. On a second `prepare_rating` run, SFDMU `deleteOldData: true` cannot delete Active PURs, so new Draft PURs are inserted alongside existing Active ones. If those Draft PURs have children (PUGs/PURPs), step 2.5 in `activateRatingRecords.apex` cannot delete them. **Fixed:** Added step 2.5a to `activateRatingRecords.apex` — deletes Draft PUG/PURP children of identified duplicate Draft PURs first, then refreshes `purIdsWithChildren` so the main deletion loop proceeds. | Resolved |

---

## References

- [Salesforce Release Notes — Summer '26](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)
- [Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)
- [Revenue Cloud Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/)
- [SFDMU v5 Notes](../references/sfdmu-composite-key-optimizations.md)
