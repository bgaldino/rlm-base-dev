---
article_id: ind.product_catalog_create_bundled_products.htm
title: Create Bundled Products
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_bundled_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Bundled Products

Bundled products are a group of products that are sold together as one unit. You can create static or configurable bundled products.

REQUIRED EDITIONS
View supported products and editions.
USER
PERMISSIONS NEEDED
To create products:	Manage Product Catalog
To use the Structure tab:	ARC Access permission set

For static products, you can’t add or remove child products, alter product quantities, or configure product attributes at run time. For configurable products, you can add or remove child products, alter product quantities, and configure product attributes at run time.

To create a bundled product, follow these instructions:

From the Product Catalog Management app’s home page, click Products.
From the product list view page, click New.
Select a record type. The record type options appear only if your product designer has set up product specification types and product specification record types. The specification type field in the product takes the value of the product specification type associated with the record type.
In the New Product window, specify the following values:
Enter a name and description for the product.
Select Bundle under Product Type. This is what makes the product a bundled product.
To make the product available for purchase, select Active.
To create a configurable product bundle, select Allowed under Configure During Sale.
To create a static product bundle, select Not Allowed.
To add a unit of measure, select a unit of measure.
If you can sell this product only when it's combined with other products, select Sell only with other products.
To assign product attributes, select a product classification using the Based On field.
NOTE You can select only an active product classification.
In the Display URL field, enter a URL that leads to a product image linked to an external data source. The product image appears on the product list and product details page.
Select Is Assetizable if the product instance must persist and become a customer asset after the customer purchases it. The default value is true.

The value of Is Assetizable on the root product of a product bundle applies to all child products in the bundle. For example, if Is Assetizable is selected on the root product, then every child product in the bundle is assetizable irrespective of the Is Assetizable value on the child product.

Select the date and time when the product becomes available for sale under Availability Date.
Select a date and time after which the product can’t be sold under End Of Life Date.
Select a date and time after which a product isn’t supported, ordered, or maintained under Discontinued Date.
Select a decomposition scope that determines the number of instances of fulfillment order line items to generate for the product when the order is submitted.
If you want the quantity of the fulfillment order line items to always be one, select Always One under Fulfillment Quantity Calculation Method. If you want the quantity of fulfillment order line items to be aggregated from the source line items, select Aggregate under Fulfillment Quantity Calculation Method.
If needed, select a type of usage model for a product or service. Anchor is the main subscription product or service. Pack is the add-on product or service that grants additional usage resources for consumption.
Save your changes.

After you create a product, you can assign it to catalog categories and subcategories. You can also configure product attributes. You can also add components to the bundle structure.

Create a Bundled Product Structure
After you create a bundled product (static or configurable), use the Structure tab in the bundled product to add child components such as groups, products, and product classifications.
Override Product Component Attributes in Bundles
You can override the attributes of product components in the context of the product bundle.
Include or Exclude Picklist Values in Overridden Product Attributes
Override product attributes to create the override in the context of a product bundle. To include or exclude specific picklist values for overridden product attributes of the data type picklist, use Include or Exclude Picklist Values. The included picklist values are available at run time while excluded picklist values are unavailable at run time.
Define Quantity Limits for Bundled Products
For bundled products businesses can limit, or require, the quantity of items purchased. For example, an airline that offers up to two companion fares for each frequent flyer customer. In Product Catalog Management, use local and group cardinality to create these quantity limitation rules.
Exclude Bundle Components From Product Selection at Run Time
To make certain products, groups, or classifications unavailable for selection at run time, you can exclude them from the product bundle. This exclusion doesn’t delete the product, it only hides the product from the user at run time. Exclusions are in the context of the root product bundle that you’re in.
/apex/HTViewHelpDoc?id=ind.Chunk1329962149.htm#product_catalog_bundled_product_validations

Convert Static and Configurable Product Bundles
Change a static bundled product to a configurable bundled product when you want to configure the product bundle during run time. You can also change a configurable bundled product to a static bundled product when you don’t want users to configure the product bundle during run time.
Manage and View Constraints for a Product
Maintain a unified user experience for product definitions and constraint rules. Manage, view, and activate all constraints associated with a product from a single location.
SEE ALSO
Creation Of a Bundled Product Structure
Assign Products to Catalog Categories and Subcategories
Configure Product Attributes
Preview the Product Configurator
