---
page_id: sforce_api_objects_valtfrmgrp.htm
title: ValTfrmGrp
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_valtfrmgrp.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ValTfrmGrp

Represents a rule that determines how an order is broken into
sub-orders with specific technical details that help in order fulfillment. The rule can be
applied to a commercial or a technical product. This object is available in API
version 61.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| DestinationPrimitiveType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The data type of the output value.  Valid values are:  - `Boolean` - `Currency` - `Date` - `Datetime` - `Number` - `Percent`—Picklist   Value - `Text` |
| IsDestinationEnumerated | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the output is a list of values (`true`) or not (`false`).  The default value is `false`. |
| IsSourceEnumerated | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the input is from a list of values (`true`) or not (`false`).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the list mapping. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who owns this record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| SourcePrimitiveType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The data type of the input value.  Valid values are:  - `Boolean` - `Currency` - `Date` - `Datetime` - `Number` - `Percent`—Picklist   Value - `Text` |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The data mapping feature that uses this value transformation group.  Valid value is `DFOListMapping` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ValTfrmGrpShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
