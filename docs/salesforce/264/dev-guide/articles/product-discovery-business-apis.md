---
page_id: product-discovery-business-apis
title: Product Discovery Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-discovery-business-apis.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-overview
legacy_page_id: product_discovery_business_apis.htm
fetched_at: 2026-11-25
---

# Product Discovery Business APIs

Use the Product Discovery Business APIs, which are composite APIs, to search products or to discover catalogs, products, and categories during the product browsing experience.

This table lists the available Product Discovery resources.

| Resource | Description |
| --- | --- |
| [`/connect/cpq/catalogs/{catalogId}`](./connect-resources-catalog-details.md) (POST) | Get catalog details for a specified catalog ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/catalogs`](./connect-resources-catalog-list.md) (POST) | Get a paginated list of catalogs. This API is a composite API for Product Discovery. |
| [`/connect/cpq/categories`](./connect-resources-categories-list.md) (POST) | Get a list of categories and subcategories of a specified catalog. This API is a composite API for Product Discovery. |
| [`/connect/cpq/categories/{categoryId}`](./connect-resources-category-details.md) (POST) | Get details of a category for a specified category ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/qualification`](./connect-resources-cpq-qualification.md) (POST) | Run the qualification procedure on a list of product IDs. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/search`](./connect-resources-global-search.md) (POST) | Retrieves a list of products based on a search query or search term. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/{productId}`](./connect-resources-product-details.md) (POST) | Get product details, such as attributes, hierarchy, or cardinality, for a specified product ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products`](./connect-resources-products-list.md) (POST) | Get a list of products for a specified catalog, category, or subcategory. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/bulk`](./connect-resources-bulk-product-details.md) (POST) | Retrieve details for multiple products. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/guided-selection`](./connect-resources-guided-product-selection.md) (POST) | Retrieve a list of products based on the response identifier or search terms of a guided selection. Guided selection captures user requirements to show suitable products. |
| [`/revenue/product-discovery/products/recommendations`](./connect-resources-product-recommendations.md) (POST) | Get a list of recommended products based on your underlying business rules. |

- 

**[Resources](./product-discovery-api-resources.md)**

Learn more about the available Product Discovery API resources.

- 

**[Request Bodies](./product-discovery-api-requests.md)**

Learn more about the available Product Discovery API request bodies.

- 

**[Response Bodies](./product-discovery-api-responses.md)**

Learn more about the available Product Discovery API response bodies.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-discovery-business-apis.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
