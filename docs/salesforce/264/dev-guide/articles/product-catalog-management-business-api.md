---
page_id: product-catalog-management-business-api
title: Product Catalog Management Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-business-api.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-overview
legacy_page_id: product_catalog_management_business_api.htm
fetched_at: 2026-11-25
---

# Product Catalog Management Business APIs

Use primitive APIs of Product Catalog Management that serve catalog definitions to users or applications.

This table lists the available Product Catalog Management resources.

| Resource | Description |
| --- | --- |
| [`/connect/pcm/catalogs`](./connect-resources-get-catalogs.md) (POST) | Retrieve, search, filter, or sort catalog records. |
| [`/connect/pcm/catalogs/{catalogId}`](./connect-resources-get-catalogs-by-id.md) (GET) | Retrieve details of catalog records based on a catalog ID. |
| [`/connect/pcm/catalogs/{catalogId}/categories`](./connect-resources-get-categories.md) (GET) | Retrieve the root-level categories of a catalog based on a catalog ID, or subcategories based on a parent category. You can also search, filter, or sort the categories. |
| [`/connect/pcm/categories/{categoryId}`](./connect-resources-get-category-by-id.md) (GET) | Retrieve details of individual category records based on a category ID. |
| [`/connect/pcm/products`](./connect-resources-get-products.md) (POST) | Retrieve products. You can also search, filter, or sort the products. |
| [`/connect/pcm/products/{productId}`](./connect-resources-get-product-by-id.md) (GET) | Retrieve details of individual product records or a bundle based on a product ID. |
| [`/revenue/product-catalog-management/product-classifications/details`](./connect-resources-product-classification.md) (POST) | Retrieve the details for a list of product classification records. |
| [`/revenue/product-discovery/products/recommendations`](./connect-resources-product-recommendations.md) (POST) | Get a list of recommended products based on your underlying business rules. |
| [`/revenue/product-configurator/rules/actions/execute`](./connect-resources-config-rules.md) (POST) | This API is used in Product Catalog Management to disable rules, get product recommendations, and get message rules. |
| [`/connect/pcm/products/bulk`](./connect-resources-product-catalog-bulk-product-details.md) (POST) | Retrieve details for multiple products. |
| [`/connect/pcm/products/variants`](./connect-resources-product-variants.md) (POST) | Retrieve the variation product associated with one or more parent variant products. |
| [`/connect/pcm/index/configurations`](./connect-resources-index-configuration.md) (GET, PUT) | Retrieve the saved index configurations. Additionally, you can persist the index configuration. |
| [`/connect/pcm/relatedRecords/{entityName}`](./connect-resources-related-records.md) (POST) | Retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object. |
| [`/connect/pcm/index/snapshots`](./connect-resources-snapshot-get.md) (GET) | Retrieve the created snapshots and snapshot indexes. |
| [`/connect/pcm/index/deploy`](./connect-resources-snapshot-deploy.md) (POST) | Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms. |
| [`/connect/pcm/index/setting`](./connect-resources-get-index-settings.md) (GET, PATCH) | Fetch and update settings related to indexing and search. |
| [`/connect/pcm/index/error`](./connect-resources-get-index-errors.md) (GET) | Get the count and details of the errors that occurred during the indexing process. |
| [`/connect/pcm/deep-clone`](./connect-resources-deep-clone.md) (POST) | Copy related records of an object along with the main product record. |
| [`/connect/pcm/unit-of-measure/info`](./connect-resources-unit-of-measure-info.md) (GET) | Get details about the unit of measure for a specific set of records. |
| [`/connect/pcm/unit-of-measure/rounded-data`](./connect-resources-unit-of-measure-rounded-data.md) (POST) | Round off and scale decimal data for a specific set of fields. |

- 

**[Resources](./product-catalog-management-api-resources.md)**

Learn more about the available Product Catalog Management API resources.

- 

**[Request Bodies](./product-catalog-management-api-requests.md)**

Learn more about the available Product Catalog Management API request bodies.

- 

**[Response Bodies](./product-catalog-management-api-responses.md)**

Learn more about the available Product Catalog Management API response bodies.

**See Also**

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-business-api.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
