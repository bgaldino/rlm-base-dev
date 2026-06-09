---
page_id: connect_responses_catalog_output.htm
title: Catalog Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_catalog_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Catalog Output

Output representation of the catalog definition.

JSON example
:   ```
    catalogs": [
        {
          "catalogType": "Sales",
          "code": "CAT009",
          "description": "SmartBytes B2B Catalog",
          "effectiveEndDate": "31-07-2023",
          "effectiveStartDate": "24-07-2023",
          "id": "0ZS1Q000000XbZAWA0",
          "name": "SmartBytes B2B Catalog",
          "numberOfCategories": 8
        }
    ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalog​Type` | String | The category of an entry in the catalog, which is customizable. For example, catalog types, such as sellable products, services, parts, technical services, or technical resources. | Small, 60.0 | 60.0 |
| `code` | String | Unique ID associated with the catalog. | Small, 60.0 | 60.0 |
| `description` | String | Description of the catalog. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `effective​EndDate` | String | Date and time from when the catalog isn't available to the end users. | Small, 60.0 | 60.0 |
| `effective​Start​Date` | String | Date and time from when the catalog is available to the end users. | Small, 60.0 | 60.0 |
| `id` | String | ID of the catalog. | Small, 60.0 | 60.0 |
| `name` | String | Name of the catalog. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `numberOf​Categories` | Integer | Number of categories in the catalog. | Small, 60.0 | 60.0 |
