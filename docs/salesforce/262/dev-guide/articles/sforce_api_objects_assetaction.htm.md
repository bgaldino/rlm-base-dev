---
page_id: sforce_api_objects_assetaction.htm
title: AssetAction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetAction

Represents a change made to a lifecycle-managed asset. The fields can’t be
edited. This object is available in API version 50.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

To use Customer Asset Lifecycle Management APIs,
you must have the Access Customer Asset Lifecycle Management APIs permission and Read
access to the Asset, Asset Action, Asset Action Source, and Asset State Period
objects.

## Fields

| Field | Details |
| --- | --- |
| ActionDate | Type  dateTime  Properties  Filter, Sort  Description  The date when an asset action change is recorded. This date can differ from the start date of the related asset state period. For example, suppose that a customer cancels a subscription in June, and the subscription expires in October. The date the customer cancels the subscription (June) is the action date of the asset action. The cancellation's effective date (October) is the start date of the asset state period. |
| ActualTaxChange | Type  currency  Properties  Filter, Nillable, Sort  Description  The rollup of actual tax from all asset action sources. This field is populated by the system. Label is **Change in Actual Tax**.  This field is a calculated field. |
| AdjustmentAmountChange | Type  currency  Properties  Filter, Nillable, Sort  Description  The rollup of adjustment amount from all asset action sources. This field is populated by the system. Label is **Change in Adjustment Amount**.  This field is a calculated field. |
| Amount | Type  currency  Properties  Filter, Sort  Description  The delta in the total asset amount resulting from an asset action. |
| AssetActionNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The ID of the asset action. Label is **Name**. |
| AssetId | Type  reference  Properties  Filter, Group, Sort  Description  The ID of the related lifecycle-managed asset. Label is **Asset**.  This field is a relationship field.  Relationship Name  Asset  Relationship Type  Lookup  Refers To  Asset |
| CanRollBack | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the last asset action can be rolled back (`true`). If this property is set to `false`, the asset and the last asset action can’t be rolled back.  The default value is `false`. This field is available in API version 65.0 and later. |
| CategoryEnum | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The business category of the asset action, for use in reporting. Asset action totals are broken out by the picklist values on this required field, and those totals are in turn reflected on assets. These categories are available and aren’t customizable. Label is **Business Category**.  Possible values are:  - `Cancellations` - `Cross-Sells` - `Downgrades` Indicates a   transition to a lower-level version or tier of an asset. - `Downsells` Indicates a   negative quantity amendment or a decreased Line Item total   price with no change in quantity. - `Initial Sale` Indicates   that the asset is initially purchased by an account. - `Other` - `Renewals` - `Swaps` Indicates the   exchange of one asset for another. Applies to both   swapped-out and swapped-in actions. - `Terms And Conditions   Changes` - `Transfers` Indicates   that an asset is transferred from one account to   another. - `Upgrades` Indicates a   transition to a higher-level version or tier of an   asset. - `Upsells` Indicates a   positive quantity amendment or an increased Line Item total   price with no change in quantity. |
| EstimatedTaxChange | Type  currency  Properties  Filter, Nillable, Sort  Description  The rollup of estimated tax from all asset action sources. This field is populated by the system. Label is **Change in Estimated Tax**.  This field is a calculated field. |
| MrrChange | Type  currency  Properties  Filter, Sort  Description  The delta in the asset’s monthly recurring revenue resulting from an asset action. For example, suppose that the MRR during an asset state period is $200 and the next asset action adds $100. Then this field’s value is $100. Label is **Change in Monthly Recurring Revenue**. |
| ProductAmountChange | Type  currency  Properties  Filter, Nillable, Sort  Description  The rollup of product amount from all asset action sources. This field is populated by the system. Label is **Change in Product Amount**.  This field is a calculated field. |
| QuantityChange | Type  double  Properties  Filter, Sort  Description  The delta in the asset quantity resulting from an asset action. For example, suppose that the asset quantity during an asset state period is 20 and the next asset action adds 10. Then this field’s value is 10. Label is **Change in Quantity**. |
| RolledbackAssetAction | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The last asset action rolled back in the current rollback transaction. This field is available in API version 65.0 and later. |
| SubtotalChange | Type  currency  Properties  Filter, Nillable, Sort  Description  The rollup of subtotal from all asset action sources. This field is populated by the system. Label is **Change in Subtotal**.  This field is a calculated field. |
| Subtype | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The subtype of the action on the asset.  Valid values are:  - `DowngradeFrom`—Available in API version 66.0   and later. - `DowngradeTo`—Available in API version 66.0   and later. - `FieldAmendment` - `Rollback` - `StartDateAdjustment` - `SwapIn`—Available   in API version 66.0 and later. - `SwapOut`—Available in API version 66.0 and   later. - `TransferFrom` - `TransferTo` - `UpgradeFrom`—Available in API version 66.0   and later. - `UpgradeTo`—Available in API version 66.0 and   later.  This field is available in API version 65.0 and later. |
| TotalAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the current and previous asset action amount. This field is populated by the system.  This field is a calculated field. |
| TotalCancellationsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Cancellations`. This field is populated by the system. |
| TotalCrossSellsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Cross-Sells`. This field is populated by the system. |
| TotalDowngradesAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Downgrades`. This field is populated by the system and is available in API version 66.0 and later. |
| TotalDownsellsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Downsells`. This field is populated by the system. |
| TotalInitialSaleAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Initial Sale`. This field is populated by the system. |
| TotalMrr | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the monthly recurring revenue for the current and previous asset action. This field is populated by the system. Label is **Total Monthly Recurring Revenue**. |
| TotalOtherAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Other`. This field is populated by the system. |
| TotalQuantity | Type  double  Properties  Filter, Nillable, Sort  Description  The sum of the changes in quantity for the current and previous asset action. This field is populated by the system. |
| TotalRenewalsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Renewals`. This field is populated by the system. |
| TotalSwapsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Swaps`. This field is populated by the system and is available in API version 66.0 and later. |
| TotalTermsAndConditionsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Terms and Conditions Changes`. This field is populated by the system. Label is **Total Terms and Conditions Changes Amount**. |
| TotalTransfersAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Transfers`. This field is populated by the system. |
| TotalUpgradesAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Upgrades`. This field is populated by the system and is available in API version 66.0 and later. |
| TotalUpsellsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of current and previous asset action amounts categorized as `Upsells`. This field is populated by the system. |
| Type | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The REST API used to generate the asset action. This field is populated by the system.  Valid values are:  - `Cancel` - `Change` - `Convert` - `Generate` |
