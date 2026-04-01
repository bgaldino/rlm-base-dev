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

Revenue Cloud v66.0 (Spring '26, API v260) — 263 objects, 4,919 fields across 9 domains.

## Quick Rules

1. Use `scripts/ai/query_erd.py` to query object details on demand.
2. Load per-domain files (e.g., `domains/pricing.md`) for detailed field/relationship info.
3. Cross-domain FKs are documented in `cross-domain-relationships.md`.
4. Product2 is the central object — most domains reference it.
5. Standard fields often have API names without `__c` suffix.

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

Use `scripts/ai/query_erd.py` for targeted lookups against the full 213-object schema:

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

- `docs/erds/erd-data.json` — complete machine-readable schema (213 objects, all fields and relationships)
- `docs/erds/*.mermaid` — per-domain ERD diagrams
- `docs/erds/revenue-cloud-erd.html` — interactive force-directed graph viewer
- `docs/erds/validation-report.md` — ERD vs org schema gap analysis
