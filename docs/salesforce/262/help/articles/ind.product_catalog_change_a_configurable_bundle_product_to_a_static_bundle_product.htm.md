---
article_id: ind.product_catalog_change_a_configurable_bundle_product_to_a_static_bundle_product.htm
title: Change a Configurable Bundle Product to a Static Bundle Product
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_change_a_configurable_bundle_product_to_a_static_bundle_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Change a Configurable Bundle Product to a Static Bundle Product

You can change a configurable bundle product to a static product bundle when you don’t want to configure the bundle during run time. You can't configure products in a static product bundle during run time. Every bundle component is present in the bundle by default and can’t be removed. You can’t change the child component quantity in the run time. Every attribute of every product component has a default value.

REQUIRED EDITIONS
View supported products and editions.
USER
PERMISSIONS NEEDED
To convert bundled products from configurable to static:	Manage Product Catalog
To use the Structure tab:	ARC Access permission set

To change a configurable bundle product to a static bundle product, these requirements must be met:

All root and child product attributes have default values.
Configure During Sale for the root product and every child product is set to Not Allowed or None.
Include component by default is selected for every child product.
Allow Quantity Changes is deselected for every child product component.
Product classification components must not exist in the configurable product bundle.
From the Product listing page, click the root configurable bundle product.
Navigate to the Attributes tab for this product.
Ensure that every inherited and configured attribute for all product components in the bundle has a default value.
From the Inherited Attributes section, configure every attribute, and enter a default value for attributes that don’t have one.
Save your changes.
From the Overridden Inherited Attributes related list, edit every attribute, and enter a default value for attributes that don’t have one.
Save your changes.
Perform these steps for all product components in this configurable bundle.
Navigate to the Structure tab for the root configurable bundle product.
Ensure that every child product component is static.
Click the name of every product child component.
From the Product page, edit the product.
Change the value of the ConfigureDuringSale field to Not Allowed or None.
Save your changes.
Set the ConfigureDuringSale field of every child product of this product component to Not Allowed or None. You can access the child components of this product component from its Structure tab.
Ensure that there are no product classification components in the bundle hierarchy.
Click the Product Classification component tile.
Click Delete. 
Perform these steps for every product component in the bundle:
Navigate to the Structure tab of the root configurable product.
Click every product component tile.
In the right panel, navigate to the Cardinality tab.
Select Include component by default.
Deselect Allow Quantity Changes.
Save your changes.
Finally, edit the root product bundle.
To change the root product to type static, change the value of Configure During Sale to Not Allowed or None.
Save your changes.

After you convert the configurable product bundle to a static product bundle, click Validate Product Definition to determine if the static bundle has any product components without default attribute values. If the validation results return such attributes, assign a default value to each of them and validate the product definition again.
