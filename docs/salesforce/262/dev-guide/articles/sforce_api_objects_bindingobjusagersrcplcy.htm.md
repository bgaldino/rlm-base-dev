---
page_id: sforce_api_objects_bindingobjusagersrcplcy.htm
title: BindingObjUsageRsrcPlcy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_bindingobjusagersrcplcy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# BindingObjUsageRsrcPlcy

Represents the policies that are used for the usage resource that's
associated with an asset or a binding object. This object is available in API version
65.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| BindingObjectId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The object that's bounded with the quote line policy or order policy.  This field is a polymorphic relationship field.  Relationship Name  BindingObject  Refers To  Account, Asset, BindingObjectCustomExt, Contract |
| DrawdownOrder | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the order that's used to debit consumption of entitlements related to the usage resource from the usage entitlement bucket.  Valid values are:  - `ExpiringFirst` - `GrantedFirst` - `GrantedLast` |
| EffectiveEndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time until when the policy remains effective. |
| EffectiveStartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the policy becomes effective. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The auto-generated identifier for the quote line item usage resource policy record. For example, BOURP-000004. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the binding object usage resource policy.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RatingFrequencyPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The rating frequency policy associated with the usage resource.  This field is a relationship field.  Relationship Name  RatingFrequencyPolicy  Refers To  RatingFrequencyPolicy |
| UsageAggregationPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage aggregation policy associated with the usage resource.  This field is a relationship field.  Relationship Name  UsageAggregationPolicy  Refers To  UsageResourceBillingPolicy |
| UsageCommitmentPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage commitment policy associated with the usage resource.  This field is a relationship field.  Relationship Name  UsageCommitmentPolicy  Refers To  UsageCommitmentPolicy |
| UsageOveragePolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage overage policy associated with the usage resource.  This field is a relationship field.  Relationship Name  UsageOveragePolicy  Refers To  UsageOveragePolicy |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource associated with the usage product.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |
