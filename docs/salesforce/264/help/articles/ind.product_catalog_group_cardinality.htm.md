---
article_id: ind.product_catalog_group_cardinality.htm
title: Manage Group Cardinality
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_group_cardinality.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_local_cardinality_and_group_cardinality.htm
fetched_at: 2026-09-04
---

# Manage Group Cardinality

Bundled products are grouped under product groups. You can control the number of components that can be added to the bundle hierarchy in the runtime through product group cardinality.

REQUIRED EDITIONS
View supported products and editions.

Group cardinality defines the minimum and maximum number of child components that users can add at run time. Add a nested child group, a product classification, or multiple product components to a root group.

With nested groups, the cardinality of the parent group defines the minimum and maximum number of child groups from which users can select products at run time. When the nested group contains a product classification, the nested group cardinality dictates the minimum and maximum number of product classification-based products that your users can add at run time.

IMPORTANT When you use nested groups, the cardinality of groups that contain child groups isn’t enforced at run time. Only the cardinality of the group at the lowest-level is enforced at run time.

When the nested group contains products, the cardinality of the nested group defines the minimum and maximum number of products that users can select at run time.

Here are the available group cardinality options.

FIELD	DESCRIPTION
Max Number of Components	The maximum number of distinct components in the group that users can add to the run-time cart.
Min Number of Components	The minimum number of distinct components in the group that users you can add to the run time cart.
NOTE The maximum number of components must be greater than or equal to the minimum number of components.
Edit Group Cardinality
Edit group cardinality to change the minimum and maximum number of distinct components in the group that users can add to the run-time cart.
Override Group Cardinality
You can override the group cardinality of groups that are at the second level and beyond in the product hierarchy. When you override the group cardinality, you update the group cardinality while maintaining a record of the original group cardinality. You can revert to the original cardinality by restoring the default cardinality.
Nested Group Cardinality and Product Classification Component Cardinality
You can add product classification components only under a product group component. The product group component and the product classification component each have their own cardinalities.
Group Cardinality Examples
To better understand how group cardinality works in Product Catalog Management, refer to these examples.
