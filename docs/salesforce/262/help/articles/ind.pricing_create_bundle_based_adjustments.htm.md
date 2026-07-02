---
article_id: ind.pricing_create_bundle_based_adjustments.htm
title: Create Bundle Based Adjustments
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_bundle_based_adjustments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create Bundle Based Adjustments

Define bundle based adjustments to calculate discounts for products being sold as a bundle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create bundle based adjustment records:	

Salesforce Pricing Design Time

IMPORTANT Before you create bundle based adjustments, ensure that your Salesforce org is set up with these details.
A product, its root bundles, and the parent product.
All of these products must be associated with a price book.
Product selling model and a selling model for the parent product and root bundle.
To understand more about bundled products, and how to set them, see Create Bundled Products.

Salesforce Pricing provides a predefined Standard Bundle Based Adjustment that you can use, or you can create a custom one.

From the App Launcher, find and select Price Management.
From the app navigation menu, select Price Adjustment Schedules.
Change the list view to All Price Adjustment Schedules.
Click Standard Bundle Based Adjustment.
If your price adjustment schedule is active, deactivate it before adding more records.
Select Bundle Based Adjustment.
TIP For faster record creation, you don't always need to navigate through menus. You can directly select Bundle Based Adjustments from the app launcher to create a new price adjustment tier record. Then, you can follow along from step 6.
Click New.
Specify these details to create a bundle based adjustment record.
Select a root bundle.
Select the root bundle selling model.
Select the parent product.
Select the parent product selling model.
Select a product.
Select a product selling model.
Select the adjustment type.
Select Percentage if the discount on the product is applied as percentage.
Select Amount if the discount on the product is applied as a flat amount.
Select Override if the discount amount falls outside the pricing policy's rule.
Specify the adjustment value.
Enter the effective date range.
Select the price adjustment schedule.
Save your changes.
On the Price Adjustment Schedule’s page, select Active to activate your Bundle Based Adjustment.
