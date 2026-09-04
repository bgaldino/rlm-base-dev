---
article_id: ind.qocal_renewal_price_uplifts.htm
title: Negotiate Price Uplifts for Subscription Renewals
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renewal_price_uplifts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_quotes_and_orders_in_the_revenue_cloud.htm
fetched_at: 2026-09-04
---

# Negotiate Price Uplifts for Subscription Renewals

Apply renewal price uplifts to subscriptions, including adjustments based on the Consumer Price Index (CPI). Sales reps negotiate renewal price uplifts during the initial sale and modify uplift percentages on assets and line items during renewals to ensure accurate pricing and maintain data integrity.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create price uplifts:	

Manage Revenue Management

AND

Create Orders from Quotes

AND

Renew Assets

AND

Sales Rep permission group

IMPORTANT Review these requirements before applying uplifts to your records.
Renewal price uplifts apply only to products with a term-defined product selling model.
The pricing procedure includes the uplift as a calculation by using the Formula-Based Pricing element.
Ensure accurate pricing by applying uplifts after discounts when you use Last Transaction Pricing.
Set the asset's Pricing Source to Last Transaction Pricing before adding the asset to a new quote or order and selecting an uplift percentage.

Modify uplift percentages on items and verify the results on the generated renewal record.

Specify the uplift percentage for the unit price in a quote line item or an order item.
Save your changes.
Select Create Order and activate the order to assetize it.
Review the asset to verify the applied unit price uplift.
Generating a renewal quote applies the negotiated price uplift.
Create and activate a new order from the renewal quote that includes the unit price uplift.
View unit price uplift details in the waterfall by hovering over the Net Unit Price field.
CPI and Renewal Price Uplift Considerations
Familiarize yourself with the supported product types, field behaviors, and system logic for applying Consumer Price Index (CPI) and renewal price uplifts. Understanding these constraints ensures accurate pricing calculations during asset renewal and helps you determine where uplift data appears in the price waterfall.
