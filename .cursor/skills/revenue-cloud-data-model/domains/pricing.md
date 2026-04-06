# Pricing Domain

14+ objects managing price books, price entries, adjustments, selling models, cost books, and derived pricing.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `PriceBook2` | Price book container | Name, IsStandard, CostBookId |
| `PriceBookEntry` | Price for a product+selling model in a price book | Product2Id, Pricebook2Id, ProductSellingModelId, UnitPrice, CurrencyIsoCode |
| `PriceAdjustmentSchedule` | Named adjustment schedule (discounts, surcharges) | Name, Pricebook2Id, CurrencyIsoCode, AdjustmentType |
| `PriceAdjustmentTier` | Tier within an adjustment schedule | PriceAdjustmentScheduleId, Product2Id, ProductSellingModelId, LowerBound, UpperBound |
| `ProductSellingModel` | Selling model type (One-Time, Evergreen, Term-Defined) | Name, SellingModelType |
| `ProductSellingModelOption` | Binds selling model to product with proration | Product2Id, ProductSellingModelId, ProrationPolicyId |
| `ProrationPolicy` | Proration rules | Name |
| `CostBook` | Cost book container | Name, IsDefault |
| `CostBookEntry` | Cost entry for a product | CostBookId, ProductId |
| `CurrencyType` | Active currencies | IsoCode |

## Attribute-Based Adjustments

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `AttributeBasedAdjRule` | Rule container for attribute-driven pricing | Name |
| `AttributeAdjustmentCondition` | Condition within an attribute adjustment rule | AttributeBasedAdjRuleId, AttributeDefinitionId, ProductId |
| `AttributeBasedAdjustment` | Adjustment linked to a rule and schedule | AttributeBasedAdjRuleId, PriceAdjustmentScheduleId, ProductId, ProductSellingModelId |

## Bundle and Derived Pricing

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `BundleBasedAdjustment` | Bundle-level adjustment | PriceAdjustmentScheduleId, ProductId, ParentProductId, RootBundleId |
| `PriceBookEntryDerivedPrice` | Derived/contributing price | PricebookId, PricebookEntryId, ProductId, ContributingProductId, ProductSellingModelId |

## Additional Pricing Objects

| Object | Purpose |
|--------|---------|
| `ContractItemPrice` | Price at contract-item level |
| `IndexRate` | Index-based rate data |
| `PriceRevisionPolicy` | Policy for price revisions |
| `PricingAPIExecution` | API execution logs |
| `PricingAdjBatchJob` / `PricingAdjBatchJobLog` | Batch adjustment processing |
| `PricingProcedureResolution` | Procedure plan resolution |
| `PricingProcessExecution` | Process execution tracking |
| `ProcedurePlanCriterion` | Criteria within procedure plans |
| `ProductPriceHistoryLog` | Price change audit trail |
| `ProductPriceRange` | Valid price ranges |
| `ProductSellingModelDataTranslation` | Translations for selling models |

## Key Relationships

```
PriceBook2 ← PriceBookEntry (Pricebook2Id)
Product2 ← PriceBookEntry (Product2Id)
ProductSellingModel ← PriceBookEntry (ProductSellingModelId)
PriceAdjustmentSchedule ← PriceAdjustmentTier (PriceAdjustmentScheduleId)
Product2 ← PriceAdjustmentTier (Product2Id)
ProductSellingModel ← PriceAdjustmentTier (ProductSellingModelId)
AttributeBasedAdjRule ← AttributeAdjustmentCondition (AttributeBasedAdjRuleId)
ProductSellingModel ← AttributeBasedAdjustment (Lookup)
ProductSellingModel ← PriceBookEntryDerivedPrice (ProductSellingModelId)
ProductSellingModel ← ProductSellingModelOption (ProductSellingModelId)
ProrationPolicy ← ProcedurePlanCriterion (ProrationPolicyId)
```

## SFDMU Data Plan: `qb-pricing`

16 objects across 1 pass with objectSets. Upstream: `qb-pcm` (Product2, PSM, ProrationPolicy, AttributeDefinition).

Key pattern: Most junction/adjustment objects use `Insert` + `deleteOldData: true` due to composite relationship-traversal externalIds (SFDMU v5 Bug 3).

Read-only references: ProductSellingModel, AttributeDefinition, Product2 (loaded by qb-pcm).
