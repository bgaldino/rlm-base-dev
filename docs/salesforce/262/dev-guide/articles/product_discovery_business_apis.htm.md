---
page_id: product_discovery_business_apis.htm
title: Product Discovery Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_discovery_business_apis.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_overview.htm
fetched_at: 2026-06-09
---

# Product Discovery Business APIs

Use the Product Discovery Business APIs, which are composite APIs, to search products
or to discover catalogs, products, and categories during the product browsing
experience.

This table lists the available Product Discovery resources.

| Resource | Description |
| --- | --- |
| [`/connect/cpq/catalogs/catalogId`](./connect_resources_catalog_details.htm.md "Get catalog details for a specified catalog ID. This API is a composite API for Product Discovery.") (POST) | Get catalog details for a specified catalog ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/catalogs`](./connect_resources_catalog_list.htm.md "Get a paginated list of catalogs. This API is a composite API for Product Discovery.") (POST) | Get a paginated list of catalogs. This API is a composite API for Product Discovery. |
| [`/connect/cpq/categories`](./connect_resources_categories_list.htm.md "Get a list of categories and subcategories of a specified catalog. This API is a composite API for Product Discovery.") (POST) | Get a list of categories and subcategories of a specified catalog. This API is a composite API for Product Discovery. |
| [`/connect/cpq/categories/categoryId`](./connect_resources_category_details.htm.md "Get details of a category for a specified category ID. This API is a composite API for Product Discovery.") (POST) | Get details of a category for a specified category ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/qualification`](./connect_resources_cpq_qualification.htm.md "Run the qualification procedure on a list of product IDs. This API is a composite API for Product Discovery.") (POST) | Run the qualification procedure on a list of product IDs. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/search`](./connect_resources_global_search.htm.md "Retrieves a list of products based on a search query or search term. This API is a composite API for Product Discovery.") (POST) | Retrieves a list of products based on a search query or search term. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/productId`](./connect_resources_product_details.htm.md "Get product details, such as attributes, hierarchy, or cardinality, for a specified product ID. This API is a composite API for Product Discovery.") (POST) | Get product details, such as attributes, hierarchy, or cardinality, for a specified product ID. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products`](./connect_resources_products_list.htm.md "Get a list of products for a specified catalog, category, or subcategory. This API is a composite API for Product Discovery.") (POST) | Get a list of products for a specified catalog, category, or subcategory. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/bulk`](./connect_resources_bulk_product_details.htm.md "Retrieve details for multiple products. This API is a composite API for Product Discovery.") (POST) | Retrieve details for multiple products. This API is a composite API for Product Discovery. |
| [`/connect/cpq/products/guided-selection`](./connect_resources_guided_product_selection.htm.md "Retrieve a list of products based on the response identifier or search terms of a guided selection. Guided selection captures user requirements to show suitable products.") (POST) | Retrieve a list of products based on the response identifier or search terms of a guided selection. Guided selection captures user requirements to show suitable products. |
| [`/revenue/product-discovery/products/recommendations`](./connect_resources_product_recommendations.htm.md "Get a list of recommended products based on your underlying business rules.") (POST) | Get a list of recommended products based on your underlying business rules. |

- **[Resources](./product_discovery_api_resources.htm.md)**  
  Learn more about the available Product Discovery API resources.
- **[Request Bodies](./product_discovery_api_requests.htm.md)**  
  Learn more about the available Product Discovery API request bodies.
- **[Response Bodies](./product_discovery_api_responses.htm.md)**  
  Learn more about the available Product Discovery API response bodies.
