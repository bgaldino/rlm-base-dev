---
article_id: ind.pricing_create_a_proration_policy.htm
title: Create a Proration Policy for a Subscription
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_a_proration_policy.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_subscription_pricing_proration.htm
fetched_at: 2026-09-07
---

# Create a Proration Policy for a Subscription

Manage charges for partial subscription periods and choose whether remainders are applied to the first or last pricing period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To create a proration policy:	Salesforce Pricing Design Time

To create a proration policy, you must have a term-defined or evergreen product selling model and a price book entry for the product.

Create a Proration Policy
From the App Launcher, find and select Proration Policies.
Click New, and enter a descriptive name.
For Proration Policy Type, select Standard Time Periods.
For Remainder Strategy, select whether the pricing engine adds the remainder from a rounded calculation to the first or last pricing period.
The remainder strategy makes sure that the sum of the pricing-period amounts equals the original amount. For example, dividing $100 equally across three pricing periods produces the round amount of $33.33 per period. The total is $99.99, with a difference of $0.01 remaining.

If you add the remainder to the first pricing period, the pricing-period amounts are $33.34, $33.33, and $33.33. If you add the remainder to the last pricing period, the pricing-period amounts are $33.33, $33.33, and $33.34.

To prorate a subscription that includes part of a pricing period, select Allow partial proration periods.
If you don't select this option, the pricing engine charges the full pricing period.
Save your changes.
Assign a Proration Policy to a Product

Connect the product, its selling model, and the proration policy.

From the App Launcher, find and select Price Books.
Select a price book.
Under Price Book Entries, select the product.
On the Related tab, in the Product Selling Model Options related list, click New.
Select a term-defined or evergreen selling model.
You can assign a proration policy only to a term-defined or evergreen product selling model.
Confirm that the Product field shows the product that you selected from the price book entry.
Select a proration policy.
To use this product selling model option as the default for the product, select Default.
Click Save.
