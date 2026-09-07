---
article_id: ind.pricing_update_your_product_price_range_entries_decision_table.htm
title: Update Your Product Price Range Entries Decision Table
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_update_your_product_price_range_entries_decision_table.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_price_tracking.htm
fetched_at: 2026-09-07
---

# Update Your Product Price Range Entries Decision Table

For users who previously enabled minimum price tracking, update your decision table to include the newly introduced option for tracking maximum prices. If you enable maximum price in Price Tracking History settings without this update, your pricing procedure will fail during execution.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To edit decision tables:	Salesforce Pricing Design Time User

If you're using the Price Tracking feature for the first time and have enabled both maximum and minimum price settings, you can use the predefined Product Price Range Entries V2. This will automatically map to record both the minimum and maximum price of a product.

From App Launcher, search for and select Lookup Tables.
Select the Product Price Range Entries decision table.
Deactivate the decision table.
Click Edit.
Click Save & Next.
To record the maximum price of a product, under Results, click +Add Results.
In the Source Object Field, enter and select MaxRecordedPrice.
Click Save & Next.
Click Save & Next again.
Click Finish.
Activate your decision table.
