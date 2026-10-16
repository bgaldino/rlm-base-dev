---
article_id: ind.product_catalog_nested_group_cardinality_and_product_classification_component_cardinality.htm
title: Nested Group Cardinality and Product Classification Component Cardinality
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_nested_group_cardinality_and_product_classification_component_cardinality.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_group_cardinality.htm
fetched_at: 2026-09-04
---

# Nested Group Cardinality and Product Classification Component Cardinality

You can add product classification components only under a product group component. The product group component and the product classification component each have their own cardinalities.

Here's an example that demonstrates how the group, nested group, and product classification cardinality determine how many products you can add in your cart at run time.

In this example, we have a parent group called Wardrobes. Mirrored Wardrobes, Sliding Wardrobes, Open Wardrobe, Fitted Wardrobe, and Corner Wardrobe are child groups of the Wardrobes parent group. Here's the cardinality of the Wardrobes parent group:

Minimum number of components: 1
Maximum number of components: 4

At run time, users can select products from a minimum of 1 child group and select products from a maximum of 4 child groups from the 5 available child groups. Let’s assume that a user selects the Mirrored Wardrobes child group.

Mirrored Wardrobes is a nested child group. This nested group has a product classification called Mirrored Wardrobes. Double-door wardrobe, three-door wardrobe, four-door sliding wardrobe, and four-door swing wardrobe are four products based on the Mirrored Wardrobe product classification.

Here's the cardinality for the Mirrored Wardrobes product classification:

Minimum number of components: 2
Maximum number of components: 4

At run time, users can select a minimum of 2 products based on the product classification and a maximum of 4 products. Let’s assume that a user selects the double-door wardrobe and the four-door swing wardrobe.

Mirrored Wardrobe Classification (Product Classification Component)

Minimum Quantity: 1
Maximum Quantity: 2
Default Quantity: 1

At run time, users can select a minimum of one instance of the product and a maximum of 2 instances of the product. That means that a user can select a minimum of 1 double-door wardrobe and a maximum of 2 double-door wardrobes. Similarly, the user can select a minimum of 1 four-door swing wardrobe and a maximum of 2 four-door swing wardrobes.
