---
page_id: connect_responses_product_discovery_catalog_output.htm
title: Catalog Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_catalog_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-11-23
---

# Catalog Details

Output representation of the details of a catalog definition.

## JSON Example

```
{
  "catalogs": [
    {
      "customFields": {},
      "id": "0ZSSG000001875O4AQ",
      "name": "Hardware Catalog",
      "numberOfCategories": 4
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalogCode` | String | Unique ID associated with the catalog. | Small, 67.0 | 67.0 |
| `catalogType` | String | Category of an entry in the catalog, which is customizable. For example, catalog types, such as sellable products, services, parts, technical services, or technical resources. | Small, 67.0 | 67.0 |
| `customFields` | Map<String, Object> | Details of the custom fields associated with a catalog. | Small, 67.0 | 67.0 |
| `description` | String | Description of the catalog. | Small, 67.0 | 67.0 |
| `effectiveEndDate` | String | Date and time from when the catalog isn’t available to the end users. | Small, 67.0 | 67.0 |
| `effectiveStartDate` | String | Date and time from when the catalog is available to the end users. | Small, 67.0 | 67.0 |
| `id` | String | ID of the catalog. | Small, 67.0 | 67.0 |
| `name` | String | Name of the catalog. | Small, 67.0 | 67.0 |
| `numberOfCategories` | Integer | Number of categories in the catalog. | Small, 67.0 | 67.0 |
| `status` | String | Status of the catalog. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_catalog_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
