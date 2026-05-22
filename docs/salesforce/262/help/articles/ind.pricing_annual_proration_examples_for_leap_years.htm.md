---
article_id: ind.pricing_annual_proration_examples_for_leap_years.htm
title: Annual Proration Examples for Leap Years
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_annual_proration_examples_for_leap_years.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Annual Proration Examples for Leap Years

Review calculations for annual billing cycles, and learn how the total days adapt to leap years. Salesforce Pricing uses a specific design convention to handle end-of-month anniversary dates. Rather than relying on simple date increments, Salesforce Pricing adjusts period end dates to accommodate the presence or absence of February 29 so that it calculates full periods logically based on date availability.

Base Transaction Details (All Examples)
Proration Period: Annual
List Price: $1,000.00

1. Start Proration Period: Anniversary (Feb 29)

Effective From: 2024-02-29
Effective To: 2025-02-27
Total Duration: 365 Days
Calculation Logic: Salesforce Pricing uses a design convention to manage leap year boundaries. Because the subscription starts on Leap Day, but the following year (2025) lacks a February 29, the next period must start on the latest available date (February 28). This forces the current full annual period to end on February 27.
Period 1: 29-Feb-2024 to 27-Feb-2025
Total Days in Period: 365
Utilized Duration: 29-Feb-2024 to 27-Feb-2025 (365 Days)
Pricing Term Count: 365 / 365 = 1.0
Subscription Price: $1,000 x 1.0 = $1,000.00

2. Start Proration Period: Anniversary (Feb 28 - Partial Period Before Leap Year)

Effective From: 2027-02-28
Effective To: 2028-02-27
Total Duration: 365 Days
Calculation Logic: This example highlights a critical distinction. Because the start date (Feb 28) is a month-end date preceding a leap year, Salesforce Pricing expects the full annual period to end on February 28, 2028 (a 366-day period). Because the subscription ends one day early on February 27, it doesn't complete the full term. Therefore, Salesforce Pricing calculates it as a partial period, resulting in a prorated charge.
Period 1: 28-Feb-2027 to 27-Feb-2028
Total Days in Period: 366 (The denominator is based on the full expected period ending 28-Feb-2028)
Utilized Duration: 28-Feb-2027 to 27-Feb-2028 (365 Days)
Pricing Term Count: 365 / 366 = 0.99726
Subscription Price: $1,000 x (365 / 366) = $997.27

3. Start Proration Period: Anniversary (Feb 28 - Preceding a Leap Year)

Effective From: 2027-02-28
Effective To: 2028-02-28
Total Duration: 366 Days
Calculation Logic: Salesforce Pricing identifies February 28 in a non-leap year as a month-end date. For annual proration, a full period ends one day before the next month-end. In 2028 (a leap year), the month-end is February 29, making the period end date February 28. By convention, the leap day (February 29) is included in the billing period when the leap year falls within the period’s end date.
Period 1: 28-Feb-2027 to 28-Feb-2028
Total Days in Period: 366
Utilized Duration: 28-Feb-2027 to 28-Feb-2028 (366 Days)
Pricing Term Count: 366 / 366 = 1.0
Subscription Price: $1,000 x 1.0 = $1,000.00
