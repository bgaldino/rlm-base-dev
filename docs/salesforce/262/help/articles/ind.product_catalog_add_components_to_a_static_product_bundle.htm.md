---
article_id: ind.product_catalog_add_components_to_a_static_product_bundle.htm
title: Add Components to a Static Product Bundle
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_add_components_to_a_static_product_bundle.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Add Components to a Static Product Bundle

Static products are non-configurable at run time. That means you can’t add or remove child products, alter product quantities, or configure product attributes at run time. You can add product and product group components to a static product bundle. Product Group components are optional.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create bundled products:	Manage Product Catalog
To use the Structure tab:	ARC Access permission set
IMPORTANT When you add a product under a new static bundle, ensure that you select None under the parent product selling model. Additionally, don’t select any component selling model.
You can optionally add Product Group (1) components to the static bundle hierarchy.
If you delete a group, all components under the group, such as products and product classifications, are deleted.
Add only static simple products or static bundled products as child components of static bundled products. You can’t add configurable simple products or configurable bundle products as child components of static bundled products.
When you add child components to a static product bundle, make sure that the field Include component by default is selected on the child components. Also ensure that the field Allow Quantity Changes isn’t selected on the child components.
If your static simple product is based on a product classification, then all attributes for all components in the static bundle must have default values.
When adding a child component with a defined unit of measure to a static product bundle, the Quantity, Min Quantity, and Max Quantity fields automatically inherit the scaling and rounding method of the child component.
From the Product Catalog Management app’s home page, click Products.
From the product list view page, click the static bundle product.
Navigate to the Structure tab.
Click the plus icon under the root product, and select Product or Product Group. Product groups are optional in a static bundle hierarchy.
To add a group, specify these details:
Enter a group name and description.

If you’re adding this group directly under the root product, the parent group field is blank. If this group is a nested group, then the parent group is the group under which you’re adding this group.

Enter the minimum and maximum number of product components that users can select in runtime.
Save your changes.
To add a product, specify these details:
Select None under parent product selling model, and click Next.
Select one or more static simple or static bundle products, and click Next.
If necessary, change the default product quantity.
Don’t select any component selling model.

If you’re adding the product under the root product, leave the Group field blank. If you’re adding the product under a group, the Group field contains the group name.

To make the component a required component in the bundle, select Require this component.
If a component is required, the Structure tab shows a solid line between the parent component and child component. If the component is optional, the Structure tab shows a dotted line between the parent component and the child component.
Ensure that Include component by default is selected.
It’s mandatory to include the product component in the static bundle by default.
Ensure that Allow quantity changes is deselected.
When Allow Quantity Changes is deselected, you can’t enter a minimum and maximum quantity.
If the price of the bundled product includes the price of this product component, select Price Includes component. In this case, ensure that you deselect Allow quantity changes.
Save your changes.
