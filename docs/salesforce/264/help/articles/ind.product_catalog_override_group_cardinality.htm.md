---
article_id: ind.product_catalog_override_group_cardinality.htm
title: Override Group Cardinality
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_override_group_cardinality.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_group_cardinality.htm
fetched_at: 2026-09-04
---

# Override Group Cardinality

You can override the group cardinality of groups that are at the second level and beyond in the product hierarchy. When you override the group cardinality, you update the group cardinality while maintaining a record of the original group cardinality. You can revert to the original cardinality by restoring the default cardinality.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To override group cardinality:	Manage Product Catalog
To use the structure tab:	ARC Access permission set
NOTE Overriding the cardinality overrides the cardinality for the group in the context of the root product bundle. The cardinality of the group remains the same in the context of other product bundles.
WARNING Overriding the group cardinality for a group that’s been added multiple times in a bundle, overrides the group cardinality for every instance of the group throughout the bundle. Groups are added multiple times when the product above the group in the hierarchy is added multiple times.
From the Product Catalog Management app’s home page, click Products.
From the Product list view page click the bundled product that contains the group whose cardinality you want to override.
Navigate to the Structure tab.
Click the group tile for the group at the second level in the product hierarchy.
The first product in the bundle hierarchy is the root product. The products, groups, and product classifications at the first level are the immediate child components of the root product. You can edit the cardinality of products, groups, and product classifications only at the first level. You can override the cardinality of products, groups, and product classifications only at the second level and beyond.
In the right pane, navigate to the Cardinality tab.
Click Override.
Overriding the cardinality overrides the cardinality for the group in the context of the product bundle. The original group cardinality is retained and can be reverted to if necessary.
Override the cardinality as necessary.
This example illustrates the original and updated group cardinality values for the group Wooden Beds at the second level. The original group cardinality was minimum 1 component and maximum 2 components. The updated group cardinality is minimum 0 components and maximum 2 components.
Save your changes
The overridden cardinality appears in the right pane. You can edit the overridden cardinality as necessary.

If you want to revert to the original group cardinality, click Restore Default Cardinality. Restoring the default cardinality deletes the overridden cardinality and restores the original group cardinality.
