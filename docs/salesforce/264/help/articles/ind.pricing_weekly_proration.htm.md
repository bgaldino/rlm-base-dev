---
article_id: ind.pricing_weekly_proration.htm
title: Weekly Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_weekly_proration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_subscription_variables.htm
fetched_at: 2026-09-07
---

# Weekly Proration Examples

Demonstrates how the system calculates pricing based on a 7-day billing cycle, for subscription and consumption products.

NOTE For the DayOfPeriod boundary field, 1 represents Monday, 2 represents Tuesday, and 7 represents Sunday. The system calculates weekly prices based on this boundary, starting each week on the selected day.
Base Transaction Details (All Examples)
Effective From: 2025-01-01
Effective To: 2025-03-17
Total Duration: 75 Days
Proration Period: Weekly
List Price: $12.01
Quantity: 12

Calculation Logic: The system divides the total duration by 7 to get the number of weeks in the term, including any partial week, then multiplies the unit price by the quantity and by that number of weeks.

Pricing Term Count: 75 / 7 = 10.71
Subscription Price: $12.01 x 12 x 10.71 = $1,543.36
