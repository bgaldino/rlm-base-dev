---
page_id: usage-management-fields-on-product2
title: Usage Management Fields on Product2
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-fields-on-product2.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-fields-on-standard-objects
legacy_page_id: usage_management_fields_on_product2.htm
fetched_at: 2026-11-25
---

# Usage Management Fields on Product2

Standard and custom fields extend the standard Product2 object for use in Usage Management to represent information about products.

## UsageModelType

**Type:** picklist

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** The type of usage model for a product or service.

Valid values are:

- `Anchor`—The main subscription product or service. Available in API version 62.0 and later.

- `Pack`—The add-on product or service that grants additional usage resources for consumption. Available in API version 62.0 and later.

- `Monetary Commitment`—An agreement by a customer to spend a minimum amount for a product or service in a defined period. Available in API version 65.0 and later.

- `Quantity Commitment`—An agreement by a customer to use a minimum quantity of a product or service in a defined period. Available in API version 65.0 and later.

- `Token Commitement`—An agreement by a customer to use a minimum quantity of tokens for a product or service in a defined period. Available in API version 65.0 and later.

**See Also**

- [Product2](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_product2.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-fields-on-product2.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
