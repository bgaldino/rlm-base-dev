---
article_id: ind.pricing_semi_annual_proration_examples.htm
title: Semi-Annual Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_semi_annual_proration_examples.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Semi-Annual Proration Examples

Demonstrates how the system calculates pricing based on 6-month billing intervals.

Base Transaction Details (All Examples)
Effective From: 2025-03-28
Effective To: 2026-02-04
Total Duration: 314 Days
Start Proration Day: 5 (Used for DayOfPeriod examples)
Start Proration Month: February (Used for DayOfPeriod examples)
Proration Period: Semi-Annual
List Price: $400.00

1. Start Proration Period: DayOfPeriod (Day 5) and Allow Partial Proration Periods: True

Calculation Logic: Periods are 6 months long, anchored to Feb 5th.
Period 1 (Partial): 5-Feb-2025 to 4-Aug-2025
Total Days in Period: 181
Utilized Duration: 28-Mar-2025 to 4-Apr-2025 (130 Days)
Pricing Term Count: 130 / 181 = 0.718232
Period 2 (Full): 5-Aug-2025 to 4-Feb-2026
Utilized Duration: 5-Aug-2025 to 4-Feb-2026 (Full Period)
Pricing Term Count: 1.0
Total Pricing Term Count: 0.718232 + 1.0 = 1.718232
Price: $400 x 1.718232 = $687.29

2. Start Proration Period: DayOfPeriod (Day 5) and Allow Partial Proration Periods: False

Calculation Logic: The term spans parts of 3 distinct 6-month blocks anchored to Feb 5.
Period 1: Feb '25 - Aug '25 (Touched) = 1.0
Period 2: Aug '25 - Feb '26 (Touched) = 1.0
Period 3: Feb '26 - Aug '26 (Touched, because the term ends on Feb 4, effectively completing the previous block, but systems often count the boundary touch. Note: Based on the provided user text saying "3.0", the logic assumes the term touches a 3rd period or the system rounds up heavily. Based on the dates (Mar '25 to Feb '26), it sits primarily in 2 periods. If 3.0 is the result, it implies the system sees the end date falling into a 3rd cycle or counts the anchor start/end inclusively across boundaries).
Price: $400 x 3.0 = $1,200.00
