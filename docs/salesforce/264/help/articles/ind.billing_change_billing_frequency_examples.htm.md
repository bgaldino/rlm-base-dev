---
article_id: ind.billing_change_billing_frequency_examples.htm
title: "Examples: Impact of Billing Frequency Change"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_change_billing_frequency_examples.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_change_billing_pricing_frequencies.htm
fetched_at: 2026-09-04
---

# Examples: Impact of Billing Frequency Change

When you change billing frequency on a transaction as different from the pricing frequency, Billing prorates the total amount from the transaction over whole and partial billing periods. For any partial periods, Billing prorates the amount based on the billing frequency. Let’s understand the calculation process with a few examples.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Mid-Year Subscription Start with Annual Billing Preference

Many enterprise customers prefer annual billing cycles for better cash flow management and reduced administrative overhead, even when product or service subscriptions start mid-month. This scenario is particularly common in businesses where the commencement of a product or service doesn’t align with calendar months, the finance teams prefer consolidated annual invoices, or when customers want predictable annual costs.

Product Configuration

Product: Analytics Platform Subscription
Unit Price: $100.00 (monthly pricing)
Quantity: 2
Pricing Term: Monthly
Billing Frequency: Annual (changed from Monthly)
Subscription Period: March 15, 2025 - March 14, 2026

Calculation Process

Step 1: Billing Period Breakdown

Monthly unit price: $100.00 (Quantity: 2 = $200.00/month)
Subscription covers: Total of 12 months

Step 2: Calculation for the first partial month in March 2025

March 15-31, 2025: 17 days out of 31 days in March
Proration multiplier: 17/31 = 0.5484
Prorated amount: $200.00 × 0.5484 = $109.68

Step 3: Calculation for Full Months

April 2025 - February 2026: 11 full months
Full month amount: $200.00 × 11 = $2,200.00

Step 4: Calculation for the last partial month in March 2026

March 1-14, 2026: 14 days out of 31 days in March
Proration multiplier: 14/31 = 0.4516
Prorated amount: $200.00 × 0.4516 = $90.32

Step 5: Generated Billing Schedule

Start Date: March 15, 2025
End Date: March 14, 2026
Billing Amount: $2,400.00 ($109.68 + $2,200.00 + $90.32)
Billing Frequency: Annual
Proration Multiplier: 1.00
Calculated Quantity: 1.00
Quarter-End Subscription with Fiscal Year Alignment

Many enterprises align their software subscriptions with fiscal quarters to streamline budget planning and financial reporting. This scenario is particularly relevant for companies with seasonal business cycles, or when finance teams manage quarterly budgets, or for other audit and compliance requirements.

In this example, a customer starts their subscription at the end of Q1 (March 25th) but wants annual billing to consolidate their software expenses into a single yearly transaction. Billing must accurately generate billing schedules for a subscription starting March 25th with only 7 days left in the quarter, spanning into the next fiscal year, while maintaining annual billing frequency with exact calendar day precision.

Product Configuration

Product: Enterprise CRM Platform
Unit Price: $180.00 (monthly pricing)
Quantity: 1
Pricing Term: Monthly
Billing Frequency: Annual (changed from Monthly)
Subscription Period: March 25, 2025 - March 24, 2026

Calculation Process

Step 1: Billing Period Breakdown

Monthly unit price: $180.00
Subscription covers: Total of 12 months

Step 2: Calculation for the first partial month in March 2025

March 25-31, 2025: 7 days out of 31 days in March
Proration multiplier: 7/31 = 0.2258
Prorated amount: $180.00 × 0.2258 = $40.64

Step 3: Calculation for Full Months

April 2025 - February 2026: 11 full months
Full month amount: $180.00 × 11 = $1,980.00

Step 4: Calculation for the last partial month in March 2026

March 1-24, 2026: 24 days out of 31 days in March
Proration multiplier: 24/31 = 0.7742
Prorated amount: $180.00 × 0.7742 = $139.36

Step 5: Generated Billing Schedule

Start Date: March 25, 2025
End Date: March 24, 2026
Billing Amount: $2,160.00 ($40.64 + $1,980.00 + $139.36)
Billing Frequency: Annual
Proration Multiplier: 1.00
Calculated Quantity: 1.00
