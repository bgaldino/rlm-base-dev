---
article_id: ind.product_catalog_change_a_static_bundle_product_to_a_configurable_bundle_product.htm
title: Change a Static Bundle Product To a Configurable Bundle Product
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_change_a_static_bundle_product_to_a_configurable_bundle_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Change a Static Bundle Product To a Configurable Bundle Product

You can change a static product bundle to a configurable product bundle when you want to configure the bundle during run time. Configurable product bundles have products under a group. Additionally, the parent product is always configurable in the run time.

REQUIRED EDITIONS
View supported products and editions.
USER
PERMISSIONS NEEDED
To convert static bundle to a configurable bundle:	Manage Product Catalog
To use the Structure tab:	ARC Access permission set

To change a static bundle product to a configurable bundle product, these requirements must be met:

All child product components are present under groups and not directly under the root product.
Configure During Sale for the root product is set to Allowed.
From the Product listing page, click the root static bundle product.
Navigate to the Structure tab for this product.
Ensure that all products are under a product group and not directly under the root static product.
From the Structure tab, add a Product Group component under the root bundle product.
Click every product that is directly under the root product.
In the right panel, click Edit Relationship.
On the Edit PRC page, in the Group field, select the newly created product group or another group to which this product can be added.
Save the changes.
Perform these steps for all the products that are directly under the root product and not under a group.
Refresh the Structure tab.
Ensure that all products are now under groups.
Finally, edit the root product bundle.
Change the value of Configure During Sale to Allowed.
Save your changes.
