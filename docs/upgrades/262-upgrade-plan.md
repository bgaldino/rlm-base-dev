# Release 262 (Summer '26) Upgrade Plan

**Branch:** `262` (originally `262-test`; upgrade work consolidated onto `262` — see Section 1)
**Target API Version:** 67.0
**Status:** Substantially Complete (2026-05-27) — Phases 1–3 and 5 done; Phase 6 final remote CI verification pending; Phase 4 UI-only validation ongoing as needed.

This document tracks all work required to certify this repository against Salesforce Release 262 (Summer '26). Check off items as they are completed.

**Headline finding:** The 260 → 262 schema delta is **field-level additive** across the **254 of 263 ERD-tracked platform objects** that were extractable from both scratch orgs (`ent-r1` 260 + `rlm-base__ent-sb0` 262) — 45 fields added, 0 removed, 0 type changes, 2 polymorphic-reference targets *expanded* (not narrowed), 243 picklist values added, and 62 picklist values removed. The picklist removals are concentrated in two non-breaking maintenance categories — IANA TimeZone renames (e.g. `America/Catamarca` → `America/Argentina/Catamarca`, `Europe/Kiev` → `Europe/Kyiv`) on 5 timezone fields, and cleanup of unused industry-specific `UsageType` values (`InsuranceRuleAction`, `StageManagement`) on fulfillment objects — and were cross-checked against every maintained CSV: **no maintained CSV populates any removed picklist value**, so **no SFDMU plan remediation is required**. The same nine objects with additive deltas (`EmailTemplate`, `FulfillmentStepDefinition`/`Group`, `FulfillmentTaskAssignmentRule`, `ObjectStateDefinition`, `OmniProcessElement`, `ProductFulfillmentScenario`, `ProductRampSegment`, `ValTfrmGrp`) appear in existing data plans per `scripts/erd/schema_diff/260-vs-262-diff.md` (`--impact`), but the picklist-removal audit (see below) and additive-field semantics together leave the plans untouched.

The two expanded polymorphic references are non-breaking but worth flagging for downstream integrations: `ApprovalSubmission.RelatedRecordId` picked up several new approvable SObjects in 262 (e.g. `BuyerAccount`, `CartAction`, `CommerceConfigRelatedRecord`, conversation-related types, `TenantConsumptionAlert`), and **`Invoice.ReferenceEntityId` now also accepts `Opportunity` and `Quote`** in addition to the existing `CreditMemo`, `DebitMemo`, `Order`, and `OrderSummary` targets — this is a substantive Billing-side capability change for partners that read or set `Invoice.ReferenceEntityId` via API/Apex. Full delta in `scripts/erd/schema_diff/260-vs-262-diff.{md,json}`.

The 9 ERD-tracked objects not present in the scratch org snapshots (`AssetDowntimePeriod`, `AssetOwnerSharingRule`, `AssetShare`, `AssetTag`, `AssetWarranty`, `PricingProcedureResolution`, `ProductPriceHistoryLog`, `ProductPriceRange`, `ProductSellingModelDataTranslation`) require enabled features / shared-object profile permissions not available in the standard RLM scratch profile; the 260↔262 schema delta for these objects was inspected separately via Core UDD source review at `gitcore.soma.salesforce.com/core-2206/core-262-public@p4/262-patch` (no changes found). The publicly reviewable evidence is committed in this repo: extracted snapshots `scripts/erd/schema_diff/260-schema.json` and `262-schema.json`, the per-object diff and impact report at `scripts/erd/schema_diff/260-vs-262-diff.{md,json}`, and the change history in this `262-upgrade-plan.md` (Phase 5 below tabulates the picklist-removal audit results). Two original known-issues (#262-3 `RateCard.Status`, #262-4 PUR validation) were revised based on that schema reality. Internal-only supplemental notes (full SME write-up, scratch-org session logs) live outside the repo under `.agents/artifacts/` and are not required to audit any claim in this plan.

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
| 1 — Setup | Provision scratch orgs; write and commit schema query scripts | Personal | ✅ Complete (2026-05-27) — `ent-r1` (260) and `rlm-base__ent-sb0` (262); tooling at `scripts/erd/schema_diff/` |
| 2 — Data Collection | Use `scripts/erd/schema_diff/extract_schema.py` against both orgs: object list comes from a single `EntityDefinition` SOQL query (for `--all-objects`) or from `docs/erds/erd-data.json`, and field metadata comes from per-object `sf sobject describe`. Commit the resulting JSON snapshots and the diff. | Personal | ✅ Complete — `scripts/erd/schema_diff/{260,262}-schema.json` and `260-vs-262-diff.md` |
| 3 — Deep Analysis | Cross-reference schema diffs against data plans, Apex scripts, export.json files | Salesforce (Opus) | ✅ Complete — committed evidence: `scripts/erd/schema_diff/260-vs-262-diff.{md,json}` (per-object diff + `--impact` cross-reference against tracked SFDMU plans), and §5 Data Plan Validation below (per-(object,field) picklist-removal CSV audit). Internal-only supplemental SME write-ups (`.agents/artifacts/262-vs-260-core-schema-research.md`, `.agents/artifacts/262-org-vs-core-cross-validation.md`) are NOT required to audit any claim in this plan. |
| 4 — UI Validation | Validate UI-only settings and toggles in 262 org via Chrome extension | Personal | Parallel with Phase 3 |
| 5 — Implementation | Data plan fixes, Apex updates, build verification | Either | Schema delta is field-level additive (45 fields added, 0 removed, 0 type changes, 2 polymorphic targets expanded) with value-level picklist deltas (243 added, 62 removed — IANA TimeZone renames + fulfillment `UsageType` cleanup). The picklist removals were audited against every maintained CSV; no CSV populates any removed value. Nine objects with deltas appear in maintained SFDMU plans per `--impact`, but no remediation is required: additive fields can't break loads, and the removed picklist values aren't referenced. No mandatory implementation changes identified. |

The `262` branch and this document are the shared source of truth across both workstations. Pull before starting any phase; commit and push at the end of each phase before switching workstations.

### Org Setup Required Before Phase 1

New scratch orgs are needed rather than reusing any existing orgs:
- **260 baseline** — fresh scratch org on Release 260 (Spring '26) for pre-upgrade schema baseline
- **262 preview** — fresh scratch org on Release 262 (Summer '26) preview pod

See Section 1 (Infrastructure) and Section 2 (Scratch Org Definitions) for prerequisites.

---

## 1. Infrastructure & Tooling

- [x] Create `262` upgrade branch from `main` (originally created as `262-test`; primary upgrade work consolidated onto `262`)
- [x] Update `sfdx-project.json` → `sourceApiVersion: 67.0`
- [x] Update `cumulusci.yml` → `api_version: 67.0`
- [x] `sfdcLoginUrl`: set to internal test pod (`login.test1.pc-rnd.salesforce.com`) on `262` branch; set to `https://login.salesforce.com` on feature branches working against production orgs
- [x] Bulk-update all `<apiVersion>` in `-meta.xml` files to 67.0
- [x] Bulk-update all `"apiVersion"` in SFDMU `export.json` files to 67.0
- [x] Update `manifest/package.xml` version to 67.0
- [x] Update Python task API version fallback defaults to 67.0
- [x] Update Apex scripts (`createTaxEngine.apex`) API version string to v67.0
- [x] Configure Dev Hub org for Release 262 / Summer '26 preview (`devhub-usa794`)
- [x] Verify `sf CLI` version supports API 67.0 (sf 2.133.4 confirmed against 262 scratch org `rlm-base__ent-sb0`)
- [x] Verify `CumulusCI` version is compatible with 67.0 (CCI 4.10 — `prepare_rlm_org` end-to-end success on 262 confirmed 2026-05-27)
- [x] Verify `SFDMU` plugin version is compatible with 67.0 (SFDMU v5.6.4 — all plans load against 262 with zero schema-driven failures)
- [x] Review current authenticated org list (`sf org list`) and clean up stale orgs
- [x] Provision new 260 baseline scratch org for schema comparison (`ent-r1`, API v66, ID 00DV500001Nru8DMAR)
- [x] Provision new 262 preview scratch org for schema comparison (`rlm-base__ent-sb0`, API v67)

---

## 2. Scratch Org Definitions (`orgs/`)

- [x] Review all scratch org definition files for 262-incompatible features or settings (no 262-incompatible features found)
- [x] Verify all `features` entries are still valid in 262 (`prepare_rlm_org` succeeded end-to-end against `rlm-base__ent-sb0`)
- [x] Check for new 262 features to add (none required — schema delta is purely additive at field level, no new feature flags needed)
- [x] Update preview org definition (`"release": "preview"`) — confirm it targets 262 preview pod (dev_preview.json removed in org cleanup)
- [x] Test scratch org creation succeeds against the 262 dev hub (multiple successful `prepare_rlm_org` runs)

---

## 3. Schema Changes

Verify SObjects and fields used across data plans and metadata against the 262 schema. Check for added, renamed, removed, or type-changed fields.

> **Analysis method:** No 262 documentation is available pre-release-freeze. All schema verification is performed against both a 260 baseline scratch org and a 262 preview scratch org via `scripts/erd/schema_diff/extract_schema.py`, then diffed with `diff_schemas.py`. Within the extractor, the **object list** comes from either `docs/erds/erd-data.json` or a single `EntityDefinition` SOQL query (when invoked with `--all-objects`), and **field metadata for each object** comes from `sf sobject describe`. `FieldDefinition` SOQL is not used by the production extractor — `sf sobject describe` returns the same field metadata in a single per-object call and surfaces relationship targets without follow-up queries. Query scripts live in `scripts/erd/schema_diff/` (created during Phase 1). Checkboxes below are updated during Phase 3 (deep analysis on Salesforce workstation with Opus).

### Revenue Lifecycle Management Objects

**Schema verified via 260-vs-262 scratch org diff (`scripts/erd/schema_diff/260-vs-262-diff.md`) on 2026-05-27.**
**Cross-referenced against Core source research (`.agents/artifacts/262-vs-260-core-schema-research.md`) and org-vs-Core cross-validation (`.agents/artifacts/262-org-vs-core-cross-validation.md`).**

- [x] `Product2` — verified unchanged between 260 and 262 (no field additions/removals/type changes)
- [x] `ProductCatalog`, `ProductCategory`, `ProductCategoryProduct` — PCM objects, verified unchanged
- [x] `Pricebook2`, `PricebookEntry` — pricing plan objects, verified unchanged
- [x] `PriceAdjustmentSchedule`, `PriceAdjustmentTier` — pricing adjustment objects, verified unchanged
- [x] `ProductSellingModel`, `ProductSellingModelOption` — selling model objects, verified unchanged
- [x] `ProductUsageResource` (PUR), `ProductUsageResourcePolicy` (PURP), `ProductUsageGrant` (PUG, NOT `ProductUsageGroup` — terminology corrected) — rating objects; field schema identical between 260 and 262. Overlap validation behavior change in 262 is runtime-gated (see #262-4), not schema-level.
- [x] `RateCard`, `RateCardEntry`, `RateCardEntryAdjTier` — verified identical schema between 260 and 262. The `Status` field is on `RateCardEntry` (slot=10, present in both releases), NOT on `RateCard`. The `RateCard.Status` claim in #262-3 is misattributed — see #262-3 below.
- [x] `BillingPolicy`, `BillingTreatment`, `BillingTreatmentItem` — billing objects, verified unchanged
- [x] `PaymentTerm` — billing plan, verified unchanged
- [x] `TaxPolicy`, `TaxTreatment`, `TaxTreatmentItem` — tax objects, verified unchanged
- [x] `ApprovalAlertContentDef` — approvals object, verified unchanged
- [x] `FulfillmentStepDefinition` — DRO object: +1 field `CustomConfigParameter`. Picklist `UsageType` deprecates `InsuranceRuleAction`/`StageManagement` (zero repo references confirmed). No data plan impact.
- [x] `TransactionProcessingType` — transaction processing object, verified unchanged
- [x] `ExpressionSet` (+1 field `Type`, picklist additions only), `ExpressionSetDefinition` (verified unchanged) — expression set objects
- [x] `DecisionTable`, `DecisionTableDatasetLink` — decision table objects, verified unchanged in this org shape (Core source research flagged `DecisionTable` as having +1 BOOLEAN field at slot=28, not visible in this scratch org configuration)

### Supporting Objects
- [x] `User`, `Profile`, `PermissionSet`, `PermissionSetGroup` — persona/access objects (PSL/PSG assignments deploy and load cleanly via `prepare_rlm_org`; SFDMU plans for personas validated)
- [x] `Network` (Experience Cloud) — PRM/payments objects (deploys cleanly via `prepare_prm` with `patch_network_email_for_deploy` workaround for immutable `emailSenderAddress`)
- [x] `EmailTemplate` — approvals email templates (deploys cleanly via `prepare_approvals` sub-flow)

---

## 4. Metadata Format Changes

Review Salesforce release notes and metadata API changelog for 262. UI-only settings (toggles with no metadata API equivalent) are validated via the Chrome extension on the personal workstation during Phase 4.

**Note:** Most metadata format checks below are implicitly validated by `prepare_rlm_org` succeeding end-to-end on `rlm-base__ent-sb0` (262) — the build deploys flows, profiles, permission sets, layouts, LWCs, AppMenu, ExperienceBundle, CustomSite, Network, and all other listed metadata types. A passing build means the metadata format is compatible with API 67.0. Checkboxes marked complete on this basis.

### Flows
- [x] Verify `.flow-meta.xml` schema is unchanged at API 67.0 (deploys cleanly via `prepare_rlm_org`)
- [x] Check for deprecated flow element types used in existing flows (no failures during deploy)
- [x] Review any new flow capabilities relevant to RLM (no immediate capability adoption needed; tracked for future)

### Custom Metadata / Settings
- [x] Verify `CustomSite` metadata schema (`allowGuestPaymentsApi` etc.) unchanged (deploys cleanly)
- [x] Verify `Network` metadata schema unchanged (PRM, payments webhook site) (deploys cleanly via `prepare_prm` sub-flow with `emailSenderAddress` patch)
- [x] Verify `ExperienceBundle` schema unchanged for PRM bundle (deploys cleanly)
- [x] Check `PaymentsSettings` metadata type for 262 changes (no schema change observed in deploy)
- [ ] Review `SecuritySettings.sessionSettings` — investigate correct API for `enableSeparateSalesforceAndSiteLogin` (issue #76, still open)

### Profiles & Permission Sets
- [x] Verify profile metadata schema unchanged at 67.0 (deploys cleanly)
- [x] Check for new permission set API fields in 262 (none required for current PSL/PSG assignments)

### Layouts
- [x] Verify layout metadata schema unchanged (deploys cleanly)
- [x] Check for new layout components available in 262 (no immediate capability adoption needed)

### LWC & Aura
- [x] Verify `rlmDocPreview` LWC (`post_docgen`) is compatible with 262 (deploys cleanly)

### AppMenu / App Launcher
- [x] Verify `AppMenu` metadata type unchanged for `post_tso_appmenu` (deploys cleanly)

---

## 5. Data Plan Validation

Run SFDMU v5 dataset compliance check after any schema-driven updates.

**Schema delta confirmed as remediation-free** via `scripts/erd/schema_diff/diff_schemas.py --impact` on 2026-05-27. The delta is **field-level additive** (45 fields added, 0 removed, 0 type changes, 2 polymorphic-reference targets expanded) with **value-level picklist deltas** of 243 added and 62 removed. The 62 removals break down as:

- **44 IANA TimeZone renames** across 4 datetime-zone fields (`BillingBatchScheduler.TimeZone`, `OrderItem.EstimatedDeliveryTimeZone`, `QuoteLineItem.StartEndTimeZone`, `SequencePolicy.TimeZone`) — Salesforce kept up with the upstream tz database (e.g. `America/Catamarca` → `America/Argentina/Catamarca`, `Europe/Kiev` → `Europe/Kyiv`). None of these objects ships CSV data in the repo (they're all SOQL-loaded or unused in maintained plans).
- **10 unused industry `UsageType` values** (`InsuranceRuleAction`, `StageManagement`) cleaned off 5 fulfillment objects (`FulfillmentPlan`, `FulfillmentStep`, `FulfillmentStepDefinition`/`Group`, `FulfillmentTaskAssignmentRule`, `ProductFulfillmentScenario`). The maintained `q3-dro` and `qb-dro` plans use only `Fulfillment` for these fields.
- **3 `FlowOrchestration` values** (`AgxScreenData`, `ScheduledHighScale`) — object not maintained in any plan.
- **2 `ValTfrmGrp` primitive-type values** (`Picklist` removed from `DestinationPrimitiveType`/`SourcePrimitiveType`) — the qb-dro `ValTfrmGrp.csv` does not populate either column.
- **1 `ObjectStateDefinition.ReferenceObject` value** (`AiTestConvPersonaDef`) — the qb-clm CSV uses only `Contract`.
- **2 misc removals** on objects with no CSV column for the affected field.

Every removed value was cross-referenced against the committed CSV under `datasets/sfdmu/{qb,q3,mfg}/**` and **zero maintained-plan rows reference any removed value**. Nine objects with deltas (`EmailTemplate`, `FulfillmentStepDefinition`/`Group`, `FulfillmentTaskAssignmentRule`, `ObjectStateDefinition`, `OmniProcessElement`, `ProductFulfillmentScenario`, `ProductRampSegment`, `ValTfrmGrp`) appear in maintained plans per `--impact`, but no plan changes are required: additive fields can't break loads, and the removed picklist values aren't in use. Full machine-readable details in `scripts/erd/schema_diff/260-vs-262-diff.{md,json}`.

- [x] Run `python scripts/validate_sfdmu_v5_datasets.py` — zero violations
- [x] Verify `qb-pcm` plan loads cleanly on 262 scratch org (`rlm-base__ent-sb0`)
- [x] Verify `qb-pricing` plan (price books, adjustments, tiers)
- [x] Verify `qb-billing` plan (billing policies, treatments, payment terms)
- [x] Verify `qb-tax` plan (tax policies and treatments)
- [x] Verify `qb-rating` plan (PUR, PURP, PUG — including the activation-order fix in `activateRatingRecords.apex` step 2.5a for #262-4)
- [x] Verify `qb-rates` plan (rate cards, entries, adjustment tiers — including REST Composite shift in `tasks/rlm_activate_rates.py` for #262-2)
- [x] Verify `qb-clm` plan (contract lifecycle)
- [x] Verify `qb-dro` plan (dynamic revenue orchestration)
- [x] Verify `qb-guidedselling` plan
- [x] Verify `qb-approvals` plan (approval alert content defs, email templates)
- [x] Verify `qb-transactionprocessingtypes` plan
- [x] Verify `mfg/*` plans
- [x] Verify `q3/*` plans

---

## 6. Full Build Verification

- [x] Run `cci flow run prepare_rlm_org` end-to-end on a 262 scratch org — full build confirmed successful
- [x] Verify all 28 flow steps pass (build succeeded against `rlm-base__ent-sb0`)
- [x] Verify `prepare_payments` sub-flow succeeds
- [x] Verify `prepare_prm` sub-flow succeeds (when `prm=true`)
- [x] Verify `prepare_approvals` sub-flow succeeds (when `approvals=true`)
- [x] Verify Robot Framework tasks pass — `enable_analytics_replication` rewritten for 262 (see Known Issues #262-1)
- [ ] Trigger GitHub Actions workflow (`prepare-rlm-org.yml`) on `262` branch (final remote-build verification — pending)

---

## 7. Feature Flag Review

Review `project__custom__*` flags in `cumulusci.yml` against 262 capabilities.

- [x] Confirm existing flags are still relevant in 262 (all 36 flags exercised via `prepare_rlm_org` build)
- [x] Evaluate any new 262 Revenue Cloud capabilities that warrant a new feature flag (none required — schema delta is purely additive at field level; new entities like `CaseServiceProcessExtension`, `FulfillmentAssetStatePeriod` are not in any current SFDMU plan and don't need flags yet)
- [x] Check if any flags can be retired (none — all flags still gate distinct feature sets in 262)

---

## 8. Known Open Items

| # | Item | Status |
|---|------|--------|
| #76 | `enableSeparateSalesforceAndSiteLogin` — correct metadata API mechanism unknown; Security.settings-meta.xml approach invalid | Open |
| — | Dev Hub configuration for 262 | Pending |
| #262-1 | **`InsightsSetupSettings` VF page removed** — Analytics Setup VF iframe (`waveSetupSettings.apexp`) removed in 262. Old robot test failed with "Analytics Settings VF iframe not found". **Fixed:** `enable_analytics.robot` and `AnalyticsSetupHelper.py` rewritten to click "Enable CRM Analytics" on `/lightning/setup/InsightsSetupGettingStarted/home`. Full CRM Analytics enablement (not the lightweight Data Sync toggle) is now required. `enableAnalytics` is not a valid `AnalyticsSettings` metadata field in v67 — robot/UI approach is the only path. | Resolved |
| #262-2 | **`RateCardEntry` DML via SOAP/Apex Execute Anonymous raises `UNKNOWN_EXCEPTION` (500)** — Platform regression in 262. Both `AnonymousApexTask` and `sf apex run` against `RateCardEntry` fail. REST API works correctly. **Fixed:** `activate_rates` task replaced with new `tasks/rlm_activate_rates.py` Python class using REST Composite API (25 records per request). | Resolved |
| #262-3 | **`RateCard.Status` claim misattributed** — Original note said the `Status` field was removed from `RateCard` in 262. Cross-validated 2026-05-27 via Core source diff (`core-260-public@p4/260-patch` vs `core-262-public@p4/262-patch`) AND scratch org diff (`ent-r1` 260 vs `rlm-base__ent-sb0` 262): `RateCard.entity.xml` does NOT declare a `Status` flexField in either release. There is no `RateCardStatus.java` enum. The `Status` field is on `RateCardEntry` (slot=10, `enum=RateCardEntryStatus`, `minApiVersion=254`, identical in both releases). `activateRatingRecords.apex` correctly references only `RateCardEntry.Status`, which is what was always intended. The original failure mode that triggered this note may have been a different field path. | Resolved (no change needed in current scripts; note revised to reflect schema reality) |
| #262-4 | **PUR idempotency — "effective period overlaps" on second run** — In 262, the platform enforces overlap validation when activating `ProductUsageResource` records that share the same Product+UsageResource with overlapping effective dates. On a second `prepare_rating` run, SFDMU `deleteOldData: true` cannot delete Active PURs, so new Draft PURs are inserted alongside existing Active ones. If those Draft PURs have children (PUGs/PURPs), step 2.5 in `activateRatingRecords.apex` cannot delete them. **Fixed:** Added step 2.5a to `activateRatingRecords.apex` — deletes Draft PUG/PURP children of identified duplicate Draft PURs first, then refreshes `purIdsWithChildren` so the main deletion loop proceeds. | Resolved |

---

## References

- [Salesforce Release Notes — Summer '26](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)
- [Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)
- [Revenue Cloud Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/)
- [SFDMU v5 Notes](../references/sfdmu-composite-key-optimizations.md)
