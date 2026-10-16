---
article_id: ind.product_catalog_product_ramp_segments.htm
title: Create a Product Ramp Segment
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_ramp_segments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.qocal_configure_ramp_segments.htm
fetched_at: 2026-09-04
---

# Create a Product Ramp Segment

A ramp deal is a type of sales agreement where price and volume vary across time periods. A ramp segment is a specific period within a ramp deal during which certain prices and volume are in effect.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To create a ramp segment:	Manage Product Catalog

Considerations for product ramp segments.

You can associate only static simple and configurable simple products with ramp segments.
You must assign a term-defined product selling model to a product and then use the combination of the term-defined product selling model and the product to create a ramp segment.
A product can have only one ramp segment of the same segment type — for example, a product can have only one yearly product ramp segment.
Before you create a product ramp segment, turn on Ramp Deals for Lines in Quotes and Orders.
From Setup, in the Quick Find box, find, and select Revenue Settings.
Turn on Ramp Deals for Lines in Quotes and Orders.
From the App Launcher, find and select Product Catalog Management.
From the product list, click the simple product for which you want to create ramp segments.
Go to the Related tab for the product.
From the Product Ramp Segments related list, click New.
In the New Product Ramp Segment window, specify the following:
Select a term-defined product selling model.
To try the product at no additional cost for a specified duration, under Segment Type select Free Trial, enter a trial duration, and select the duration type. For example, to offer a 1-month trial at no additional cost, enter 1 in the Trial Duration field and select Month under Duration Type. To associate a trial segment at no additional cost with a product, first associate a yearly or custom segment with that product.
To create a segment for a specific number of years, select Yearly under Segment Type. Leave the Trial Duration and Duration Type fields blank.
To create a segment for a custom duration, select Custom under Segment Type. Leave the Trial Duration and Duration Type fields blank.
Save your changes.
