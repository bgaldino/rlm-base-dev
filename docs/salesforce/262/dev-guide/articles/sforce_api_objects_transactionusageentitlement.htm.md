---
page_id: sforce_api_objects_transactionusageentitlement.htm
title: TransactionUsageEntitlement
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_transactionusageentitlement.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# TransactionUsageEntitlement

Represents the details of each usage entitlement that's granted with
the purchased sellable product, such as quantity and date when the entitlements were
granted. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

To create, update, and delete transaction usage entitlement records, you must have the
Usage Management Run Time permission set license.

## Fields

| Field | Details |
| --- | --- |
| AccountId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The account that's associated with the usage entitlement.  This field is a relationship field.  Relationship Name  Account  Refers To  Account |
| ActionType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of action that resulted in the transaction usage entitlement.  Valid values are:  - `Amend` - `Cancellation` - `New` - `Ramp` - `Renewal` |
| AssetId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The asset associated with the sellable product.  This field is a relationship field.  Relationship Name  Asset  Refers To  Asset |
| ChargeForOverage | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The action to be taken when the entitlements are used beyond their grant values.  Valid values are:  - `No`—Don't charge   for overconsumption - `Yes`—Charge for   overconsumption |
| DrawdownOrder | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The order that's used to debit entitlement consumption from the usage entitlement bucket.  Valid values are:  - `ExpiringFirst` - `GrantedFirst` - `GrantedLast` |
| EffectiveEndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the active transaction usage entitlement ends. |
| EffectiveStartDateTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the transaction usage entitlement becomes active. |
| EntitlementQuantity | Type  double  Properties  Create, Filter, Sort, Update  Description  The entitlement quantity for the usage resource. |
| EntitlementProcessingStatus | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates whether the transaction usage entitlement has been processed by entitlement service to be used in Billing. Available in API version 65.0 and later.  Possible values are:  - `PENDING`—Pending - `PROCESSED`—Processed  The default value is `PENDING`. |
| EntitlementUomClassId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The unit of measure class for the usage entitlement.  This field is a relationship field.  Relationship Name  EntitlementUomClass  Refers To  UnitOfMeasureClass |
| EntitlementUomId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The unit of measure to calculate the usage entitlement.  This field is a relationship field.  Relationship Name  EntitlementUom  Refers To  UnitOfMeasure |
| ExternalOrderItem | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The custom or external order item that's associated with the entitlement. |
| GrantBindingTargetId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The target associated with the entitlements that are granted with the sellable product.  This field is a relationship field.  Relationship Name  GrantBindingTarget  Refers To  Account, Asset, BindingObjectCustomExt, Contract |
| GrantType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the type of model that defines how the usage resource is consumed. Available in API version 65.0 and later.  Possible values are:  - `Commit` - `Grant`  The default value is `Grant`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Auto number, Defaulted on create, Filter, idLookup, Sort  Description  Autogenerated identifier for the transaction usage entitlement record. |
| NetQuantity | Type  double  Properties  Create, Filter, Sort, Update  Description  The total quantity that combines the amended quantity with the initial transaction quantity in the order item. |
| OriginalEndDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The end date of the transaction usage entitlement when the related order was assetized, amended, renewed, or canceled. |
| OrderItemId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The order item that's associated with the entitlement.  This field is a polymorphic relationship field.  Relationship Name  OrderItem  Refers To  OrderItem, WorkOrderLineItem |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the transaction usage entitlement.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PricebookEntryId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The price book entry that's associated with the sellable product.  This field is a relationship field.  Relationship Name  PricebookEntry  Refers To  PricebookEntry |
| ProductId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The sellable product for which the entitlement is granted.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| RatingFrequencyPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The sellable product for which the entitlement is granted. Available in API version 64.0 and later. This field is deprecated and will be retired in a future version.  This field is a relationship field.  Relationship Name  RatingFrequencyPolicy  Refers To  RatingFrequencyPolicy |
| TokenResourceId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage resource of category Token associated with the usage resource related to the usage product added in the quote line item. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  TokenResource  Refers To  UsageResource |
| TransactionQuantity | Type  double  Properties  Create, Filter, Sort, Update  Description  The transaction quantity in the order for the usage entitlement. |
| UsageAggregationPolicyId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The usage aggregation policy for this entitlement. This field is deprecated and will be retired in a future version.  This field is a relationship field.  Relationship Name  UsageAggregationPolicy  Refers To  UsageResourceBillingPolicy |
| UsageGrantRefreshPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage grant refresh policy that's associated with the transaction usage entitlement.  This field is a relationship field.  Relationship Name  UsageGrantRefreshPolicy  Refers To  UsageGrantRenewalPolicy |
| UsageGrantRolloverPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage grant rollover policy that's associated with the transaction usage entitlement.  This field is a relationship field.  Relationship Name  UsageGrantRolloverPolicy  Refers To  UsageGrantRolloverPolicy |
| UsageModelType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of usage model for a product or service. `Anchor` is the main subscription product or service. `Pack` is the add-on product or service that grants additional usage resources for consumption. `Commit` is the product or service with a specific committed quantity of consumption.  Valid values are:  - `Anchor` - `Monetary   Commitment` - `Pack` - `Quantity Commitment` - `Token Commitment`  Available in API version 64.0 and later. |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource record that's associated with the transaction usage entitlement.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |
| ValidityPeriodTerm | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The duration for which the usage resource grant is valid, when used with the validity period units. |
| ValidityPeriodUnit | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The length of a validity period for the usage resource grant, when used with the validity period term.  Valid values are:  - `Month` - `None` - `Year` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[TransactionUsageEntitlementFeed](https://developer.salesforce.com/docs/./sforce_api_associated_objects_feed.htm.md)
:   Feed tracking is available for the object.

[TransactionUsageEntitlementHistory](https://developer.salesforce.com/docs/./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.

[TransactionUsageEntitlementOwnerSharingRule](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing rules are available for the object.

[TransactionUsageEntitlementShare](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing is available for the object.
