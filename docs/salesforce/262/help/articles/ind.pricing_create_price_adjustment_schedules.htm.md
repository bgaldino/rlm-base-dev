---
article_id: ind.pricing_create_price_adjustment_schedules.htm
title: Create and Manage Price Adjustment Schedules
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_price_adjustment_schedules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create and Manage Price Adjustment Schedules

Define price adjustment schedules and set volume, attribute, or bundle-based discounts for your products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create price adjustment schedules:	

Salesforce Pricing Design Time

Salesforce Pricing comes with several predefined price adjustment schedules that you can use right out of the box, including:

Standard Attribute Based Adjustment
Standard Bundle Based Adjustment
Standard Price Adjustment Tier

You can use these, or create custom price adjustment schedules tailored to your business rules. Any existing price adjustment schedule can also be easily cloned, saving you time.

To create a price adjustment schedule record, follow these steps:

From App Launcher, find and select Price Adjustment Schedules.
Click New.
Give your price adjustment schedule a name.
Select the Adjustment Method.
Range	Select this option if you want to give all your products the same discount options. For example, you can give a flat discount of 10% when a customer purchases 10 items or more.
Slab	Select this option if you want to give different discounts based on the conditions set. For example, you can give the customer a discount of 10% for the first 10 items and 15% when they purchase 11–20 items.
Select the Schedule Type.
Volume	Select this option if you want to give a discount based on the quantity. For example, a flat discount of 10% on purchase of 50 items or more.
Attribute	Select this option if you want to give discounts based on the attributes associated with the product. For example, a discount of $50 on all red mobile phones.
Bundle	Select this option if you want to give a discount on different items sold together as a single product. For example, a discount of 10% if your customer purchases a television with a warranty.
Provide an effective date range.
The Effective From date specifies the date and time from when the discount is applied to the product. If you don’t choose an Effective To date, the discount applies indefinitely.
Save your changes.

You can modify price adjustment schedule records in two ways: by updating the fields that have the icon. If you update the price details, another record is created.
