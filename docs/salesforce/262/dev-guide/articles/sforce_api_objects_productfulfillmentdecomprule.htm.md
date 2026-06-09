---
page_id: sforce_api_objects_productfulfillmentdecomprule.htm
title: ProductFulfillmentDecompRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productfulfillmentdecomprule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductFulfillmentDecompRule

Represents a rule that determines how an order is broken into
sub-orders with specific technical details that help in order fulfillment. It can be
applied to a commercial or a technical product. This object is available in API
version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ConditionData | Type  textarea  Properties  Create, Nillable, Update  Description  The condition for executing the product fulfillment decomposition. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later. |
| DestinationProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The destination product for the decomposition rule.  This field is a relationship field.  Relationship Name  DestinationProduct  Relationship Type  Lookup  Refers To  Product2 |
| DestinationIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The destination entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the decomposition rule. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| Priority | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The priority of the decomposition rule. Decomposition rules are executed in order of priority. |
| SourceProductClassificationId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The classification of the source product that's used for decomposition. This field is available in API version 62.0 and later.  This field is a relationship field.  Relationship Name  SourceProductClassification  Refers To  ProductClassification |
| SourceClassIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The source classification entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later. |
| SourceIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The source entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later. |
| SourceProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Source product for the decomposition rule.  This field is a relationship field.  Relationship Name  SourceProduct  Relationship Type  Lookup  Refers To  Product2 |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductFulfillmentDecompRuleShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
