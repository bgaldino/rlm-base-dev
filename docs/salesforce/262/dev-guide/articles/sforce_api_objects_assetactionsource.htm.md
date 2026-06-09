---
page_id: sforce_api_objects_assetactionsource.htm
title: AssetActionSource
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetactionsource.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetActionSource

Represents an optional way to record what transactions caused changes to
lifecycle-managed assets. Use it to trace financial and other information about asset
actions. This object supports Salesforce order products and work order line items, and
transaction IDs from other systems. The fields can’t be edited. This object is
available in API version 50.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`.

## Special Access Rules

To use Customer Asset Lifecycle Management APIs,
you must have the Access Customer Asset Lifecycle Management APIs permission and Read
access to the Asset, Asset Action, Asset Action Source, and Asset State Period
objects.

## Fields

| Field | Details |
| --- | --- |
| ActualTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The region-specific tax amount determined at time of the order.  This field is not used for price and tax calculations. |
| AdjustmentAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  An adjustment to the product amount, such as a discount. |
| AssetActionId | Type  reference  Properties  Filter, Group, Sort  Description  The related asset action, that is, the change caused by an asset action source transaction.  This field is a relationship field.  Relationship Name  AssetAction  Relationship Type  Lookup  Refers To  AssetAction |
| AssetActionSourceNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The ID of the asset action source. Label is **Name**. |
| BillingReference | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ID of the OrderItem or OrderItemDetail record that this AssetActionSource record is created for. |
| Discount | Type  percent  Properties  Filter, Nillable, Sort  Description  The discount, expressed as a percentage, that's applied to the asset.  This field is available in API version 62.0 and later. |
| DiscountAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The discount, expressed as currency, that's applied to the asset.  This field is available in API version 62.0 and later. |
| EffectiveGrantDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the resources associated with the asset were granted.  This field is available in orgs that have Revenue Cloud when Rate Management is enabled.  This field is available in API version 62.0 and later. |
| EndDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The end date of the service or change. |
| EstimatedTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The estimate of the region-specific tax amount made at time of the transaction. |
| ExternalReference | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ID of an asset action source transaction originating in a system outside of Salesforce. |
| ExternalReferenceDataSource | Type  string  Properties  Filter, Group, Nillable, Sort  Description  A system outside of Salesforce that contains asset action source transactions. |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the legal entity record associated with the asset action source transaction.  This field is a relationship field.  This field is available in API version 62.0 and later.  Relationship Name  LegalEntity  Relationship Type  Lookup  Refers To  LegalEntity |
| ListPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  List price for the order product. Value is inherited from the associated PriceBookEntry upon order product creation. |
| NetUnitPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  The final adjusted unit price, inclusive of all adjustments, but exclusive of tax. The unit price after all price adjustments are applied. |
| ObligatedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  When a line amount is prorated, this amount shows the service amount that’s been consumed. |
| OriginalLineNumber | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of the original order item detail line. Salesforce uses this information to create a record to amend, renew, or cancel an order. This field is available in API version 64.0 and later.  Relationship Name  OrderItemDetail  Relationship Type  Lookup  Refers To  LineNumber |
| PeriodBoundary | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Boundary delimiters for periods. It determines when a period starts and/or ends.  Valid values are:  - `AlignToCalendar` - `Anniversary` - `DayOfPeriod` - `LastDayOfPeriod` |
| PeriodBoundaryDay | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number specifying the day number when Period Boundary is a specific day in a week/month/year. It only applies when PeriodBoundary is set to "day of period.” |
| PeriodBoundaryStartMonth | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Field is populated based on input in the StartDate, PeriodBoundary, and PeriodBoundaryDay when BillingFrequency2 is Annual or by manual user entry. Possible values are: 1-January  2-February  3-March  4-April  5-May  6-June  7-July  8-August  9-September  10-October  11-November  12-December |
| PricebookEntryId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  PricebookEntry is used as a lookup for price information in order to pre-populate OrderItem's ListPrice and UnitPrice. |
| PricingTermCount | Type  double  Properties  Filter, Nillable, Sort  Description  Number of pricing terms is this subscription product. |
| ProductAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The product amount after the asset action source transaction. |
| ProductSellingModelId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Specifies the product selling model type. Foreignkey to ProductSellingModel entity. |
| ProrationPolicyId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the ProrationPolicy used for pricing. |
| Quantity | Type  double  Properties  Filter, Nillable, Sort  Description  The product quantity or the change in product quantity after the asset action source transaction. |
| ReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of an asset action source transaction originating in Salesforce. The transaction can be an order product or a work order line item.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntityItem  Relationship Type  Lookup  Refers To  OrderItem, WorkOrderLineItem |
| SegmentIdentifier | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ID of the ramp segment associated with the asset action source transaction.  The maximum supported length is 255 characters from API version 67.0 and later.  This field is available in API version 62.0 and later. |
| StartDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The start date of the service or change. |
| Subtotal | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the product amount and the adjustment amount.  This field is a calculated field. |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Lookup to Tax Treatment entity. It's used to calculate tax. |
| TotalLineAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The price of the line before any price adjustments were applied. SalesTransactionItem: ProratedStartingTotal / StartingPriceTotal. Note: TotalPrice is computed using the UnitPrice, which includes discounts (price adjustments), while TotalLineAmount doesn’t include price adjustments. |
| TotalPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  Calculated by the pricing engine for ARC. Summation of TotalAdjustmentAmount plus TotalLineAmount for this item. |
| TransactionDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date of a source transaction, such as an order date. |
| UnitPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  The unit price of the item before any discounts or tax calculation. |
