---
article_id: ind.product_catalog_create_simple_products.htm
title: Create Simple Products
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_simple_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Simple Products

Learn how to create simple products for your product catalog. Simple products are products that aren't bundled with other products. You can create static or configurable simple products.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To create a simple product:	Manage Product Catalog

For static products, you can’t add or remove child products, alter product quantities, or configure product attributes at run time. For configurable products, you can add or remove child products, alter product quantities, and configure product attributes at run time.

To create a simple product, follow these instructions:

From the Product Catalog Management app’s home page, click Products.
From the product list view page, click New.
Select a record type. The record type options appear only if your product designer has set up product specification types and product specification record types.
In the New Product window, specify these details:
Enter a name and description for the product.
Enter a product code.
Select None under Product Type. This makes the product a simple product.
To create a configurable simple product, select Allowed under Configure During Sale.
To create a static simple product, select Not Allowed under Configure During Sale.
If you can only sell this product when it's combined with other products, select Sell only with other products.
To make the product available for purchase, select Active.
To add a unit of measure, select a unit of measure.
To assign product attributes, select a product classification using the Based On field.
In Display URL, enter a URL that leads to a product image linked to an external data source. The product image is displayed in the runtime.
If you want the product instance to persist and become a customer asset after purchase, select Is Assetizable. This option is selected by default.
Select the date and time when the product becomes available for sale under Availability Date.
Select a date and time after which the product can’t be sold under Discontinued Date.
Select a date and time after which a product isn’t supported, ordered, or maintained under End Of Life Date.
Select a decomposition scope that determines the number of instances of fulfillment order line items to generate for the product when the order is submitted.
If you want the quantity of the fulfillment order line items to always be one, select Always One under Fulfillment Quantity Calculation Method. If you want the quantity of fulfillment order line items to be aggregated from the source line items, select Aggregate under Fulfillment Quantity Calculation Method.
If needed, select a type of usage model for a product or service. Anchor is the main subscription product or service. Pack is the add-on product or service that grants additional usage resources for consumption. Commit is an agreement by a customer to use a minimum quantity of a product or service in a defined period.
Save your changes.

After you create a product, you can choose to assign it to catalog categories and subcategories. You can also configure product attributes if the product is based on a product classification.

SEE ALSO
Assign Products to Catalog Categories and Subcategories
Configure Product Attributes
Preview the Product Configurator
