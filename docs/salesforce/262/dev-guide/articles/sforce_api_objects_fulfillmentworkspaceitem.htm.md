---
page_id: sforce_api_objects_fulfillmentworkspaceitem.htm
title: FulfillmentWorkspaceItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentworkspaceitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentWorkspaceItem

Represents information about the attributes that are used in the
definition for a fulfillment step group. This object is available in API version 61.0
and later.

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
| FulfillmentStepDefinitionGroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  For internal use only.  This field is a relationship field.  Relationship Name  FulfillmentStepDefinitionGroup  Relationship Type  Master-detail  Refers To  FulfillmentStepDefinitionGroup (the detail object) |
| FulfillmentWorkspaceId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the parent fulfillment workspace that's related to this record.  This field is a relationship field.  Relationship Name  FulfillmentWorkspace  Relationship Type  Master-detail  Refers To  FulfillmentWorkspace (the master object) |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the fulfillment workspace item. |
| ShowOrder | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The display sequence value of the fulfillment workspace item. |
