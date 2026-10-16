---
article_id: ind.product_catalog_bundled_product_validations.htm
title: Manage Validations for Product Bundles
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_bundled_product_validations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_create_bundled_products.htm
fetched_at: 2026-09-04
---

# Manage Validations for Product Bundles

As product bundles grow over time, tracking the number of components and ensuring that every component meets the cardinality and structural requirements can become challenging. Validate Product Definition runs on-demand checks against your entire bundled product to ensure compliance. The validations also suggest corrective actions to help maintain the integrity and accuracy of your product configurations.

REQUIRED EDITIONS
View supported products and editions.
Configurable Product Validations

Here’s what’s validated for configurable parent products:

The number of products in a group must be greater than or equal to the minimum number of components in the group.
The number of required products in a group must be less than or equal to the maximum number of components in the group.
The number of child groups under a parent group must be greater than or equal to the minimum number of components in the parent group.
The number of child groups that have required product components must be less than or equal to the maximum number of components in the parent group.
EXAMPLE Consider a parent group PG that has this cardinality:
Minimum number of components: 2
Maximum number of components: 4

The parent group has only one child group CG1.

The validation fails because the parent group must have a minimum of 2 child groups but only one child group exists.

EXAMPLE Consider a parent group PG that has this cardinality:
Minimum number of components: 1
Maximum number of components: 1

The parent group has two child groups with these components:

Child group CG1 has one optional product
Child group CG2 has one optional product

The validation succeeds because both the child groups have optional products, and users can select a product from either of these groups at runtime. The number of required products is 0, which is less than the maximum number of components in the group, which is 1.

EXAMPLE Consider a parent group PG that has this cardinality:
Minimum number of components: 1
Maximum number of components: 1

The parent group has two child groups with these components:

Child group CG1 has one required product
Child group CG2 has one required product

The validation fails because both the child groups have required products. The number of required products in a group is 2, which is greater than the maximum number of components in the group, which is 1.

Example of a Static Product Validation

Here’s what’s validated for static parent products:

The default number of components in a group must be greater than or equal to the minimum number of components in the group.
The default number of components must be less than or equal to the maximum number of components in the group.
The number of child groups under a parent group must be greater than or equal to the minimum number of components in the parent group.
The number of child groups under a parent group must be less than or equal to the maximum number of components in the parent group.
EXAMPLE Consider a parent group PG that has this cardinality:
Minimum number of components: 2
Maximum number of components: 5

The parent group has two child groups with these components:

Child group CG1 has one required product.
Child group CG2 has one optional product.

The validation succeeds because the number of child groups under PG is equal to the minimum number of components but less than the maximum number of components.

Validate the Product Definition
Use Validate Product Definition to check the integrity of your product bundles.
