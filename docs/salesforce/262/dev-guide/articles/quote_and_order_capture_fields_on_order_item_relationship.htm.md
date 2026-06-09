---
page_id: quote_and_order_capture_fields_on_order_item_relationship.htm
title: Transaction Management Fields on Order Item Relationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_item_relationship.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Order Item Relationship

Standard and custom fields extend the standard Order Item Relationship object
for use in Transaction Management. This object is available in API version 58.0 and
later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Item Relationship](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_orderitemrelationship.htm) for fields on the
Salesforce platform object.

## Fields

| Field | Details |
| --- | --- |
| ProductRelatedComponentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the product that is included in a product bundle, a set, or a product and an add-on.  This field is a relationship field.  Relationship Name  ProductRelatedComponent  Relationship Type  Lookup  Refers To  ProductRelatedComponent |
