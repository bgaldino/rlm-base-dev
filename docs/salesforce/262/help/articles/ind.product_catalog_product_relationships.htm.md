---
article_id: ind.product_catalog_product_relationships.htm
title: Product Relationship Management in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_relationships.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Product Relationship Management in Agentforce Revenue Management

Bundle products consist of components such as groups, products, and product classifications. These components are related to each other through product relationships.

REQUIRED EDITIONS
View supported products and editions.

The first product in a product hierarchy is the root product (1). All components added to the root product are its children (2).

A root product can have multiple root groups or multiple products as its immediate level-one child components. A root group can have either multiple child groups, or multiple products, or a single product classification component as its immediate child component.

You define a Product Relationship Type when you add a product or a product classification component to a bundle.

Specify Component Detail Fields
FIELD	DESCRIPTION
Child Product	The name of the child product that you add to the bundle. This field is empty when you add a product classification to a group.
Child Product Classification	The name of the product classification that you add to a group. This field is empty when you add products to a group.
Sequence	The display order of the product in the run-time cart
Quantity	The default quantity of the product or products based on the product classification in the run-time cart
Product Relationship Type	When you add a product, the product relationship type is Bundle to Bundle Component Relationship. When you add a product classification, the product relationship type is Bundle to Product Classification Component Relationship
Group	The group under which you add the product or product classification
Require this component	To make the product a required component in the bundle, select Require this component. Ensure that Require this component is deselected for product classification components.
Include component by default	To include the product in the bundle by default, select Include component by default. Ensure that Include component by default is deselected for product classification components.
Allow Quantity Changes	To allow users to change product quantities during run time, select Allow quantity changes. If Allow Quantity Changes is deselected, you can’t enter a minimum and maximum quantity
Min Quantity	The minimum number of products that you can select in the bundle at run time
Max Quantity	The maximum number of products that you can select in the bundle at run time
Additional Product-Related Component Fields

To edit the product relationship, click the product tile from the Structure tab and click Edit Relationship under the Relationship tab in the right pane.

FIELD	DESCRIPTION
Component Selling Model	
Don’t select a component selling model for products added under a new static bundle. The parent selling model for these products must be none.
Don’t select a component selling model for configurable bundles.

Quantity Scaling Method	

Defines how the child product quantity changes as the quantity of the parent product changes in the runtime cart. This field can have these values:

None: Select Allow Quantity Changes to change the quantity values of the child product in the run time, irrespective of the quantity of the parent product. Deselect Allow Quantity Changes to restrict changes to the quantity values of the child product in the run time irrespective of the quantity of the parent product.
Constant:
The quantity of the child product in the runtime cart remains constant irrespective of the changes to the parent product quantity when the Quantity Scaling Method is set to Constant. You can’t change the child product quantity in the runtime. The child product quantity value remains what was defined in the design time in Product Catalog Management.
You must deselect Allow Quantity Changes when the Quantity Scaling Model is set to Constant.
Proportional:
This is the default value for the Quantity Scaling Method when you don’t select Allow Quantity Changes in the Specify Component Details window. The Quantity Scaling Method is set to None when you select Allow Quantity Changes in the Specify Component Details window.
When the Quantity Scaling Method is set to Proportional, the quantity of the child product in the runtime cart changes in proportion to the changes to the parent product quantity. For instance, if the parent product quantity is A and the child product quantity is B, then the runtime cart has A number of parent products, but A multiplied by B number of child products.

Quote Visibility	

The value in this field controls whether a child product is shown in Transaction Line Editor, quote documents, both, or neither:

Always: To show the child product in both Transaction Line Editor and quote documents.
Never: To hide the child product in both Transaction Line Editor and quote documents.
Transaction Line Editor Only
Quote Document Only

If you don’t select a value, child products appear in quotes and quote documents.

If you hide a bundled product, its child products are also hidden. If you show a bundled product, its child products are shown based on their individual visibility settings.

WARNING
You can’t change a child product's quantity in the runtime cart if the Quantity Scaling Method is Constant or Default (even for legacy products where Allow Quantity Changes is selected). To enable edits, change the scaling method to None or Proportional.
When using the Proportional quantity scaling method with Allow Quantity Changes enabled, you can edit the child product's quantity only when configuring the product in the configurator. The quantity field is read-only in the sales transaction line editor because it displays the final calculated quantity stored on the quote line item, not the editable per-parent unit quantity.
