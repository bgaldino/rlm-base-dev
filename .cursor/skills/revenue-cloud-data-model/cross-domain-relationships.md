# Cross-Domain Relationships

Complete map of foreign key relationships that span Revenue Cloud domains. Derived from `erd-data.json`, mermaid diagrams, and SFDMU data plan analysis.

## Product2 as Universal Hub

Product2 (PCM) is referenced by objects in every other domain:

| Target Object | Field | Domain |
|--------------|-------|--------|
| PriceBookEntry | Product2Id | Pricing |
| PriceAdjustmentTier | Product2Id | Pricing |
| PriceBookEntryDerivedPrice | ProductId, ContributingProductId | Pricing |
| AttributeAdjustmentCondition | ProductId | Pricing |
| BundleBasedAdjustment | ProductId, ParentProductId, RootBundleId | Pricing |
| RateCardEntry | ProductId | Rates |
| ProductConfigurationFlow | ReferenceObjectId | Configurator |
| ProductConfigurationRule | ProductId | Configurator |
| QuoteLineItem | Product2Id | Transactions |
| OrderItem | Product2Id | Transactions |
| Asset | Product2Id | Transactions |
| FulfillmentOrderLineItem | Product2Id | Transactions |
| InvoiceLine | Product2Id | Billing |
| ProductUsageResource | ProductId | Usage |
| ProductFulfillmentDecompRule | SourceProductId, DestinationProductId | DRO |
| ProductFulfillmentScenario | ProductId | DRO |
| UsageResource | UsageDefinitionProductId | Usage |

Product2 also carries direct policy FKs set by billing/tax data plans:
- `Product2.BillingPolicyId` → BillingPolicy (Billing)
- `Product2.TaxPolicyId` → TaxPolicy (Billing)

## ProductSellingModel Cross-Domain Links

ProductSellingModel (Pricing) is referenced across Pricing, Transactions, Rates, and Usage:

| Target Object | Field | Domain |
|--------------|-------|--------|
| PriceBookEntry | ProductSellingModelId | Pricing |
| PriceAdjustmentTier | ProductSellingModelId | Pricing |
| PriceBookEntryDerivedPrice | ProductSellingModelId | Pricing |
| ContractItemPrice | ProductSellingModelId | Pricing |
| QuoteLineItem | ProductSellingModelId | Transactions |
| OrderItem | ProductSellingModelId | Transactions |
| RateCardEntry | ProductSellingModelId | Rates |
| ProductUsageGrant | ProductSellingModelId | Usage |

## Account as Transaction Hub

Account (Transactions) is referenced by most transactional and billing objects:

| Target Object | Field | Domain |
|--------------|-------|--------|
| Contact | AccountId | Transactions |
| Quote | AccountId | Transactions |
| Order | AccountId | Transactions |
| Contract | AccountId | Transactions |
| Asset | AccountId | Transactions |
| FulfillmentOrder | AccountId | DRO |
| BillingAccount | AccountId | Billing |
| BillingSchedule | AccountId | Billing |
| Invoice | AccountId | Billing |
| CreditMemo | AccountId | Billing |
| Payment | AccountId | Billing |

## PriceBook2 Cross-Domain Links

| Target Object | Field | Domain |
|--------------|-------|--------|
| PriceBookEntry | Pricebook2Id | Pricing |
| Order | Pricebook2Id | Transactions |
| Quote | Pricebook2Id | Transactions |
| PriceBookRateCard | PriceBookId | Rates |

## UsageResource Cross-Domain Links

UsageResource (Usage) bridges Usage, Rates, and Billing:

| Target Object | Field | Domain |
|--------------|-------|--------|
| ProductUsageResource | UsageResourceId | Usage |
| ProductUsageGrant | UsageResourceId | Usage |
| TransactionJournal | UsageResourceId | Usage |
| UsageSummary | UsageResourceId | Usage |
| RateCardEntry | UsageResourceId | Rates |
| RateCard | UsageResourceId | Rates |

