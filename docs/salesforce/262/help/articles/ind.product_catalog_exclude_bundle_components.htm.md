---
article_id: ind.product_catalog_exclude_bundle_components.htm
title: Exclude Bundle Components From Product Selection at Run Time
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_exclude_bundle_components.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Exclude Bundle Components From Product Selection at Run Time

To make certain products, groups, or classifications unavailable for selection at run time, you can exclude them from the product bundle. This exclusion doesn’t delete the product, it only hides the product from the user at run time. Exclusions are in the context of the root product bundle that you’re in.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To exclude components:	Manage Product Catalog
To use the structure tab:	ARC Access permission set

Excluding products is useful when you need to temporarily restrict a product from being sold, while still keeping it as part of the bundle for use later. Once the restriction period ends, a product manager can restore the product's availability.

For example, a medical device manufacturer sells a patient monitoring system including sensors, a display unit, and connection cables. If there's an unexpected disruption in the supply chain for a specific type of connection cable, the product manager can temporarily exclude that cable component from the bundle configuration. This prevents sales reps from quoting systems that cannot be fully fulfilled due to the supply shortage.

To exclude a bundle component from product selection at run time, follow these instructions:

From the Product Catalog Management app’s home page, click Products.
From the Product list view page, click the bundled product that contains the group or product component that you want to exclude from the product bundle.
Go to the Structure tab.
Click the product tile, product classification tile, or the group tile at the second level in the product hierarchy.
The first product in the bundle hierarchy is the root product. The products and groups at the first level are the immediate child components of the root product. You can exclude products, product classifications, and groups from the second level in the product hierarchy and beyond.
Click .
Excluding a group automatically excludes all the components under that group.
NOTE You can’t edit or override the cardinality of an excluded component.

To include an excluded product or group, click Restore Default Cardinality. You can also click the  to include the product or group.
