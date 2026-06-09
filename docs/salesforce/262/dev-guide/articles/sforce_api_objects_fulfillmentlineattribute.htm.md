---
page_id: sforce_api_objects_fulfillmentlineattribute.htm
title: FulfillmentLineAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentlineattribute.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentLineAttribute

Represents an attribute of a fulfillment order line. This object
is available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  A unique identifier for the attribute definition in the catalog.  This field is a relationship field.  Relationship Name  AttributeDefinition  Refers To  AttributeDefinition |
| AttributeName | Type  string  Properties  Filter, Group, idLookup, Nillable, Sort  Description  The name of the attribute. |
| AttributePicklistValueId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  AttributePicklistValue  Refers To  AttributePicklistValue |
| AttributeValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value of the attribute. |
| ExternalId | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID that uniquely identifies the relationship in an external data source. |
| FulfillmentOrderLineItemId | Type  reference  Properties  Create, Filter, Group, Sort  Description  A unique identifier for the fulfillment order line item.  This field is a relationship field.  Relationship Name  FulfillmentOrderLineItem  Relationship Type  Master-detail  Refers To  FulfillmentOrderLineItem (the master object) |
