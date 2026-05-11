---
article_id: ind.billing_field_combination_requirements.htm
title: Field Combination Requirements
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_field_combination_requirements.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Field Combination Requirements

The combination of billing frequency, period boundary, period boundary day, and period boundary start month determines billing behavior.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Identify which period boundary values are supported for each billing frequency.

BILLING FREQUENCY	SUPPORTED PERIOD BOUNDARY	SUPPORTED PERIOD BOUNDARY DAY AND PERIOD BOUNDARY START MONTH
Monthly, annual	Align to calendar, anniversary, day of period, last day of period	You can only specify period boundary start month when period boundary is day of period. You can't specify period boundary start month for monthly billing frequency.
Quarterly, semiannual	Anniversary, day of period	You can only specify period boundary day and period boundary start month for day of period.

Here are some examples that illustrate how different configurations of billing frequency and period boundaries work.

QUARTERLY BILLING WITH A TRANSITION MONTH BEFORE THE CYCLE BEGINS

Businesses often need flexibility when a customer’s order begins before the regular billing cycle is scheduled to start. In such cases, you can configure billing to handle a short initial billing period that covers the gap between the order start date and the beginning of the defined cycle. Let's say an order product has the following configuration:

Billing frequency: Quarterly
Period boundary: Day of period
Period boundary day: 1
Period boundary start month: July
Order start date: June 1, 2025

When invoicing runs with a target date of June 1, 2025, billing generates a monthly invoice for the period from June 1 to June 30, covering the period before the quarterly cycle begins.

When invoicing runs again after July 1, billing generates the first full quarterly invoice for the period from July 1 to September 30.

This configuration supports an initial one-month billing period before transitioning to a recurring quarterly schedule.

ALIGN ANNUAL BILLING TO A CUSTOM START MONTH

Some businesses align annual billing to a fixed month, such as the start of a fiscal year, regardless of when a customer places an order. This setup ensures coverage from the order date while anchoring all future invoices to the chosen billing cycle start. For example, an order is placed on August 1, 2025 and has the following configuration:

Billing frequency: Annual
Period boundary: Day of period
Period boundary day: 1
Period boundary start month: April

When invoicing runs on August 1, billing generates an invoice for the period from August 1, 2025 to March 31, 2026.

When invoicing runs again on April 1, 2026, billing generates the next annual invoice covering the period from April 1, 2026 to March 31, 2027.

This configuration aligns all future billing to start on April 1, even though the order was placed in August.

TERM-BASED PRODUCT WITH SEMI-ANNUAL BILLING

Some subscriptions follow the customer’s start date instead of aligning to a fixed calendar boundary. With an anniversary-based setup, each billing period is calculated from the original subscription start, creating consistent intervals, such as semiannual or annual. This ensures the customer is always billed for a full term tied to when their service began. A term-based subscription begins on January 15, 2025. The configuration includes:

Billing frequency: Semiannual
Period boundary: Anniversary

When invoicing runs on January 15, an invoice is generated for the period from January 15 to July 14.

Subsequent invoices are generated every 6 months, starting July 15, January 15 (next year), and so on.

This setup ties each billing period directly to the original subscription start date, maintaining consistent semiannual billing.

TERM-DEFINED PRODUCT WITH QUARTERLY BILLING AND A MID-TERM AMENDMENT

In some cases, a subscription may need to handle changes within an active billing term, such as an update to quantity or product configuration. With quarterly billing tied to a fixed day, the system generates standard invoices while also applying prorated adjustments for mid-term amendments, maintaining accurate charges within the affected billing period. For example, a term product starts on January 15, 2025 with the following configuration:

Billing frequency: Quarterly
Period boundary: Day of period
Period boundary start month: January
Period boundary start date: 15

The billing frequency is quarterly, and the period boundary is set to day of period with a start date of January 15. Each billing period starts from the 15th of one month to the 14th of the month 3 months later. The first invoice, generated in advance on January 15, covers the period from January 15 to April 14. On February 15, a mid-term amendment, such as a quantity change, occurs. At the next invoicing run, Billing calculates a prorated charge for the updated quantity, effective from February 15 to April 14. On April 15, Billing generates the next quarterly invoice, covering the period from April 15 to July 14 and reflecting the amended configuration.
