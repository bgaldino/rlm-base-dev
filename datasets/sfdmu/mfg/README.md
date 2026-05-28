# Manufacturing (MFG) SFDMU Data Plans

This directory holds SFDMU v5 data plans for the Manufacturing data shape, following the same conventions as the QuantumBit shape under `datasets/sfdmu/qb/en-US/`.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Data Plans](#data-plans)
- [Load Order](#load-order)
- [Feature Flags](#feature-flags)
- [Extract and Delete Tasks](#extract-and-delete-tasks)
- [Multi-Pass Plans](#multi-pass-plans)

---

## Directory Structure

```
datasets/sfdmu/mfg/
└── en-US/
    ├── mfg-pcm/            # Product Catalog Management seed data
    ├── mfg-pricing/        # Pricing records (pricebooks, adjustments, cost books)
    ├── mfg-dro/            # Digital Revenue Operations fulfillment rules
    ├── mfg-billing/        # Billing entities (LegalEntity, BillingPolicy, GL accounts)
    ├── mfg-tax/            # Tax entities (TaxPolicy, TaxTreatment)
    ├── mfg-guidedselling/  # Guided Selling assessment questions and OmniScript config
    ├── mfg-rebates/        # Rebate programs, members, and payout periods
    ├── mfg-aaf/            # Advanced Account Forecasting sets and facts
    └── mfg-configflow/     # Product configuration flow assignments (RenderDraw)
```

Each plan directory contains an `export.json`, one CSV per object, and `source/` / `target/` sub-directories used for post-processing and idempotency checking.

---

## Data Plans

### mfg-pcm

**Purpose:** Core Manufacturing product catalog — products, categories, classifications, attributes, selling models, and component relationships. This is the foundation plan; all other plans that reference `Product2` depend on it loading first.

**CCI task:** `insert_badger_pcm_data`
**Feature flags:** `badger`
**Path anchor:** `*badger_product_dataset`

| Object | Notes |
|--------|-------|
| `AttributePicklist` | Picklist attribute definitions |
| `AttributePicklistValue` | Picklist value entries |
| `UnitOfMeasureClass` | Unit of measure class groupings |
| `UnitOfMeasure` | Unit of measure records |
| `AttributeDefinition` | Attribute definitions |
| `AttributeCategory` | Attribute category groupings |
| `AttributeCategoryAttribute` | Category ↔ attribute links |
| `ProductClassification` | Product classification types |
| `ProductClassificationAttr` | Classification ↔ attribute links |
| `Product2` | All Manufacturing products |
| `ProductAttributeDefinition` | Product ↔ attribute assignments |
| `ProductSellingModel` | Selling models (one-time, evergreen, term) |
| `ProrationPolicy` | Proration policy definitions |
| `ProductSellingModelOption` | Product ↔ selling model options |
| `ProductRampSegment` | Ramp segment definitions |
| `ProductRelationshipType` | Relationship type definitions |
| `ProductComponentGroup` | Component group definitions |
| `ProductRelatedComponent` | BOM / component relationships |
| `ProductComponentGrpOverride` | Component group overrides |
| `ProductRelComponentOverride` | Component relationship overrides |
| `ProductCatalog` | MFG product catalog |
| `ProductCategory` | Category hierarchy |
| `ProductCategoryProduct` | Category ↔ Product assignments |
| `ProductQualification` | Product qualification rules |
| `ProductDisqualification` | Product disqualification rules |
| `ProductCategoryDisqual` | Category-level disqualification rules |
| `ProductCategoryQualification` | Category-level qualification rules |
| `ProdtAttrScope` | Attribute scope rules |

---

### mfg-pricing

**Purpose:** Pricing records — price adjustment schedules, tiers, pricebook entries, cost books, and attribute-based adjustments. Depends on `mfg-pcm` (Product2 must exist). The `deploy_mfg_pricing_procedure` task injects live `PriceAdjustmentSchedule` IDs into the ExpressionSetDefinition after this plan loads.

**CCI task:** `insert_badger_pricing_data`
**Feature flags:** `badger`
**Path anchor:** `*badger_pricing_dataset`
**Delete task:** `delete_badger_pricing_data`

| Object | Notes |
|--------|-------|
| `CurrencyType` | Active currency definitions |
| `ProrationPolicy` | Proration policy reference (upsert) |
| `ProductSellingModel` | Selling model reference (upsert) |
| `AttributeDefinition` | Attribute reference (upsert) |
| `Product2` | Product reference (upsert) |
| `CostBook` | Cost book definitions |
| `Pricebook2` | Standard and custom pricebooks |
| `PriceAdjustmentTier` | Tier breakpoints per schedule |
| `PriceAdjustmentSchedule` | Volume, attribute, and bundle adjustment schedules |
| `AttributeBasedAdjRule` | Attribute-based adjustment rule conditions |
| `AttributeAdjustmentCondition` | Individual adjustment conditions |
| `AttributeBasedAdjustment` | Attribute-based price adjustment rules |
| `BundleBasedAdjustment` | Bundle-based price adjustment rules |
| `PricebookEntry` | Product ↔ pricebook price entries |
| `PricebookEntryDerivedPrice` | Derived price overrides |
| `CostBookEntry` | Cost entries per product |

---

### mfg-dro

**Purpose:** Digital Revenue Operations (DRO) fulfillment decomposition rules and workspace definitions. Depends on `mfg-pcm` (Product2 must exist). After loading, `update_product_fulfillment_decomp_rules` runs to link rules to live Product2 IDs.

**CCI task:** `insert_badger_dro_data`
**Feature flags:** `badger`
**Path anchor:** `*badger_dro_dataset`

| Object | Notes |
|--------|-------|
| `User` | Running user reference for workspace ownership |
| `Product2` | Product reference (upsert by Name) |
| `IntegrationProviderDef` | Integration provider definitions |
| `FulfillmentWorkspace` | Workspace definitions |
| `FulfillmentWorkspaceItem` | Items within each workspace |
| `FulfillmentStepDefinitionGroup` | Step definition groups |
| `FulfillmentStepDefinition` | Individual fulfillment step definitions |
| `FulfillmentStepDependencyDef` | Step dependency ordering rules |
| `FulfillmentStepJeopardyRule` | Jeopardy rules per step |
| `FulfillmentFalloutRule` | Fallout handling rules |
| `ProductFulfillmentScenario` | Scenario definitions |
| `ProductFulfillmentDecompRule` | Product ↔ fulfillment decomposition rules |

---

### mfg-billing

**Purpose:** Manufacturing billing configuration — accounting periods, legal entity, billing policies, treatments, general ledger accounts, and payment terms. Conditionally loaded when `billing=true`. Uses a 3-pass `objectSets` pattern to handle activation sequencing.

**CCI task:** `insert_mfg_billing_data`
**Feature flags:** `badger` + `billing`
**Path anchor:** `*badger_billing_dataset`
**Multi-pass:** Yes — 3 object sets (see [Multi-Pass Plans](#multi-pass-plans))

| Object | Notes |
|--------|-------|
| `AccountingPeriod` | Accounting period records |
| `LegalEntity` | MFG legal entity |
| `LegalEntyAccountingPeriod` | Legal entity ↔ period links |
| `PaymentTerm` | Payment term definitions |
| `PaymentTermItem` | Individual payment term items |
| `BillingPolicy` | Billing policy records |
| `BillingTreatment` | Billing treatment definitions |
| `BillingTreatmentItem` | Treatment line items |
| `Product2` | Product ↔ billing policy assignments |
| `GeneralLedgerAccount` | GL account records |
| `GeneralLedgerAcctAsgntRule` | GL assignment rules |

After loading, `activate_billing_records` and `deploy_post_billing` finalize the billing configuration.

---

### mfg-tax

**Purpose:** Manufacturing tax configuration — tax engine, tax policies, and product tax policy assignments. Conditionally loaded when `tax=true`. Uses a 2-pass `objectSets` pattern to handle Draft → Active sequencing.

**CCI task:** `insert_mfg_tax_data`
**Feature flags:** `badger` + `tax`
**Path anchor:** `*badger_tax_dataset`
**Multi-pass:** Yes — 2 object sets (see [Multi-Pass Plans](#multi-pass-plans))

| Object | Notes |
|--------|-------|
| `LegalEntity` | MFG legal entity reference (upsert) |
| `TaxEngine` | Tax engine definition |
| `TaxPolicy` | Tax policy records |
| `TaxTreatment` | Tax treatment records |
| `Product2` | Product ↔ TaxPolicy assignments (update) |

After loading, `activate_tax_records` completes the activation sequence.

---

### mfg-guidedselling

**Purpose:** Guided Selling seed data — assessment questions, question sets, OmniScript process records, and configuration assignments. The metadata (AssessmentQuestion XML, OmniScript definitions, ProductDiscovery settings) is deployed earlier by `deploy_mfg_guided_selling`; this plan loads the runtime configuration records.

**CCI task:** `insert_badger_guidedselling_data`
**Feature flags:** `badger` + `mfg_guidedselling`
**Path anchor:** `*badger_guidedselling_dataset`

| Object | Notes |
|--------|-------|
| `AssessmentQuestionConfig` | Assessment question configuration records |
| `AssessmentQuestionSetConfig` | Assessment question set configuration |
| `AssessmentQuestion` | Assessment question records |
| `AssessmentQuestionSet` | Assessment question set records |
| `AssessmentQuestionAssignment` | Question ↔ set assignment records |
| `AssessmentQuestionVersion` | Assessment question version records |
| `OmniProcess` | GuidedSelling OmniScript process records |
| `OmniProcessElement` | OmniScript element definitions |
| `OmniScriptConfig` | OmniScript configuration records |
| `OmniProcessAsmtQuestionVer` | OmniScript ↔ assessment question version links |

---

### mfg-rebates

**Purpose:** Rebate program seed data — rebate types, programs, members, payout periods, and batch calculation job definitions.

**CCI task:** `insert_badger_rebates_data`
**Feature flags:** `badger` + `mfg_rebates`
**Path anchor:** `*badger_rebates_dataset`

| Object | Notes |
|--------|-------|
| `BatchCalcJobDefinition` | Aggregate-by-member rebate calculation job |
| `Account` | Account records referenced by rebate members |
| `RebateProgram` | Rebate program records |
| `RebateProgramPayoutPeriod` | Payout period definitions |
| `RebateProgramMember` | Account ↔ rebate program memberships |
| `ProgramRebateType` | Rebate type definitions |
| `ProgramRebateTypeBenefit` | Benefit rules per rebate type |

---

### mfg-aaf

**Purpose:** Advanced Account Forecasting seed data — forecast sets, facts, and partner assignments. The metadata (custom fields, dimension sources, forecast set configuration) is deployed earlier by `prepare_mfg_aaf`; this plan loads the forecast data itself.

**CCI task:** `insert_badger_aaf_data`
**Feature flags:** `badger` + `mfg_aaf`
**Path anchor:** `*badger_aaf_dataset`
**Delete task:** `delete_badger_aaf_data`
**Extract tasks:** `extract_mfg_aaf_data` / `extract_mfg_aaf_with_category_fix`

| Object | Notes |
|--------|-------|
| `Account` | Account records referenced by forecast sets |
| `Product2` | Product reference (upsert by Name) |
| `ProductCategory` | Product category reference |
| `Period` | Fiscal period records |
| `AdvAccountForecastSet` | Forecast set definitions |
| `AdvAcctForecastSetPartner` | Forecast set ↔ account partner links |
| `AdvAccountForecastFact` | Individual forecast fact records |

---

### mfg-configflow

**Purpose:** Product configuration flow assignments for 3D Visualization (RenderDraw). Maps Manufacturing products to their RenderDraw configuration flows. Deployed as part of `prepare_mfg_visuals`.

**CCI task:** `insert_mfg_configflow_data`
**Feature flags:** `badger` + `mfg_visuals`
**Path anchor:** `*badger_configflow_dataset`

| Object | Notes |
|--------|-------|
| `ProductConfigurationFlow` | RenderDraw configuration flow definitions |
| `ProductConfigFlowAssignment` | Product ↔ configuration flow assignments |

---

## Load Order

Plans must load in the following sequence due to object dependencies. This order is enforced by the `prepare_mfg_data` and sub-feature flows within `prepare_manufacturing`.

```
Step  Plan              CCI Task / Flow                      Gate
────  ────────────────  ───────────────────────────────────  ─────────────────────────
 1    mfg-pcm           insert_badger_pcm_data               badger
 2    mfg-pricing       insert_badger_pricing_data           badger
 3    mfg-dro           insert_badger_dro_data               badger
 4    (CML models)      import_mfg_cml flow                  badger
 5    mfg-tax           prepare_mfg_tax flow                 badger + tax
 6    mfg-billing       prepare_mfg_billing flow             badger + billing
 7    mfg-guidedselling insert_badger_guidedselling_data     badger + mfg_guidedselling
 8    mfg-rebates       insert_badger_rebates_data           badger + mfg_rebates
 9    mfg-aaf           insert_badger_aaf_data               badger + mfg_aaf
10    mfg-configflow    insert_mfg_configflow_data           badger + mfg_visuals
```

Steps 1–6 run within `prepare_mfg_data` (step 7 of `prepare_manufacturing`). Steps 7–10 run in their respective sub-feature flows later in `prepare_manufacturing`.

**Key dependencies:**
- `mfg-pcm` must load before all other plans — all plans reference `Product2` by Name
- `mfg-pricing` must load before `deploy_mfg_pricing_procedure` (which injects live `PriceAdjustmentSchedule` IDs into the ExpressionSetDefinition)
- `mfg-dro` must load before `update_product_fulfillment_decomp_rules`
- `mfg-tax` and `mfg-billing` both reference `LegalEntity` — their load order relative to each other is independent
- `mfg-aaf` metadata (`deploy_mfg_aaf_fields`, `deploy_mfg_aaf_dim_source`, `deploy_mfg_aaf_forecast_set`) must deploy before `insert_badger_aaf_data`

---

## Feature Flags

| Flag | Default | Plans / tasks gated |
|------|---------|---------------------|
| `badger` | `true` | All MFG plans and deploy tasks |
| `badger_data` | `true` | Data insertion tasks within flows |
| `billing` | `true` | `mfg-billing` |
| `tax` | `true` | `mfg-tax` |
| `mfg_guidedselling` | `true` | `mfg-guidedselling` |
| `mfg_rebates` | `true` | `mfg-rebates` |
| `mfg_aaf` | `true` | `mfg-aaf` |
| `mfg_visuals` | `true` | `mfg-configflow` |

---

## Extract and Delete Tasks

### Extract

| Task | Plan | Notes |
|------|------|-------|
| `extract_mfg_aaf_data` | `mfg-aaf` | Extracts AAF forecast data from a source org |
| `fix_mfg_aaf_category_extraction` | `mfg-aaf` | Post-processes the extracted AAF CSV to fix `Category__c` picklist values; run after `extract_mfg_aaf_data` |
| `extract_mfg_aaf_with_category_fix` | `mfg-aaf` | Convenience flow: runs `extract_mfg_aaf_data` then `fix_mfg_aaf_category_extraction` in sequence |

### Delete

| Task | Plan | What gets deleted |
|------|------|-------------------|
| `delete_badger_aaf_data` | `mfg-aaf` | Deletes `AdvAccountForecastFact` and `AdvAcctForecastSetPartner` in reverse plan order; run before `insert_badger_aaf_data` for a clean reload |
| `delete_badger_pricing_data` | `mfg-pricing` | Deletes all Insert-operation pricing records: `PricebookEntryDerivedPrice`, `PricebookEntry`, `BundleBasedAdjustment`, `AttributeBasedAdjustment`, `AttributeAdjustmentCondition`, `PriceAdjustmentTier` |

---

## Multi-Pass Plans

Three plans use `objectSets` to enforce a multi-pass insert/update pattern required by activation sequencing constraints in Salesforce billing and tax objects.

### mfg-billing (3 passes)

| Pass | Objects | Purpose |
|------|---------|---------|
| Set 1 | `AccountingPeriod`, `LegalEntity`, `LegalEntyAccountingPeriod`, `PaymentTerm`, `PaymentTermItem`, `BillingPolicy`, `BillingTreatment`, `BillingTreatmentItem`, `Product2`, `GeneralLedgerAccount`, `GeneralLedgerAcctAsgntRule` | Create all records in Draft status |
| Set 2 | `BillingTreatmentItem` | Re-insert treatment items after treatments exist (resolves parent ordering) |
| Set 3 | `BillingTreatment`, `BillingPolicy` | Activate treatments and policies |

After loading, `activate_billing_records` and `deploy_post_billing` finalize the billing configuration.

### mfg-tax (2 passes)

| Pass | Objects | Purpose |
|------|---------|---------|
| Set 1 | `LegalEntity`, `TaxEngine`, `TaxPolicy`, `TaxTreatment`, `Product2` | Create all records in Draft status; assign `TaxPolicy` to products |
| Set 2 | `TaxTreatment`, `TaxPolicy` | Activate treatments and policies; set `DefaultTaxTreatmentId` on `TaxPolicy` |

After loading, `activate_tax_records` completes the activation sequence.
