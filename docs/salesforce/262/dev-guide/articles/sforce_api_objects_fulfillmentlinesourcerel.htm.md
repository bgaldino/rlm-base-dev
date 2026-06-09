---
page_id: sforce_api_objects_fulfillmentlinesourcerel.htm
title: FulfillmentLineSourceRel
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentlinesourcerel.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentLineSourceRel

Represents the relationship between a fulfillment order line and its
decomposition source. This object is available in API version 61.0 and
later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| Action | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the action to be performed on the asset fulfillment decomposition record. This field is available in API version 66.0 and later.  Possible values are:  - `Add` - `Cancel` - `NoChange`—No   Change |
| FulfilmentOrderLineId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the fulfillment order line.  This field is a relationship field.  Relationship Name  FulfilmentOrderLine  Refers To  FulfillmentOrderLineItem |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The relation between the two order line sources. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| SourceItemIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The ID of the decomposition source that's related to the fulfilment order line. This field is available in API version 64.0 and later. |
| SourceLineItemId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the source line item.  This field is a polymorphic relationship field.  Relationship Name  SourceLineItem  Refers To  FulfillmentOrderLineItem, OrderItem |
| SourceType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of source for the line item.  Valid values are:  - `SourceBundleRoot` - `SourceLineItem` |
| SupplementalAction | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The supplemental action that's applied to the line item based on the run-time changes made to the original fulfillment request. This field is available in API version 62.0 and later.  Valid values are:  - `Add` - `Amend` - `Cancel` - `NoChange` |
| UniqueIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort  Description  For internal use only. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentLineSourceRelShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
