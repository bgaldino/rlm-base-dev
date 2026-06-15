---
article_id: ind.pricing_annual_proration_examples.htm
title: Annual Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_annual_proration_examples.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Annual Proration Examples

Demonstrates how the system calculates pricing based on a yearly billing cycle.

Base Transaction Details (All Examples)
Effective From: 2025-03-28
Effective To: 2026-02-04
Total Duration: 314 Days
Start Proration Day: 5 (Used for DayOfPeriod examples)
Start Proration Month: February (Used for DayOfPeriod examples)
Proration Period: Annual
List Price: $800.00

1. Start Proration Period: DayOfPeriod (Feb 5) and Allow Partial Proration Periods: True

Calculation Logic: The system creates billing periods anchored to February 5th.
Period 1: 5-Feb-2025 to 4-Feb-2026
Total Days in Period: 365
Utilized Duration: 28-Mar-2025 to 4-Feb-2026 (314 Days)
Pricing Term Count: 314 / 365 = 0.860274
Subscription Price: $800 x 0.860274 = $688.22

2. Start Proration Period: DayOfPeriod (Feb 5) and Allow Partial Proration Periods: False

Pricing Term Count: 1.0
Calculation Logic: The term utilizes a single billing period (Feb 5 to Feb 4). Since the subscription falls within this specific annual cycle, the system rounds the partial usage up to 1 full unit.
Subscription Price: $800 x 1.0 = $800.00

3. Start Proration Period: Anniversary (Mar 28) and Allow Partial Proration Periods: True

Calculation Logic: The system creates periods anchored to the start date (Mar 28).
Period 1: 28-Mar-2025 to 27-Mar-2026
Total Days in Period: 365
Utilized Duration: 28-Mar-2025 to 04-Feb-2026 (314 Days)
Pricing Term Count: 314 / 365 = 0.860274
Subscription Price: $800 x 0.860274 = $688.22

4. Start Proration Period: Anniversary (Mar 28) and Allow Partial Proration Periods: False

Calculation Logic: The subscription duration sits entirely within a single anniversary year (Period 1 above); this is counted as 1 full unit.
Pricing Term Count: 1.0
Subscription Price: $800 x 1.0 = $800.00

5. Start Proration Period: AlignToCalendar (Jan 1) and Allow Partial Proration Periods: True

Calculation Logic: The system calculates the total days utilized divided by the days in the year.
Period 1: 1-Jan-2025 to 31-Dec-2025
Utilized Duration: 28-Mar-2025 to 31-Dec-2025 (279 /365)
Period 2: 1-Jan-2026 to 31-Dec-2026
Utilized Duration: 1-Jan-2026 to 04-Feb-2026 (35/365)
Total: (279/365 + 35/365) = 0.860274
Subscription Price: $800 x 0.860274 = $688.22

6. Start Proration Period: AlignToCalendar (Jan 1) and Allow Partial Proration Periods: False

Calculation Logic: The term crosses the Jan 1 boundary, touching two distinct calendar years (2025 and 2026). Each "touched" calendar year counts as 1.0.
Period 1: 2025 (Touched) = 1.0
Period 2: 2026 (Touched) = 1.0
Subscription Price: $800 x 2.0 = $1,600.00
