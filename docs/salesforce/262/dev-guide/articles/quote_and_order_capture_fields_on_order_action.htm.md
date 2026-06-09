---
page_id: quote_and_order_capture_fields_on_order_action.htm
title: Transaction Management Fields on Order Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_action.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Order Action

Standard and custom fields extend the standard Order Action object for use in
Transaction Management. This object is available in API version 55.0 and
later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Action](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_orderaction.htm) for fields on the Salesforce
platform object.

## Fields

| Field | Details |
| --- | --- |
| Type | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The business action that created the order product.  Valid values are:  - `Add` - `Amend` - `Cancel` - `No Change`—A   child product was added to the bundle, but the top-level   product in the bundle was otherwise unchanged. - `Renew` |
