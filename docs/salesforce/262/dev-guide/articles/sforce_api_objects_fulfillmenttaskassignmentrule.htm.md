---
page_id: sforce_api_objects_fulfillmenttaskassignmentrule.htm
title: FulfillmentTaskAssignmentRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmenttaskassignmentrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentTaskAssignmentRule

Represents a set of actions that assign a task to a user or
queue. This object is available in API version 63.0 and later.

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
| ConditionData | Type  textarea  Properties  Create, Nillable, Update  Description  The condition for executing the fulfillment task assignment rule. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later. |
| ConditionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Condition ID that's used to determine the task assignment.  This field is a polymorphic relationship field.  Relationship Name  Condition  Refers To  ExpressionSet |
| DestinationId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Destination ID of the task assignment such as, Queue or User.  This field is a polymorphic relationship field.  Relationship Name  Destination  Refers To  Group, User |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the object that specifies the condition used to determine the task assignment. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the task assignment rule record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Priority | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The priority of the rule for execution. |
| SourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Source ID of the task assignment such as Queue.  This field is a relationship field.  Relationship Name  Source  Refers To  Group |
| TaskAllocationType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The method of assigning the manual step.  Valid values are:  - `ContextBased` - `LeastLoaded` - `RoundRobin` |
| UsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Name of the usage type.  Possible values are:  - `Fulfillment` - `Generic` - `InsuranceRuleAction`—Insurance Rule   Action - `IntegrationOrchestrator`—Integration   Orchestrator  The default value is `Fulfillment`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentTaskAssignmentRuleFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[FulfillmentTaskAssignmentRuleHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[FulfillmentTaskAssignmentRuleShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
