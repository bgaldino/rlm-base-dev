---
article_id: ind.product_catalog_product_catalog_management_limits.htm
title: Product Catalog Management Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_catalog_management_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_introduction.htm
fetched_at: 2026-09-04
---

# Product Catalog Management Limits

Before you plan and create products, attributes, and a bundled product hierarchy in Product Catalog Management, make sure that you’re aware of the capabilities and limits.

REQUIRED EDITIONS
View supported products and editions.
Product Classification Limits
You can create up to 10,000 products by using a single product classification.
A product classification hierarchy can have up to 3 levels of subclassifications. At each level, a parent classification can have up to 5 child subclassifications. For example, a root classification such as Electronics can have up to 5 subclassifications (Audio, Video, Computing, Mobile, Accessories), and each of those can have up to 5 subclassifications of its own.
A simple or bundle product can have up to 200 dynamic attributes. As a best practice, limit the attribute count for better performance.
Product Bundle Limits
A product bundle hierarchy can have up to 3 levels of nesting (root product, child group, and nested child group).
A product bundle can have up to 200 bundle components total across all groups and levels.
A bundle includes up to 200 lines, including the root product. This means a single quote line item or order line item for a bundle supports up to 199 associated child items.
A product bundle hierarchy can have up to 600 attribute overrides in total, including all bundle components.
A product bundle hierarchy can have up to 10 product component overrides.
A product bundle hierarchy can have up to 10 group component overrides.
Category and Catalog Limits
A category hierarchy can have up to 5 levels, excluding the root category.
A category can have up to 100,000 products.
You can search catalogs with up to 20 million products using the product field search option.
You can select a combined total of up to 87 searchable and filterable fields and attributes. There is no specific limit for each type, provided the combined total doesn't exceed 87.
You can index up to 1,000,000 products. To increase this limit, contact Salesforce Customer Support.
You can partially index up to 2,000 products.
API Limits
The Bulk Product Details API can take up to 100 product IDs in the request.
NOTE With Indexed product feature enabled, when defining constraints from product definition, the Add Item lookup displays all products as opposed to displaying the current product. You must search for the product to add to the Constraint Model.
Large Transaction Limits
Apex Pricing isn’t supported when using a procedure plan with product discovery.
Qualification within product details is unavailable if the configurator invokes product discovery to retrieve those details.
Large transactions require the use of Product Catalog Management Cache. Because Product Catalog Management Cache doesn’t support localization, your organization can’t have data translation enabled while using Large transactions.
Due to the mandatory use of Product Catalog Management Cache, Field-Level Security (FLS) and Record-Level Security (RLS) aren’t supported in Large transactions.
Large transactions support Advanced decision tables. Modifying the pricing procedure to use Standard or Custom decision tables is unsupported and will cause the procedure to fail.
