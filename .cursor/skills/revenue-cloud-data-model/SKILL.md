---
name: revenue-cloud-data-model
description: >-
  Revenue Cloud (RLM) data model reference covering 263 objects across 9 domains.
  Use when working with Revenue Cloud objects, understanding object relationships,
  writing SOQL queries, building data plans, or answering questions about the
  RLM schema. Covers PCM, Pricing, Rates, Configurator, Transactions, DRO,
  Usage, Billing, and Approvals domains.
---

# Revenue Cloud Data Model

Revenue Cloud v68.0 (Winter '27 / Release 264) — **263 objects, 4,252 platform fields, 674 relationships** across 9 domains.

The ERD reflects **canonical Revenue Cloud platform schema only**. Custom fields (any `__c` suffix, including project-deployed `RLM_*__c` and managed-package fields) are excluded by validation tooling so the schema stays platform-pure.

**Verified 2026-08-15 against:**
- Two fresh `prepare_rlm_org` 264 scratch orgs — `rlm-base__264merged` and
  `rlm-base__264fresh` (Winter '27, API v68, `ent` shape). They agreed
  field-for-field (254 describable objects, 3,913 platform fields each), so no
  figure here rests on a single org.
- The committed 262 snapshot `scripts/erd/schema_diff/262-schema.json` as baseline —
  the same artifact the previous refresh was built from, and the same org shape, so
  the delta is not confounded by shape differences.
- Core UDD source and the 127-entity orphan classification carried forward from the
  262 pass (`.agents/artifacts/orphan-fields/`); not re-run for 264.

**262 → 264 delta:** **70 fields added, 8 removed**, 0 type changes, 1 polymorphic
reference-target change, 270 picklist values added and 18 removed, across 62 changed
objects. All 8 removals are in the usage domain, and **7 of the 8** are one coherent
change rather than attrition — 264 moved the usage policy bindings off the definition
and runtime objects and onto `ProductUsageResourcePolicy`, the
**product-and-resource-specific** binding site. The 8th,
`TransactionUsageEntitlement.DrawdownOrder`, is a separate change and is the row most
often got wrong — see the table below.

⚠ **PURP is the new binding site, not the only one.** `UsageResourcePolicy` still
carries the same four lookups (`RatingFrequencyPolicyId`,
`UsageAggregationPolicyId`, `UsageCommitmentPolicyId`, `UsageOveragePolicyId`) in a
264 org, bound at **resource** level rather than product-and-resource. Verified on
`rlm-base__264merged` and `rlm-base__264fresh`. When you need the policy that applies
to a specific product's use of a resource, read PURP; `UsageResourcePolicy` is the
resource-wide default.

| Removed in 264 | Where the binding lives now |
|---|---|
| `TransactionUsageEntitlement.ChargeForOverage`, `.RatingFrequencyPolicyId`, `.UsageAggregationPolicyId` | `ProductUsageResourcePolicy` → `UsageOveragePolicy` / `RatingFrequencyPolicy` / `UsageResourceBillingPolicy` |
| `TransactionUsageEntitlement.DrawdownOrder` | **Not on PURP** — PURP has no drawdown field. In 264 `DrawdownOrder` lives on `ProductUsageGrant` (design time) and on the per-transaction policy objects `QuotLineItmUsageRsrcPlcy`, `OrderItemUsageRsrcPlcy` and `BindingObjUsageRsrcPlcy` (runtime). The maintained rating plans already carry `ProductUsageGrant.DrawdownOrder`. |
| `UsageResource.UsageResourceBillingPolicyId` | `ProductUsageResourcePolicy.UsageAggregationPolicyId` |
| `RatingFrequencyPolicy.ProductId`, `.UsageResourceId` | `ProductUsageResourcePolicy.RatingFrequencyPolicyId` (the policy no longer knows its own product/resource) |
| `ProductUsageGrant.OverageChargeable` | `UsageOveragePolicy.OverageChargeable` via `ProductUsageResourcePolicy` |

Only **one** of the eight broke the 264 compile: `TransactionUsageEntitlement.ChargeForOverage`,
which `RLM_UsageUploaderController` read in two places, fixed in #365. #365 names the
other three `TransactionUsageEntitlement` removals alongside it and sources chargeability
from the replacement `UsageOveragePolicy.OverageChargeable`, so those were already known
there — what this diff adds for them is the schema record, not the discovery. Genuinely
first recorded here: `UsageResource.UsageResourceBillingPolicyId`, both
`RatingFrequencyPolicy` lookups, and the removal of `ProductUsageGrant.OverageChargeable`
(which #365 implied by reading from the policy instead, but never stated).
Both `RatingFrequencyPolicy` removals are still selected by the `qb-rating` and
`q3-rating` export queries — see #264-66. Full diff at
`scripts/erd/schema_diff/262-vs-264-diff.md`.

<details>
<summary>260 → 262 delta (previous refresh, kept for history)</summary>

**260 → 262 delta:** **Field-level additive** (45 fields added, 0 removed, 0 type changes, 2 polymorphic-reference targets expanded — e.g. `Invoice.ReferenceEntityId` now also accepts `Opportunity`/`Quote`) with **value-level picklist deltas** of 243 added and 62 removed. The 62 picklist removals are IANA TimeZone renames on datetime-zone fields plus cleanup of unused industry-specific `UsageType` values (`InsuranceRuleAction`, `StageManagement`) on fulfillment objects and a few miscellaneous values. Every removed value was cross-referenced against every CSV under `datasets/sfdmu/{qb,q3,mfg}/**` — **zero maintained-plan rows reference any removed value**. Nine objects with deltas appear in existing SFDMU plans per `scripts/erd/schema_diff/260-vs-262-diff.md` `--impact` output, but **no SFDMU remediation is required**: additive fields cannot break existing CSV imports, and the removed picklist values aren't in use. Full diff at `scripts/erd/schema_diff/260-vs-262-diff.md`.

</details>

**Common misconceptions resolved (DO NOT propagate):**
- The Revenue Cloud "PUG" entity is `ProductUsageGrant`, NOT `ProductUsageGroup` (which doesn't exist in core source)
- `RateCard.Status` does not exist in any Salesforce release. The Status field is on `RateCardEntry` (slot=10, identical across 260, 262 and 264)
- The 262 `RateCardEntry` SOAP DML failure (#262-2) is a runtime platform regression, not a schema change
- The 262 PUR overlap validation enforcement (#262-4) is runtime-gated, not a schema/validator code change

## Quick Rules

1. Use `scripts/ai/query_erd.py` to query object details on demand.
2. Load per-domain files (e.g., `domains/pricing.md`) for detailed field/relationship info.
3. Cross-domain FKs are documented in `cross-domain-relationships.md`.
4. Product2 is the central object — most domains reference it.
5. Standard fields often have API names without `__c` suffix.
6. To validate ERD against an org or refresh from a new release, see `.cursor/skills/schema-validation/SKILL.md`.
7. Custom fields are NOT in the ERD by design. To verify a `__c` field exists, query the org directly with `sf sobject describe`.

## Domain Overview

| Domain | Objects | Key Entities | Purpose |
|--------|---------|-------------|---------|
| **PCM** | 11 | Product2, ProductCategory, AttributeDefinition, ProductRelatedComponent | Product catalog: products, bundles, attributes, classifications, categories |
| **Pricing** | 14+ | PriceBook2, PriceBookEntry, PriceAdjustmentSchedule, ProductSellingModel | Price books, price entries, adjustments, selling models, proration |
| **Rate Management** | 15 | RateCard, RateCardEntry, RateAdjustmentByTier, PriceBookRateCard | Rate cards for usage-based pricing, tiered adjustments |
| **Configurator** | 4 | ProductConfigurationFlow, ProductConfigurationRule | Product configuration rules and flow assignments |
| **Transaction Mgmt** | 37 | Account, Quote, QuoteLineItem, Order, OrderItem, Asset, Contract | Core commercial objects: quote-to-cash lifecycle |
| **DRO** | 27 | FulfillmentPlan, FulfillmentStep, FulfillmentStepDefinition, ProductFulfillmentDecompRule | Dynamic Revenue Orchestration: fulfillment plans, decomposition, orchestration |
| **Usage Mgmt** | 22 | ProductUsageResource (PUR), ProductUsageResourcePolicy (PURP), ProductUsageGrant (PUG), UsageResource, UsageSummary | Usage entitlements, grants, rating, metering |
| **Billing** | 54 | BillingSchedule, Invoice, InvoiceLine, CreditMemo, Payment, TaxPolicy, LegalEntity | Invoicing, payments, tax, GL, collections |
| **Approvals** | 1 | ApprovalSubmission | Approval workflow submissions |

## Central Object: Product2

`Product2` is the hub of the entire Revenue Cloud data model. Nearly every domain connects back to it:

- **PCM**: ProductAttributeDefinition, ProductCategoryProduct, ProductRelatedComponent, ProductSellingModelOption all reference Product2
- **Pricing**: PriceBookEntry, PriceAdjustmentTier, BundleBasedAdjustment link products to price books and adjustments
- **Rates**: RateCardEntry links Product2 to rate cards via UsageResource
- **Configurator**: ProductConfigurationFlow and ProductConfigurationRule bind to Product2
- **Transactions**: QuoteLineItem, OrderItem, Asset, FulfillmentOrderLineItem, InvoiceLine all carry Product2Id
- **Usage**: ProductUsageResource (PUR) binds Product2 to UsageResource; ProductUsageGrant (PUG) grants usage entitlements per product
- **Billing**: Product2 carries BillingPolicyId, TaxPolicyId — set by billing/tax data plans
- **DRO**: ProductFulfillmentDecompRule and ProductFulfillmentScenario reference Product2

## Critical Cross-Domain Relationships

```
Account ←── Quote, Order, Contract, Asset, BillingAccount, FulfillmentOrder, Invoice, CreditMemo, Payment
Product2 ←── PriceBookEntry, QuoteLineItem, OrderItem, Asset, RateCardEntry, ProductUsageResource
PriceBook2 ←── PriceBookEntry, Order, Quote, PriceBookRateCard
ProductSellingModel ←── PriceBookEntry, QuoteLineItem, OrderItem, PriceAdjustmentTier, RateCardEntry, ProductUsageGrant
Order ←── OrderItem, FulfillmentOrder, BillingSchedule, Invoice (via ReferenceEntityId)
Quote ←── QuoteLineItem; Order.QuoteId links to originating Quote
OrderItem ←── FulfillmentOrderLineItem, AssetActionSource, OrderItemDetail, OrderItemAttribute
Asset ←── AssetAction, AssetStatePeriod, AssetRelationship, ProductUsageGrant
UsageResource ←── ProductUsageResource, RateCardEntry, RateCard, TransactionJournal, UsageSummary
LegalEntity ←── TaxTreatment, BillingScheduleGroup, GeneralLedgerAccount, Invoice, CreditMemo
BillingSchedule ←── InvoiceLine, BillingPeriodItem, BillingMilestonePlanItem
```

## Quote-to-Cash Flow (Object Lifecycle)

```
Product2 + PriceBookEntry
        ↓
    Quote → QuoteLineItem
        ↓ (Place Order)
    Order → OrderItem
        ↓ (Asset Creation)
    Asset → AssetStatePeriod, AssetAction → AssetActionSource
        ↓ (Fulfillment)
    FulfillmentOrder → FulfillmentOrderLineItem
    FulfillmentPlan → FulfillmentStep
        ↓ (Billing)
    BillingSchedule → BillingScheduleGroup
        ↓ (Invoice)
    Invoice → InvoiceLine → InvoiceLineTax
        ↓ (Payment)
    Payment → PaymentLineInvoice
```

## Key Abbreviations

| Abbreviation | Full Name | Domain |
|-------------|-----------|--------|
| PCM | Product Catalog Management | PCM |
| PSM | ProductSellingModel | Pricing |
| PSMO | ProductSellingModelOption | PCM/Pricing |
| PBE | PriceBookEntry | Pricing |
| PAS | PriceAdjustmentSchedule | Pricing |
| PAT | PriceAdjustmentTier | Pricing |
| PUR | ProductUsageResource | Usage |
| PURP | ProductUsageResourcePolicy | Usage |
| PUG | ProductUsageGrant | Usage |
| DRO | Dynamic Revenue Orchestration | DRO |
| RABT | RateAdjustmentByTier | Rates |
| BSG | BillingScheduleGroup | Billing |
| CLM | Contract Lifecycle Management | Transactions |
| CML | Constraint Markup Language | Configurator |

## Per-Domain Reference Files

For detailed object lists, fields, and relationships within each domain, read the appropriate reference file:

- **PCM**: [domains/pcm.md](domains/pcm.md)
- **Pricing**: [domains/pricing.md](domains/pricing.md)
- **Rate Management**: [domains/rates.md](domains/rates.md)
- **Configurator**: [domains/configurator.md](domains/configurator.md)
- **Transaction Management**: [domains/transactions.md](domains/transactions.md)
- **DRO**: [domains/dro.md](domains/dro.md)
- **Usage Management**: [domains/usage.md](domains/usage.md)
- **Billing**: [domains/billing.md](domains/billing.md)
- **Approvals**: [domains/approvals.md](domains/approvals.md)

For cross-domain FK mappings: [cross-domain-relationships.md](cross-domain-relationships.md)

## Querying the Data Model

Use `scripts/ai/query_erd.py` for targeted lookups against the full 263-object schema:

```bash
python scripts/ai/query_erd.py describe Product2         # fields, relationships, domain
python scripts/ai/query_erd.py relationships Product2     # all objects linked to/from Product2
python scripts/ai/query_erd.py domain Billing             # all objects in a domain
python scripts/ai/query_erd.py path Product2 Invoice      # relationship path between two objects
python scripts/ai/query_erd.py search "usage"             # fuzzy object/field search
python scripts/ai/query_erd.py stats                      # domain counts summary
```

For live org introspection, use the Salesforce DX MCP `run_soql_query` tool.

## Source Data

- `docs/erds/erd-data.json` — canonical machine-readable schema (263 objects, 4,252 fields, 674 relationships, custom fields excluded)
- `docs/erds/*.mermaid` — per-domain ERD diagrams
- `docs/erds/revenue-cloud-erd.html` — interactive force-directed graph viewer
- `docs/erds/validation-report.md` — most recent ERD vs org schema gap analysis; records the **expected** feature-gated baseline (9 objects unfindable in a default RLM scratch profile, **0** objects with field gaps, **58** ERD-side fields absent from a stock org — the feature-gated / cross-cloud set carried forward from the 262 pass). Use this file as the diff target for new validation runs — a clean refresh produces zero NEW gaps vs this baseline, not zero gaps absolute. The 262 baseline was 33 objects and 822 fields. The object figure fell to 0 because `--patch` added every field the org had; the field figure fell to 58 through deliberate removal (orphan-cleanup batches plus the 8 fields 264 retired), because `--patch` only ever adds and cannot reduce it. Trust the generated report over any count quoted in prose.
- `scripts/erd/schema_diff/{260,262,264}-schema.json` — fresh-org schema snapshots, **one committed per release**; 264 is the current one. Field metadata in these files is a **dict keyed by field name**, not a list — an accessor written for a list returns `None` for every field and any check built on it silently passes
- ⚠ **The second-org cross-validation is not a committed artifact.** The 264 capture is dual-sourced, but only one snapshot is kept; the second extraction is reproducible rather than stored, so the repo does not carry two 2 MB snapshots per release. To re-confirm, extract the ERD's own object list from a second org of the same release and diff:

  ```bash
  python scripts/erd/schema_diff/extract_schema.py --org <second-alias> \
      --output /tmp/crossval.json
  ```

  Pass **neither** `--objects` nor `--all-objects`: the default reads the object list
  straight from `erd-data.json`, which is what you want. `--all-objects` fails outright
  with `EXCEEDED_ID_LIMIT`, because `EntityDefinition` does not support `queryMore()`.
  Re-run on 2026-08-15 against `rlm-base__264fresh`: 254 objects / 3,913 fields,
  **0 field-set and 0 `referenceTo` differences** vs the committed capture. The 9
  objects reported missing are the documented feature-gated set, not a discrepancy.
  Full workflow in `.cursor/skills/schema-validation/SKILL.md`
- `scripts/erd/schema_diff/262-vs-264-diff.md` — current verified release delta (262 → 264), including the SFDMU plan `--impact` cross-reference
- `scripts/erd/schema_diff/260-vs-262-diff.md` — previous release delta, kept for history

Internal-only (not committed; intentionally git-ignored):
- `.agents/artifacts/orphan-fields/orphan-field-ownership.json` — per-entity ownership classification for 127 verified entities (used by the `orphan_batch_helper.py` workflow; not required to audit any claim in this skill).
- `docs/erds/orphan-candidates-after-batch*.md` — per-batch orphan classification reports produced by the cleanup workflow. The final outcome of the cleanup is already baked into `erd-data.json` and `validation-report.md`; the intermediate batch reports are local artifacts only.
