---
page_id: quote_and_order_capture_fields_on_quote_document.htm
title: Transaction Management Fields on Quote Document
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_quote_document.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Quote Document

Standard and custom fields extend the standard Quote Document object for use
in Transaction Management to represent information about quote documents. This object
is available in API version 61.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Quote Document](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_quotedocument.htm) for fields on the Salesforce
platform object.

## Fields

| Field | Details |
| --- | --- |
| Document Template | Type  String  Properties  Create, Filter, Group, Nillable, Sort  Description  The template ID used for generating the quote document. |
| Status | Type  Picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The status of the quote document.  Possible values are:  - `Completed` - `Failed` - `Generating` - `In Progress` - `None` - `Queued`  The default value is `None`. |
