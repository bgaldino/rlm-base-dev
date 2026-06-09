---
page_id: sforce_api_objects_fulfillmentstepdependency.htm
title: FulfillmentStepDependency
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstepdependency.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentStepDependency

Represents a dependency between tasks by defining the order between a
task and one that depends on it. This object is available in API version 61.0 and
later.

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
| DependencyDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the fulfillment step dependency definition.  This field is a relationship field.  Relationship Name  DependencyDefinition  Refers To  FulfillmentStepDependencyDef |
| DependentStepId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The name of a fulfillment step that depends on this step.  This field is a relationship field.  Relationship Name  DependentStep  Relationship Type  Master-detail  Refers To  FulfillmentStep |
| DependsOnStepId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the fulfillment step that this step depends on. That is, the name of the step that must be executed before this one can run.  This field is a relationship field.  Relationship Name  DependsOnStep  Refers To  FulfillmentStep |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  An automatically generated name for the fulfillment step dependency. |
