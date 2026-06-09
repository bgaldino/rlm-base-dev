---
page_id: quote_and_order_capture_fields_on_object_state_definition.htm
title: Transaction Management Fields on Object State Definition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_object_state_definition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Object State Definition

Standard and custom fields extend the standard Object State Definition object
for use in Transaction Management to represent the object state model for a particular
status field for an entity.  This object is available in API version 60.0 and later.

## Fields

| Field | Details |
| --- | --- |
| AppUsageType | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  This field indicates under which AppUsageType the transition applies to. For example, ObjectStateDefinition associated with “Revenue Lifecycle Management” AppUsageType will apply to quotes, assets, or orders associated with “Revenue Lifecycle Management”. |