## LegalEntity Cross-Domain Links

LegalEntity (Billing) anchors tax, GL, and invoicing:

| Target Object | Field | Domain |
|--------------|-------|--------|
| TaxTreatment | LegalEntityId | Billing |
| TaxRate | LegalEntityId | Billing |
| TaxPolicy | LegalEntityId | Billing |
| BillingScheduleGroup | LegalEntityId | Billing |
| GeneralLedgerAccount | LegalEntityId | Billing |
| GeneralLedgerAcctAsgntRule | LegalEntityId | Billing |
| LegalEntyAccountingPeriod | LegalEntityId | Billing |
| Invoice | LegalEntityId | Billing |
| InvoiceLine | LegalEntityId | Billing |
| CreditMemo | LegalEntityId | Billing |
| CreditMemoLineTax | LegalEntityId | Billing |
| DebitMemoLine | LegalEntityId | Billing |
| PaymentLineInvoice | LegalEntityId | Billing |

## Order → Billing Bridge

Order (Transactions) connects to Billing via:

| Target Object | Field | Domain |
|--------------|-------|--------|
| BillingSchedule | ReferenceEntityId | Billing |
| Invoice | ReferenceEntityId | Billing |
| CreditMemo | ReferenceEntityId | Billing |
| FulfillmentOrder | OrderId | DRO |

## Quote → Order → Asset Chain

The full lifecycle chain with cross-object references:

```
Quote.AccountId → Account
QuoteLineItem.QuoteId → Quote
QuoteLineItem.Product2Id → Product2
QuoteLineItem.PricebookEntryId → PriceBookEntry
QuoteLineItem.ProductSellingModelId → ProductSellingModel

Order.QuoteId → Quote
Order.AccountId → Account
Order.ContractId → Contract
Order.Pricebook2Id → PriceBook2

OrderItem.OrderId → Order
OrderItem.QuoteLineItemId → QuoteLineItem
OrderItem.Product2Id → Product2
OrderItem.OriginalOrderItemId → OrderItem (amendments)

Asset.Product2Id → Product2
Asset.AccountId → Account
Asset.ParentId → Asset (bundle hierarchy)

AssetAction.AssetId → Asset
AssetActionSource.AssetActionId → AssetAction
AssetActionSource.OrderItemId → OrderItem
```

## Fulfillment Bridge (DRO ↔ Transactions)

```
FulfillmentOrder.OrderId → Order
FulfillmentOrder.AccountId → Account
FulfillmentOrderLineItem.FulfillmentOrderId → FulfillmentOrder
FulfillmentOrderLineItem.OrderItemId → OrderItem
FulfillmentOrderLineItem.Product2Id → Product2
```

## Data Plan Load Order (Dependency Chain)

```
scratch_data (Account, Contact)
    └→ qb-pcm (Product2, attributes, bundles, categories — ROOT)
        ├→ qb-pricing (PriceBook2, PriceBookEntry, adjustments)
        ├→ qb-billing (BillingPolicy, treatments, PaymentTerm, LegalEntity)
        │   └→ qb-accounting (GL accounts and rules)
        ├→ qb-tax (TaxPolicy, TaxTreatment, TaxEngine)
        ├→ qb-rating (UsageResource, PUR, PURP, PUG)
        │   └→ qb-rates (RateCard, RateCardEntry, RABT) — MUST follow qb-rating
        ├→ qb-dro (fulfillment step definitions, decomp rules)
        ├→ qb-clm (contract lifecycle objects)
        ├→ qb-guidedselling (OmniScript assessment questions)
        ├→ qb-product-images (Product2 DisplayUrl)
        ├→ qb-prm (Partner accounts, channel programs)
        ├→ qb-approvals (approval alert content)
        └→ qb-transactionprocessingtypes (standalone)
```
