---
article_id: ind.pricing_quarterly_proration_examples.htm
title: Quarterly Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_quarterly_proration_examples.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Quarterly Proration Examples

Demonstrates how the system calculates pricing based on 3-month billing intervals.

Base Transaction Details (All Examples)
Effective From: 2025-03-28
Effective To: 2026-02-04
Total Duration: 314 Days
Start Proration Day: 5 (Used for DayOfPeriod examples)
Start Proration Month: February (Used for DayOfPeriod examples)
Proration Period: Quarterly
List Price: $200.00

1. Start Proration Period: AlignToCalendar (1st of Month) and Allow Partial Proration Periods: True

Calculation Logic: Periods align with calendar quarters (Jan-Mar, Apr-Jun, etc.). Average days in a quarter = 91.25.
Period 1 (Partial - Q1): 1-Jan-2025 to 31-Mar-2025
Utilized Duration: 28-Mar-2025 to 31-Mar-2025 (4 Days)
Pricing Term Count: 4 / 91.25 (Avg) = 0.043836
Period 2 (Full - Q2): 1-Apr-2025 to 30-Jun-2025
Pricing Term Count: 1.0
Period 3 (Full - Q3): 1-Jul-2025 to 30-Sep-2025
Pricing Term Count: 1.0
Period 4 (Full - Q4): 1-Oct-2025 to 31-Dec-2025
Pricing Term Count: 1.0
Period 5 (Partial - Q1): 1-Jan-2026 to 31-Mar-2026
Utilized Duration: 1-Jan-2026 to 4-Feb-2026 (35 Days)
Pricing Term Count: 35 / 91.25 (Avg) = 0.383562
Total Pricing Term Count:: 0.043836 + 3.0 + 0.383562 = 3.427 (approx 3.436464 using exact day counts per specific quarter logic).
Price: $200 x 3.436464 = $687.29

2. Start Proration Period: AlignToCalendar (1st of Month) and Allow Partial Proration Periods: False

Calculation Logic: The term touches 5 distinct calendar quarters. Each touched quarter counts as 1.0 unit.
Period 1: Q1 2025 (Touched)
Period 2: Q2 2025 (Full)
Period 3: Q3 2025 (Full)
Period 4: Q4 2025 (Full)
Period 5: Q1 2026 (Touched)
Price: $200 x 5.0 = $1,000.00
