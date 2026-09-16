---
article_id: ind.product_catalog_create_a_product_selling_model.htm
title: Create a Product Selling Model
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_a_product_selling_model.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_product_selling_model.htm
fetched_at: 2026-09-04
---

# Create a Product Selling Model

Create product selling models for your products from the Product Catalog Management home page.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To create product selling models:	Manage Product Catalog
From the Product Catalog Management app’s home page, click Product Selling Models.
On the Product Selling Model list view page, click New.
In the New Product Selling Model window, specify these details:
The product selling model name.
The selling model type.
If you selected Term-Defined or Evergreen selling model type, enter the length of the term and the unit of time.
To define a one year term-defined product selling model:
Selling Model Type: Term-Defined
Pricing Term: 1
Pricing Term Unit: Year
To define a monthly recurring evergreen product selling model:
Selling Model Type: Evergreen
Pricing Term: 1
Pricing Term Unit: Month
If you selected the Term-Defined selling model type and want the product to be renewed automatically, select Automatically Renew Asset by Default.

When sales reps or customers add a product to a quote or an order, this auto-renewal status is stored in the line item created for the product.

Sales reps and customers can edit the line item to adjust the auto-renewal status.

Transaction Management passes the status to subsequent stages. For example, when sales reps create an order from a quote, the auto-renewal status of quote line items is passed to the corresponding order line items.

Select a status for the selling model.
You can’t change the status of a product selling model back to draft after you’ve set the status to active or inactive.
Save your changes.
