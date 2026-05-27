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

Revenue Cloud v67.0 (Summer '26 / Release 262) — **263 objects, 4,190 platform fields, 674 relationships** across 9 domains.

The ERD reflects **canonical Revenue Cloud platform schema only**. Custom fields (any `__c` suffix, including project-deployed `RLM_*__c` and managed-package fields) are excluded by validation tooling so the schema stays platform-pure.

**Verified 2026-05-27 against:**
- 260 baseline scratch org `ent-r1` (Spring '26, API v66)
- 262 target scratch org `rlm-base__ent-sb0` (Summer '26, API v67)
- Core UDD source at `gitcore.soma.salesforce.com/core-2206/core-262-public@p4/262-patch`
- 127 entities individually verified against canonical entity XMLs

**260 → 262 delta:** 45 fields added, 0 removed, 0 type changes, 0 SFDMU plan impact. Full diff at `scripts/erd/schema_diff/260-vs-262-diff.md`.

**Common misconceptions resolved (DO NOT propagate):**
- The Revenue Cloud "PUG" entity is `ProductUsageGrant`, NOT `ProductUsageGroup` (which doesn't exist in core source)
- `RateCard.Status` does not exist in any Salesforce release. The Status field is on `RateCardEntry` (slot=10, identical 260 vs 262)
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

- `docs/erds/erd-data.json` — canonical machine-readable schema (263 objects, 4,190 fields, 674 relationships, custom fields excluded)
- `docs/erds/*.mermaid` — per-domain ERD diagrams
- `docs/erds/revenue-cloud-erd.html` — interactive force-directed graph viewer
- `docs/erds/validation-report.md` — most recent ERD vs org schema gap analysis
- `docs/erds/orphan-candidates-after-batch7.md` — final orphan classification report (38 explicitly-documented feature-gated/cross-cloud fields kept as informational)
- `scripts/erd/schema_diff/{260,262}-schema.json` — fresh-org schema snapshots for 260 and 262
- `scripts/erd/schema_diff/260-vs-262-diff.md` — verified release delta
- `.agents/artifacts/orphan-field-ownership.json` — per-entity ownership classification for 127 verified entities
