---
article_id: ind.pricing_create_price_adjustment_tiers_volume_discounts.htm
title: Create Price Adjustment Tiers for Volume Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_price_adjustment_tiers_volume_discounts.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create Price Adjustment Tiers for Volume Discounts

Set up pricing rules that automatically adjust prices and offer discounts based on the quantities purchased by creating price adjustment tier records. You can use them to implement various strategies, including both volume or tiered discounts. This adjustment type enables you to define a product's price based on the number of items being sold.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create price adjustment tiers:	

Salesforce Pricing Design Time

IMPORTANT Before you create a price adjustment tier record, ensure that your Salesforce org has a product selling model and has products added to a price book.

Salesforce Pricing provides a predefined Standard Price Adjustment Tier that you can use, or you can create a custom one.

From the App Launcher, find and select Price Management.
From the app navigation menu, select Price Adjustment Schedules.
Change the list view to All Price Adjustment Schedules.
Click Standard Price Adjustment Tier.
If your price adjustment schedule is active, deactivate it before adding more records.
Select Standard Price Adjustment Tier.
TIP For faster record creation, you don't always need to navigate through menus. You can directly select Price Adjustment Tiers from the app launcher to create a new price adjustment tier record. Then, you can follow along from step 6.
Click New.
Specify these details to create a price adjustment tier record.
Select a product.
Select a product selling model.
Select the price adjustment schedule that must be associated with this price adjustment tier record.
Select the tier type.
Select Percentage if the discount on the product is applied as percentage.
Select Amount if the discount on the product is applied as a flat amount.
Select Override if the discount amount falls outside the pricing policy's rule.
Specify the tier value.
If the tier type is Percentage, the tier value is the percentage value of the discount, for example, 10%. If the tier type is Amount, the tier value is the flat amount of the discount, for example, US$100.
Enter the Lower Bound and Upper Bound values.
These values represent the minimum and maximum quantity of discount that can be applied to the product.
IMPORTANT Values are inclusive and the tiers can’t overlap.
Enter the effective date range.
IMPORTANT
Price adjustment tiers with the same effective date must have consecutive lower and upper bound values, with no gaps.
To prevent calculation errors, especially when multi-currency is disabled, don't create duplicate Price Adjustment Tier records. For a unique combination of Product, Product Selling Model, Price Adjustment Schedule, Currency, and Effective Dates, make sure that the quantity ranges (Lower and Upper Bounds) don't overlap.
Save your changes.
On the Price Adjustment Schedule’s page, select Active to activate your Price Adjustment Tier adjustment schedule.
SEE ALSO
Create Price Adjustment Schedules
