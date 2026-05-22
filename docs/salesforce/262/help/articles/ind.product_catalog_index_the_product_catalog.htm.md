---
article_id: ind.product_catalog_index_the_product_catalog.htm
title: Build the Product Index
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_index_the_product_catalog.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Build the Product Index

Rebuild the index every time you add or remove products, change product information, or change search options so that the data accessible to run-time systems is up to date. When the rebuilding is in progress, Product Catalog Management continues to use the existing index. Product Catalog Management uses the updated index only after the index rebuild process is complete.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To build and rebuild indexes:	

Manage Product Index and Search

AND

View Product Catalog

NOTE If the index rebuild fails, Product Catalog Management continues to use the active index.
From the Product Catalog Management app’s home page, click Index and Search Configuration.

To index the product catalog for the first time, click Create Full Index.

To rebuild the index after a change to product data or search configuration, click Rebuild Index.
Select index rebuilding option, and click Rebuild.

Each time you rebuild the full or partial index, a new log entry is added to the Rebuild History section, enabling the user to track the rebuild activity. The Build Status will show In Progress for the duration of the rebuild operation. Once the index operation is successful, click the Refresh icon to view the modifications in the Rebuild History section. You can view the Activation Status in the Index Summary section.

Starting a partial or full index rebuild cancels any rebuilds that are in progress and initiates a new index rebuild.

SEE ALSO
Product Catalog Index Errors and Troubleshooting
