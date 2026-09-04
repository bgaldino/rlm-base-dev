---
article_id: ind.product_configurator_bundled_products_instance_quantity.htm
title: Calculate End Quantity and Instance Quantity in Bundled Products
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_bundled_products_instance_quantity.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_configure_bundled_products.htm
fetched_at: 2026-09-04
---

# Calculate End Quantity and Instance Quantity in Bundled Products

By default, when you calculate the quantity of a child product in a bundle, the constraint engine returns the end quantity, which is the total quantity of the child product across all parent instances. You can also calculate instance quantity, the quantity of the child product per instance of the parent product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To configure a product:	Product Configurator

When you turn on the Constraint Instance Quantity setting in Revenue Settings, the constraint engine returns the instance quantity of the child product. For example, if a customer orders 3 generator sets and each set requires 2 alternators, the instance quantity is 2, the quantity per bundle. The end quantity of alternators is 6.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on Constraint Instance Quantity.
