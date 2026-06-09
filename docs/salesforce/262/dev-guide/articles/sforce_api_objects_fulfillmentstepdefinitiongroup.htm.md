---
page_id: sforce_api_objects_fulfillmentstepdefinitiongroup.htm
title: FulfillmentStepDefinitionGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstepdefinitiongroup.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentStepDefinitionGroup

Represents a set of fulfillment step definitions. This object is
available in API version 61.0 and later.

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
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the fulfillment step definition group. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| UsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The business that uses Fulfillment Orchestration.  Possible values are:  - `IntegrationOrchestrator` - `Generic` - `InsuranceRuleAction` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentStepDefinitionGroupHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[FulfillmentStepDefinitionGroupShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
