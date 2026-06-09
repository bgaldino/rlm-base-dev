---
page_id: sforce_api_objects_fulfillmentlinerel.htm
title: FulfillmentLineRel
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentlinerel.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentLineRel

Represents a relationship between two fulfillment order lines.
This object is available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssociatedFoItemInventory | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Inventory level for the associated fulfillment order item.  Valid values are:  - `Included in Main   Inventory` - `Not Included in Main   Inventory`  This field is available in API version 63.0 and later. |
| AssociatedFulfillOrderItemId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The identifier of the associated fulfillment order line item.  This field is a relationship field.  Relationship Name  AssociatedFulfillOrderItem  Refers To  FulfillmentOrderLineItem |
| AssociatedLineRole | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The role of the associated fulfillment order line item.  Valid values are:  - `BundleComponent` - `ClassificationComponent`—Product   Classification Component |
| AssociatedQuanScaleMethod | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Method used to scale the quantity of the associated order item summary relative to the main fulfillment order item.  Valid values are:  - `Constant` - `Proportional`  The default value is `Proportional`.  This field is available in API version 63.0 and later. |
| FulfillmentOrderId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the parent fulfillment order.  This field is a relationship field.  Relationship Name  FulfillmentOrder  Refers To  FulfillmentOrder |
| MainFulfillOrderItemRole | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The role of the primary fulfillment order line item.  Valid value is `Bundle`. |
| MainFulfillmentOrderItemId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the associated fulfillment order line item.  This field is a relationship field.  Relationship Name  MainFulfillmentOrderItem  Relationship Type  Master-detail  Refers To  FulfillmentOrderLineItem (the master object) |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the fulfillment order line relationship. |
| ProductRelationshipTypeId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The type of relationship between two assets.  This field is a relationship field.  Relationship Name  ProductRelationshipType  Refers To  ProductRelationshipType |
