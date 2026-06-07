---
article_id: ind.pricing_monthly_proration_examples.htm
title: Monthly Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_monthly_proration_examples.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Monthly Proration Examples

Demonstrates how the system calculates pricing based on a monthly billing cycle.

Base Transaction Details (All Examples)
Effective From: 2025-03-28
Effective To: 2026-02-04
Total Duration: 314 Days
Start Proration Day: 5 (Used for DayOfPeriod examples)
Start Proration Month: February (Used for DayOfPeriod examples)
Proration Period: Monthly
List Price: $90.00

1. Start Proration Period: DayOfPeriod (Day 5) and Allow Partial Proration Periods: True

Calculation Logic: The billing cycles run from the 5th of one month to the 4th of the next.
Period 1 (Partial): 5-Mar-2025 to 4-Apr-2025
Total Days in Period: 31
Utilized Duration: 28-Mar-2025 to 4-Apr-2025 (8 Days)
Pricing Term Count: 8 / 31 = 0.258065
Period 2 (Full): 5-Apr-2025 to 4-May-2025
Pricing Term Count: 1.0
... (Periods 3 through 10 are full months) ...
Period 11 (Full): 5-Jan-2026 to 4-Feb-2026
Utilized Duration: 5-Jan-2026 to 4-Feb-2026 (Full Period)
Pricing Term Count: 1.0
Total Pricing Term Count:: 0.258065 (Period 1) + 10 (Periods 2-11) = 10.258065
Price: $90 x 10.258065 = $923.23

2. Start Proration Period: DayOfPeriod (Day 5) and Allow Partial Proration Periods: False

Pricing Term Count: 1.0
Calculation Logic: The term spans 10 full monthly periods (Apr–Jan) plus 1 partial period (March 28–Apr 4). The partial period is rounded up to 1 unit.
Total: 1 (Partial) + 10 (Full) = 11.0
Subscription Price: $90 x 11.0 = $990.00

3. Start Proration Period: AlignToCalendar (1st of Month) and Allow Partial Proration Periods: True

Calculation Logic: Billing cycles align with the calendar month (1st to 30th/31st).
Period 1 (partial): 1-Mar-2025 to 31-Mar-2025
Total Days in Period: 31
Utilized Duration: 28-Mar-2025 to 04-Feb-2026 (4 Days)
Pricing Term Count: 4 / 31 = 0.129032
Period 2 (Full): 1-Apr-2025 to 30-Apr-2025
Pricing Term Count: 1.0
... (Periods 3 through 11 are full months)...
Period 12 (Partial): 1-Feb-2026 to 28-Feb-2026
Total Days in Period: 28
Utilized Duration: 1-Feb-2026 to 4-Feb-2026 (4 Days)
Pricing Term Count: 4 / 28 = 0.142857
Total Pricing Term Count: 0.129032 + 10 (Full Months) + 0.142857 = 10.271889
Price: $90 x 10.271889 = $924.47

4. Start Proration Period: AlignToCalendar (1st of Month) and Allow Partial Proration Periods: False

Calculation Logic: The term touches 12 distinct calendar months (Mar 2025 through Feb 2026).
March 2025 (Touched) = 1.0
April 2025 through Jan 2026 (10 Full Months) = 10.0
February 2026 (Touched) = 1.0
Total: 12.0
Price: $90 x 12.0 = $1,080.00

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
