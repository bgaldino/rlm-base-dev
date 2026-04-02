# Transaction Management Domain

37 objects covering the core commercial lifecycle: accounts, quotes, orders, assets, contracts, and their detail/attribute records.

## Core Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `Account` | Customer account | Name, ParentId (self-ref hierarchy) |
| `Contact` | Person associated with an account | AccountId, Name |
| `Quote` | Sales quote | AccountId, ContactId, Pricebook2Id, Status, ExpirationDate |
| `QuoteLineItem` | Line item on a quote | QuoteId, Product2Id, PricebookEntryId, ProductSellingModelId, Quantity, UnitPrice |
| `Order` | Purchase order | AccountId, QuoteId, ContractId, Pricebook2Id, SalesTransactionTypeId, Status |
| `OrderItem` | Line item on an order | OrderId, Product2Id, PricebookEntryId, ProductSellingModelId, QuoteLineItemId, OriginalOrderItemId |
| `Contract` | Service contract | AccountId |
| `Asset` | Customer-owned asset (created from OrderItem) | AccountId, Product2Id, ContactId, ParentId (self-ref), RootAssetId |
| `SalesTransactionType` | Transaction type classification | — |

## Asset Lifecycle Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `AssetStatePeriod` | Time-sliced state of an asset | AssetId, StartDate, EndDate, Quantity, Amount |
| `AssetAction` | Action performed on an asset (New, Amend, Renew, Cancel) | AssetId, ActionType |
| `AssetActionSource` | Source transaction for an asset action | AssetActionId, OrderItemId |
| `AssetRelationship` | Relationship between assets | AssetId, RelatedAssetId |
| `AssetContractRelationship` | Links asset to contract | AssetId |
| `AssetTokenEvent` | Token consumption events on an asset | — |

## Quote Detail Objects

| Object | Purpose |
|--------|---------|
| `QuoteLineGroup` | Groups quote line items (bundles) |
| `QuoteLineDetail` | Extended detail for a quote line |
| `QuoteLineItemAttribute` | Attribute values on a quote line |
| `QuoteLineRateAdjustment` | Rate adjustments applied to a quote line |
| `QuoteLineRateCardEntry` | Rate card entries on a quote line |
| `QuotLineItmUsageRsrcPlcy` | Usage resource policy on a quote line |
| `QuotLineItmUseRsrcGrant` | Usage resource grant on a quote line |
| `QuoteAction` | Actions on a quote (sourced from assets) |

## Order Detail Objects

| Object | Purpose |
|--------|---------|
| `OrderItemGroup` | Groups order items (bundles) |
| `OrderItemDetail` | Extended detail for an order item |
| `OrderItemAttribute` | Attribute values on an order item |
| `OrderItemRateAdjustment` | Rate adjustments applied to an order item |
| `OrderItemRateCardEntry` | Rate card entries on an order item |
| `OrderItemUsageRsrcPlcy` | Usage resource policy on an order item |
| `OrderItemUsageRsrcGrant` | Usage resource grant on an order item |
| `OrderDeliveryMethod` | Delivery method for an order |

## Fulfillment Bridge

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `FulfillmentOrder` | Fulfillment order (from Order) | AccountId, OrderId |
| `FulfillmentOrderLineItem` | Line items being fulfilled | FulfillmentOrderId, OrderItemId, Product2Id |

## Key Relationships

```
Account ← Quote, Order, Contract, Asset, Contact, FulfillmentOrder (AccountId)
Account ← Account (ParentId, self-ref)
Quote ← QuoteLineItem (QuoteId, master-detail)
Order ← OrderItem (OrderId, master-detail)
Product2 ← QuoteLineItem, OrderItem, Asset, FulfillmentOrderLineItem (Product2Id)
PriceBookEntry ← QuoteLineItem, OrderItem (PricebookEntryId)
ProductSellingModel ← QuoteLineItem, OrderItem (ProductSellingModelId)
Quote ← Order (QuoteId)
Contract ← Order (ContractId)
QuoteLineItem ← OrderItem (QuoteLineItemId)
OrderItem ← OrderItem (OriginalOrderItemId, self-ref for amendments)
Asset ← AssetAction (AssetId)
AssetAction ← AssetActionSource (AssetActionId)
OrderItem ← AssetActionSource (OrderItemId)
Asset ← AssetStatePeriod (AssetId)
Asset ← Asset (ParentId, RootAssetId — bundle hierarchy)
Order ← FulfillmentOrder (OrderId)
FulfillmentOrder ← FulfillmentOrderLineItem (FulfillmentOrderId, master-detail)
OrderItem ← FulfillmentOrderLineItem (OrderItemId)
```

## SFDMU Data Plans

- `scratch_data` — base Account and Contact records
- `qb-clm` — Contract lifecycle objects (ObjectStateDefinition, transitions, etc.)
- Transaction records (Quote, Order, Asset) are created at runtime via business APIs, not data plans
