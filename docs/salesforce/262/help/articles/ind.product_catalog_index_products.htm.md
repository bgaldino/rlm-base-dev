---
article_id: ind.product_catalog_index_products.htm
title: Manage Your Product Index
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_index_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Manage Your Product Index

To utilize product search and discoverability, you must maintain an accurate index of the product fields and attributes in your product catalog.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To build and rebuild indexes:	

Manage Product Index and Search

AND

View Product Catalog

Rebuild your index whenever you add, change, or remove items. There are two index rebuild options: Full and Partial.

Use the Full Index Rebuild to rebuild the entire search index, including changes to index settings and structural changes. Use the Partial Index Rebuild to update recent changes to products and assignment categories.

To help you decide when to run a Full or Partial index, refer to the scenarios listed in the table.

Changes	Full Index Rebuild	Partial Index Rebuild
Modification of the Manage Fields & Attributes tab in the search configuration.	Applicable	Not Applicable
Modification of the Index Settings tab for localization, such as updating the supported and default languages.	Applicable	Not Applicable
Modification to the Product Specification Type and the Product Specification Record Type.	Applicable	Not Applicable
Modification to the Attribute Picklist value when configured with the Attribute Definition.	Applicable	Not Applicable
Modification of the Data Translation settings.	Applicable	Not Applicable
Attribute values, such as overriding the picklist values, changing the default values, excluding the picklist values, etc.	Applicable	Applicable
Modification of the product field values.	Applicable	Applicable
Modification of the attribute values, such as overriding the picklist values, changing the default values, excluding the picklist values, and etc.	Applicable	Applicable
Modification of the product category assignments.	Applicable	Applicable
Modification of the product data translation values.	Applicable	Applicable

By default, you can fully index up to 1,000,000 products and you can partially index up to 2,000 products.

When you rebuild the search index, consider these factors.

If the indexing excludes some products because the individual product size exceeds the limit, contact Salesforce Customer Support.
You can rebuild the search index up to 60 times per hour. We recommend you to wait at least 5 minutes between full index rebuilds.
After you initiate a rebuild of an index, we recommend that you wait a few minutes before initiating another rebuild. Rebuilding indexes too quickly results in an error.

To get started with your product index, follow these instructions:

Build the Product Index
Rebuild the index every time you add or remove products, change product information, or change search options so that the data accessible to run-time systems is up to date. When the rebuilding is in progress, Product Catalog Management continues to use the existing index. Product Catalog Management uses the updated index only after the index rebuild process is complete.
Product Catalog Index Errors and Troubleshooting
Updating the index can, at times, cause errors in products or even index failures. On the Indexes page of the Index and Search Configuration tile, review the different error scenarios and the corresponding actions you can take when updating the index.
Configure Search Index Localization
Localize your search by configuring the index settings. Choose supported languages and set the default language for your search index.
