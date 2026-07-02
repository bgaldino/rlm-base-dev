---
article_id: ind.product_catalog_product_catalog_management_limits.htm
title: Product Catalog Management Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_catalog_management_limits.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Product Catalog Management Limits

Before you plan and create products, attributes, and a bundled product hierarchy in Product Catalog Management, make sure that you’re aware of the capabilities and limits.

REQUIRED EDITIONS
View supported products and editions.
You can create up to 10,000 products by using a single product classification.
A simple or bundle product can have up to 200 dynamic attributes. As a best practice, we recommend that you limit the attribute count for better performance.
A product bundle hierarchy can have up to three levels, where a parent can have up to five child nodes at a given level.
A product bundle hierarchy can have up to 600 attribute overrides in total, including all bundle components.
A product bundle hierarchy can have up to 10 product component overrides.
A product bundle hierarchy can have up to 10 group component overrides.
A category can have a up to 100,000 products.
The Bulk Product Details API can take up to 100 product IDs in the request.
A category hierarchy can have up to 5 levels, excluding the root category.
You can select a combined total of up to 87 searchable and filterable fields and attributes. There is no specific limit for each type, provided the combined total doesn't exceed 87.
You can search catalogs with up to 20 million products using the product field search option.
You can index up to 1,000,000 products. To increase this limit, contact Salesforce Customer Support.
You can partially index up to 2,000 products.
With Indexed product feature enabled, when defining constraints from product definition, the Add Item lookup displays all products as opposed to displaying the current product. You must search for the product to add to the Constraint Model.
NOTE We recommend that you add no more than 200 bundle components to a product bundle hierarchy.
