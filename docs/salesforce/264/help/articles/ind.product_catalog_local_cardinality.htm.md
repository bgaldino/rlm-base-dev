---
article_id: ind.product_catalog_local_cardinality.htm
title: Manage Local Cardinality
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_local_cardinality.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_local_cardinality_and_group_cardinality.htm
fetched_at: 2026-09-04
---

# Manage Local Cardinality

Use local cardinality to define if a product component or products based on a product classification are required, are included in the bundle by default, whether their quantities can be changed, and what the minimum and maximum quantities are.

REQUIRED EDITIONS
View supported products and editions.

Here are the available cardinality fields:

CARDINALITY FIELDS	DESCRIPTION
Require this component	Select if the product component is a required component in the product bundle. Deselect if the product component is an optional component in the product bundle. If Require this component is selected, ensure that you select Include component by default. Ensure that Require this component is deselected for a product classification components.
Include component by default	Select if the product component is included in the product bundle by default. Deselect if the product component isn’t included in the product bundle by default. You must select this field if the product component is a required component. Ensure that Include component by default is deselected for product classification components.
Allow quantity changes	

Select if users can edit the product quantity at run time.

If Allow Quantity Changes is deselected, you can’t enter a minimum quantity and maximum quantity.
If the Price includes component field in the product related component record is selected, then you must deselect Allow quantity changes.
NOTE If the product's Quantity Scaling Method is set to Proportional, selecting this checkbox makes the quantity editable, but only when configuring the product in the configurator. Once added to a quote, the quantity field is locked (read-only) in the sales transaction line editor. This happens because the line editor displays the final multiplied quantity stored on the quote line item, rather than the editable per-parent unit quantity.

Price Includes Component	Select when the price of the product bundle includes the price of the component. You can’t change component quantities when you select Price Includes Component.
Quantity Scaling Method	

Defines how the child product quantity changes as the quantity of the parent product changes in the runtime cart. This field can have these values:

None: To change the quantity values of the child product in the run time irrespective of the quantity of the parent product, select Allow Quantity Changes. Deselect Allow Quantity Changes to restrict changes to the quantity values of the child product in the run time irrespective of the quantity of the parent product.
Constant:
The quantity of the child product in the runtime cart remains constant irrespective of the changes to the parent product quantity when the Quantity Scaling Method is set to Constant. You can’t change the child product quantity in runtime. The child product quantity value remains what was defined in design time in Product Catalog Management.
You must deselect Allow Quantity Changes when the Quantity Scaling Model is set to Constant.
Proportional:
This is the default value for the Quantity Scaling Method when Allow Quantity Changes isn’t selected in the Specify Component Details window. The Quantity Scaling Method is set to None when the Allow Quantity Changes is selected in the Specify Component Details window.
When the Quantity Scaling Method is set to Proportional, the quantity of the child product in the runtime cart changes in proportion to the changes to the parent product quantity. For example, if the parent product quantity is A and the child product quantity is B, then the runtime cart has A number of parent products, but A multiplied by B number of child products.

Min Quantity	The minimum number of product components or products based on a product classification in the bundle.
Max Quantity	The maximum number of product components or products based on a product classification in the bundle.
Quantity	The default number of product components or products based on a product classification in the bundle.
Edit Local Cardinality
To define the default, minimum, and maximum quantity of a product that’s permissible in the product bundle, edit the local cardinality of the product component and the product classification component.
Override Local Cardinality
You can override the cardinality of product components and product classification components that are at the second level and beyond in the product hierarchy. When you override the local cardinality, you update the product component or product classification component cardinality while maintaining a record of the original local cardinality. You can revert to the original cardinality by restoring the default cardinality.
