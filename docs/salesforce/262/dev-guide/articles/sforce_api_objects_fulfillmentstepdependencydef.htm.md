---
page_id: sforce_api_objects_fulfillmentstepdependencydef.htm
title: FulfillmentStepDependencyDef
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstepdependencydef.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentStepDependencyDef

Represents a dependency that must be created between two fulfillment
step records. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| DependencyScope | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The scope of the fulfillment step dependency definition. For example, Order or Order Item.  Valid values are:  - `Bundle` - `LineItem` - `Plan` - `CrossPlan` - `Custom`  The default value is `Plan`. |
| DependsOnStepDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fulfillment step definition that must be executed before this step.  This field is a relationship field.  Relationship Name  DependsOnStepDefinition  Refers To  FulfillmentStepDefinition |
| FulfillmentStepDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The identifier of the fulfillment step definition.  This field is a relationship field.  Relationship Name  FulfillmentStepDefinition  Relationship Type  Master-detail  Refers To  FulfillmentStepDefinition (the master object) |
| IsCompensateInReverse | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the order to insert the compensated group steps is reversed when a fulfillment step is canceled (`true`) or not (`false`).  The default value is `false`. This field is available in API version 63.0 and later. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the fulfillment step dependency definition. |
| PropagateStateToDependentStep | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The state that’s propagated to the dependent fulfillment step when the source fulfillment step is amended or canceled in the fulfillment plan.  Valid values are:  - `Amended` - `Both` - `Canceled` - `None`  This field is available in API version 63.0 and later. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentStepDependencyDefChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.")
:   Change events are available for the object.

[FulfillmentStepDependencyDefFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[FulfillmentStepDependencyDefHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[FulfillmentStepDependencyDefOwnerSharingRule](./sforce_api_associated_objects_ownersharingrule.htm.md "StandardObjectNameOwnerSharingRule is the model for all owner sharing rule objects associated with standard objects. These objects represent a rule for sharing a standard object with users other than the owner.")
:   Sharing rules are available for the object.

[FulfillmentStepDependencyDefShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
