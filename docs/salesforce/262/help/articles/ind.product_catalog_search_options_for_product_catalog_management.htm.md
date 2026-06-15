---
article_id: ind.product_catalog_search_options_for_product_catalog_management.htm
title: Search Options in Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_search_options_for_product_catalog_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Search Options in Product Catalog Management

Product Catalog Management gives your sales reps three search options to quickly find the products in a catalog. They can choose the search option based on its search capabilities and the size of the product catalog.

REQUIRED EDITIONS
View supported products and editions.

The search options are Salesforce Object Query Language (SOQL) search, Indexed search, and Product field search (SOSL based).

SOQL based search: This option is suitable for simple product searches. It can search for products by term, and it has a quick find feature within the transaction line table (such as a specific UI element). The search API supports filtering by ‌standard and custom Product2 fields.

Indexed search: This option provides comprehensive search capabilities, including configurable term-based search across various product fields, product attributes, faceted search, guided product selection (question-based), and quick find.

Product field search (SOSL): This option is suitable for large product catalogs (over 4 million products),This option searches across text-indexed fields of the product object, including key fields such as product name, description, product code, and SKU

CAPABILITY	SOQL BASED SEARCH	INDEXED SEARCH	PRODUCT FIELD SEARCH
Catalog size	Less than or equal to 250,000 products.	Less than or equal to 4 million products.	More than 4 million products and up to 20 million products. 
Setup	Not Required	Required	Required
Supported capabilities	Term-based search by product name	
Faceted search
Full and partial indexing
Search index configuration
Term-based search for product fields or attributes
Guided product selection
	Term-based search by product fields such as name, description, product code, and SKU.
Unsupported Capabilities	
Faceted search
Attribute- based search
Guided product selection
Search by translated product name
	Search by translated, searchable, and filterable field or attribute values.	
Faceted search
Attribute -based search
Guided product selection
Search by translated product name and description
Product Field Search in Product Catalog Management
Sales reps can use the Product field search option to quickly locate specific products within large catalogs (millions of products) by searching text-indexed fields such as Product Name, Description, Product Code, and SKU.
Product Index and Search in Product Catalog Management
Enable sales reps to find products quickly and easily with an index of all the products available across catalogs. Specify searchable fields and attributes that users can use to search the index for products.
Semantic Search
Semantic search reduces “no results found” pages, lowers bounce rates, and improves conversions by interpreting search intent. It matches product names, descriptions, categories, and dynamic attributes based on the words that buyers enter in the search bar.
