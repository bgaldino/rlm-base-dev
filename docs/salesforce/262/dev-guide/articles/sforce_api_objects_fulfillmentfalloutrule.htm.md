---
page_id: sforce_api_objects_fulfillmentfalloutrule.htm
title: FulfillmentFalloutRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentfalloutrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentFalloutRule

Represents the fulfillment fallout handling rule. This object is
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
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| ErrorCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The failure error code of the fulfillment step that's associated with the rule. |
| FalloutQueueId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fallout queue that's associated with the fallout task. This field is available in API version 62.0 and later.  This field is a relationship field.  Relationship Name  FalloutQueue  Refers To  Group |
| FlowDefinitionName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the flow definition that's associated with the `AutoTask` type of fulfillment step. |
| IntegrationDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The integration definition that's associated with the `Callout` type of fulfillment step.  This field is a relationship field.  Relationship Name  IntegrationDefinition  Relationship Type  Lookup  Refers To  IntegrationProviderDef |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the flow definition that's associated with the `AutoTask` type of fulfillment step. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the fulfillment record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| RetriesAllowed | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of times a retry policy is run before the fulfillment step is considered failed. |
| RetryIntervals | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The interval after which the selected retry policy is run when the fulfillment step fails. This field is available in API version 62.0 and later. |
| RetryPolicy | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the retry policy used when the fulfillment step fails.  Valid value is:  - `Immediate` - `Monotonous` - `Staggered` |
| StepType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the type of fulfillment step associated with the fallout rule.  Valid values are:  - `AutoTask` - `Callout` - `ManualTask` - `Milestone` - `Pause` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentFalloutRuleHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[FulfillmentFalloutRuleShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
