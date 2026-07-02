---
page_id: sforce_api_objects_orderitemusagersrcplcy.htm
title: OrderItemUsageRsrcPlcy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_orderitemusagersrcplcy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# OrderItemUsageRsrcPlcy

Represents the policies that are used for the usage resource that's
associated with the usage product added in the order item. This object is available in
API version 65.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| DrawdownOrder | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the order that's used to debit consumption of entitlements related to the usage resource from the usage entitlement bucket.  Valid values are:  - `ExpiringFirst` - `GrantedFirst` - `GrantedLast` |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  An auto-generated number assigned to the order item for usage product grant record. For example, OIURG-4567 |
| OrderItemId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The order item associated with the usage product.  This field is a relationship field.  Relationship Name  OrderItem  Relationship Type  Master-detail  Refers To  OrderItem (the master object) |
| ProductUsageResourcePolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The product usage resource policy associated with the usage resource related to the usage product added in the order item.  This field is a relationship field.  Relationship Name  ProductUsageResourcePolicy  Refers To  ProductUsageResourcePolicy |
| RatingFrequencyPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The rating frequency policy associated with the usage resource related to the usage product added in the order item.  This field is a relationship field.  Relationship Name  RatingFrequencyPolicy  Refers To  RatingFrequencyPolicy |
| UsageAggregationPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage aggregation policy associated with the usage resource related to the usage product added in the order item.  This field is a relationship field.  Relationship Name  UsageAggregationPolicy  Refers To  UsageResourceBillingPolicy |
| UsageCommitmentPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage commitment policy associated with the usage resource related to the usage product added in the order item.  This field is a relationship field.  Relationship Name  UsageCommitmentPolicy  Refers To  UsageCommitmentPolicy |
| UsageOveragePolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage overage policy associated with the usage resource related to the usage product added in the order item.  This field is a relationship field.  Relationship Name  UsageOveragePolicy  Refers To  UsageOveragePolicy |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource associated with the usage product that's added in the order item.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |
