---
article_id: ind.pricing_monthly_proration_examples_for_leap_years.htm
title: Monthly Proration Examples for Leap Years
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_monthly_proration_examples_for_leap_years.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Monthly Proration Examples for Leap Years

Review calculations for monthly billing cycles, and learn how the total days adapt to leap years and varying month lengths. For a monthly product selling model, Salesforce Pricing anchors exactly to the numerical start date. If an anniversary subscription starts on the 29th, 30th, or 31st, and that exact date doesn't exist in the following month, Salesforce Pricing uses a design convention: it aligns the next period to the latest available day of that subsequent month. All full periods behave as "month-end to month-end minus one.

Base Transaction Details (All Examples)
Proration Period: Monthly
List Price: $150.00

1. Start Proration Period: Anniversary (Feb 28)

Effective From: 2027-02-28
Effective To: 2027-03-27
Total Duration: 28 Days
Calculation Logic: For start dates on or before the 28th, the calculation is straightforward. Salesforce Pricing anchors to the 28th. The full period is defined strictly from the 28th of the current month to the 27th of the next month.
Period 1: 28-Feb-2027 to 27-Mar-2027
Total Days in Period: 28
Utilized Duration: 28-Feb-2027 to 27-Mar-2027 (28 Days)
Pricing Term Count: (28 / 28) = 1.0
Subscription Price: $150 x 1.0 = $150.00

2. Start Proration Period: Anniversary (Jan 29)

Effective From: 2025-01-29
Effective To: 2025-02-27
Total Duration: 30 Days
Calculation Logic: Salesforce Pricing anchors to the 29th. Because February doesn't have a 29th in a standard year, the next period must start on the latest available date (February 28). This forces Period 1 to end on February 27 to maintain the full month convention.
Period 1: 29-Jan-2025 to 27-Feb-2025
Total Days in Period: 30
Utilized Duration: 29-Jan-2025 to 27-Feb-2025 (30 Days)
Pricing Term Count: (30 / 30) = 1.0
Subscription Price: $150 x 1.0 = $150.00

3. Start Proration Period: Anniversary (Jan 30)

Effective From: 2025-01-30
Effective To: 2025-03-29
Total Duration: 59 Days
Calculation Logic: Salesforce Pricing anchors to the 30th. Since February lacks a 30th, Period 1 ends on February 27 so the next period can start on the latest available date (February 28). Because March does have a 30th, Period 2 resumes starting on March 30, which forces Period 2 to end on March 29.
Period 1: 30-Jan-2025 to 27-Feb-2025
Total Days in Period: 29
Utilized Duration: 30-Jan-2025 to 27-Feb-2025 (29 Days)
Period 2: 28-Feb-2025 to 29-Mar-2025
Total Days in Period: 30
Utilized Duration: 28-Feb-2025 to 29-Mar-2025 (30 Days)
Pricing Term Count: (29 / 29) + (30 / 30) = 1.0 + 1.0 = 2.0
Subscription Price: $150 x 2.0 = $300.00

4. Start Proration Period: Anniversary (Jan 31)

Effective From: 2025-01-31
Effective To: 2025-03-30
Total Duration: 59 Days
Calculation Logic: Salesforce Pricing anchors to the 31st and adjusts for months with fewer days. Period 1 ends on February 27 so Period 2 can start on February 28. For the transition to April (which lacks a 31st), Period 2 must end on March 30 so Period 3 can start on the latest available date (April 30).
Period 1: 31-Jan-2025 to 27-Feb-2025
Total Days in Period: 28
Utilized Duration: 31-Jan-2025 to 27-Feb-2025 (28 Days)
Period 2: 28-Feb-2025 to 30-Mar-2025
Total Days in Period: 31
Utilized Duration: 28-Feb-2025 to 30-Mar-2025 (31 Days)
Pricing Term Count: (28 / 28) + (31 / 31) = 1.0 + 1.0 = 2.0
Subscription Price: $150 x 2.0 = $300.00
