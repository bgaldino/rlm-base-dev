---
page_id: product_catalog_management_business_api.htm
title: Product Catalog Management Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_business_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_overview.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Business APIs

Use primitive APIs of Product Catalog Management that serve catalog definitions to
users or applications.

This table lists the available Product Catalog Management resources.

| Resource | Description |
| --- | --- |
| [`/connect/pcm/catalogs`](./connect_resources_get_catalogs.htm.md "Retrieve, search, filter, or sort catalog records.") (POST) | Retrieve, search, filter, or sort catalog records. |
| [`/connect/pcm/catalogs/catalogId`](./connect_resources_get_catalogs_by_ID.htm.md "Retrieve details of catalog records based on a catalog ID.") (GET) | Retrieve details of catalog records based on a catalog ID. |
| [`/connect/pcm/catalogs/catalogId/categories`](./connect_resources_get_categories.htm.md "Retrieve the root-level categories of a catalog based on a catalog ID, or subcategories based on a parent category. You can also search, filter, or sort the categories.") (GET) | Retrieve the root-level categories of a catalog based on a catalog ID, or subcategories based on a parent category. You can also search, filter, or sort the categories. |
| [`/connect/pcm/categories/categoryId`](./connect_resources_get_category_by_ID.htm.md "Retrieve details of individual category records based on a category ID.") (GET) | Retrieve details of individual category records based on a category ID. |
| [`/connect/pcm/products`](./connect_resources_get_products.htm.md "Retrieve products. You can also search, filter, or sort the products.") (POST) | Retrieve products. You can also search, filter, or sort the products. |
| [`/connect/pcm/products/productId`](./connect_resources_get_product_by_ID.htm.md "Retrieve details of individual product records or a bundle based on a product ID.") (GET) | Retrieve details of individual product records or a bundle based on a product ID. |
| [`/revenue/product-catalog-management/product-classifications/details`](./connect_resources_product_classification.htm.md "Retrieve the details for a list of product classification records.") (POST) | Retrieve the details for a list of product classification records. |
| [`/revenue/product-discovery/products/recommendations`](./connect_resources_product_recommendations.htm.md "Get a list of recommended products based on your underlying business rules.") (POST) | Get a list of recommended products based on your underlying business rules. |
| [`/revenue/product-configurator/rules/actions/execute`](./connect_resources_config_rules.htm.md "Run rules for a specific quote or order based on a context ID or transaction ID.") (POST) | This API is used in Product Catalog Management to disable rules, get product recommendations, and get message rules. |
| [`/connect/pcm/products/bulk`](./connect_resources_product_catalog_bulk_product_details.htm.md "Retrieve details for multiple products.") (POST) | Retrieve details for multiple products. |
| `/connect/pcm/index/configurations` (GET, PUT) | Retrieve the saved index configurations. Additionally, you can persist the index configuration. |
| [`/connect/pcm/relatedRecords/entityName`](./connect_resources_related_records.htm.md "Retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object.") (POST) | Retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object. |
| [`/connect/pcm/index/snapshots`](./connect_resources_snapshot_get.htm.md "Retrieve the created snapshots and snapshot indexes.") (GET) | Retrieve the created snapshots and snapshot indexes. |
| [`/connect/pcm/index/deploy`](./connect_resources_snapshot_deploy.htm.md "Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms.") (POST) | Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms. |
| [`/connect/pcm/index/setting`](./connect_resources_get_index_settings.htm.md "Fetch and update settings related to indexing and search.") (GET, PATCH) | Fetch and update settings related to indexing and search. |
| [`/connect/pcm/index/error`](./connect_resources_get_index_errors.htm.md "Get the count and details of the errors that occurred during the indexing process.") (GET) | Get the count and details of the errors that occurred during the indexing process. |
| [`/connect/pcm/deep-clone`](./connect_resources_deep_clone.htm.md "Copy related records of an object along with the main product record.") (POST) | Copy related records of an object along with the main product record. |
| [`/connect/pcm/unit-of-measure/info`](./connect_resources_unit_of_measure_info.htm.md "Get details about the unit of measure for a specific set of records.") (GET) | Get details about the unit of measure for a specific set of records. |
| [`/connect/pcm/unit-of-measure/rounded-data`](./connect_resources_unit_of_measure_rounded_data.htm.md "Round off and scale decimal data for a specific set of fields.") (POST) | Round off and scale decimal data for a specific set of fields. |

- **[Resources](./product_catalog_management_api_resources.htm.md)**  
  Learn more about the available Product Catalog Management API resources.
- **[Request Bodies](./product_catalog_management_api_requests.htm.md)**  
  Learn more about the available Product Catalog Management API request bodies.
- **[Response Bodies](./product_catalog_management_api_responses.htm.md)**  
  Learn more about the available Product Catalog Management API response bodies.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "Connect REST API Developer Guide: Introduction - HTML (New Window)")
