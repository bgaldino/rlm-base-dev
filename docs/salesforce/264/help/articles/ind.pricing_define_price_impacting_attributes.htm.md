---
article_id: ind.pricing_define_price_impacting_attributes.htm
title: Set Price Impacting Attributes for Products
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_define_price_impacting_attributes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_add_attribute_based_price_element.htm
fetched_at: 2026-11-23
---

# Set Price Impacting Attributes for Products

Simplify the selling experience for your sales reps using price-impacting attributes when selling your product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To create price impacting attributes:	

Salesforce Pricing Design Time

OR

Salesforce Pricing Run Time

Instead of manually calculating discounts or navigating complex product catalogs, sales reps can simply select desired product characteristics like color, size, or material. The price automatically updates in real-time, even applying specific discounts—for example, a 10% markdown for a red mobile phone.

This dynamic pricing capability significantly reduces quoting errors because sales reps can quickly configure precise product pricing and instantly determine the final price.

Before implementing attribute-based pricing, you must define attributes for your products and designate at least one product attribute as price-impacting.

IMPORTANT To create a valid attribute-based pricing rule, verify that the attribute is active and has Is Price Impacting selected.

To learn how to set attributes for products, see Create Product Attributes in Revenue Cloud.

From App Launcher, find and select Price Management.
From the app navigation menu, select Products.
Select a product from the list. If you don’t see products on this page, change the list view to show All Products.
On the Related tab, under Overridden Inherited Attributes, select an attribute.
If the desired attribute isn't available under Overridden Inherited Attributes, from the dropdown menu on the right of the Inherited Attributes section next to the desired attribute, select Configure.
The attribute moves to the Overridden Inherited Attributes list.
On the Product Attribute Definition page, edit and select the Is Price Impacting option.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_define_price_impacting_attributes.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
