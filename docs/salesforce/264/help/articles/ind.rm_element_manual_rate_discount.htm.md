---
article_id: ind.rm_element_manual_rate_discount.htm
title: Manual Rate Discount
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_manual_rate_discount.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Manual Rate Discount

The Manual Rate Discount element calculates the final price of a product after you manually enter the external discounts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Manual discounts support adjustment types such as number, percentage, and currency. The adjustment type determines the type of calculation performed. For example, if you select the Amount adjustment type and the adjustment value is 10, a discount of US$10 is applied to the usage resource. Similarly, a 10% discount is applied to the usage resource's value if you select the Percentage adjustment type.

For example, create rating rules for users with a voucher that makes them eligible to receive an additional discount of 10% on all their consumption.

Manual Rate Discount Variables
To calculate discounts, use the RateManagementContext context definition and map the variables to the relevant context tags.
Add the Manual Rate Discount Element
Here’s how you can add the Manual Rate Discount element to your rating procedure.
