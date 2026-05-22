---
article_id: ind.pricing_create_attribute_based_adjustments.htm
title: Create Attribute Based Adjustments
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_attribute_based_adjustments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create Attribute Based Adjustments

Set up pricing rules that automatically adjust prices and offer discounts based on a product's price-impacting attributes by creating attribute-based adjustment records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create attribute based adjustment records:	

Salesforce Pricing Design Time


To access the Attribute Adjustment Condition object:	Salesforce Pricing Manager
IMPORTANT Before you create an attribute based adjustment record, ensure that your Salesforce org has a product selling model and has products added to a price book. Define attributes to your products and ensure that at least one is price-impacting.

Salesforce Pricing provides a predefined Standard Attribute Based Adjustment that you can use, or you can create a custom one.

From the App Launcher, find and select Price Management.
From the app navigation menu, select Price Adjustment Schedules.
Change the list view to All Price Adjustment Schedules.
Click Standard Attribute Based Adjustment.
If your price adjustment schedule is active, deactivate it before adding more records.
Select Attribute Based Adjustment.
TIP For faster record creation, you don't always need to navigate through menus. You can directly select Attribute Based Adjustments from the app launcher to create a new price adjustment tier record. Then, you can follow along from step 6.
Click New.
Specify these details to create a price adjustment tier record.
Select a product.
Select a product selling model.
Select the adjustment type.
Select Percentage if the discount on the product is applied as percentage.
Select Amount if the discount on the product is applied as a flat amount.
Select Override if the discount amount falls outside the pricing policy's rule.
Specify the adjustment value.
Enter the effective date range.
Click Next.
Set the condition for when the attribute based adjustment is applied.
Save your changes.
On the Price Adjustment Schedule’s page, select Active to activate your Attribute Based Adjustment.
SEE ALSO
Create Price Adjustment Schedules
