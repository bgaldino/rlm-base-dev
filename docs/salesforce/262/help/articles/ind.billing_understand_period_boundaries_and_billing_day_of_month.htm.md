---
article_id: ind.billing_understand_period_boundaries_and_billing_day_of_month.htm
title: Period Boundaries and Billing Day of Month
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_understand_period_boundaries_and_billing_day_of_month.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Period Boundaries and Billing Day of Month

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Period Boundaries and Billing Day of Month

You can use the Period Boundary, Period Boundary Day, and Period Boundary Start Month fields on transactions, such as order product, to define when billing begins, how billing periods are segmented, and how proration is applied. The period boundary on the order product ‌defines how the billing period is calculated. The Billing Day of the Month field on the Billing Schedule record specifies the day you expect to bill the customer. Together, these fields define how billing periods align with the transaction timeline and how Billing in Agentforce Revenue Management calculates and groups charges on invoice lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Period Boundaries and Their Impact on Billing Cycles

Consider monthly advance billing of an order product that starts on August 5 with period boundary set to anniversary. When the billing schedule is created, the next billing date is set to August 5.

Billing periods follow the order start date and run from August 5 to September 4, September 5 to October 4, and so on.

If the period boundary is set to align to calendar, the first billing period covers August 5 to August 31. After the first billing cycle, the next billing date is updated to September 1. Then, billing follows calendar months from that point onward, such as September 1 to September 30, October 1 to October 31, and so on.

If the period boundary is set to the last day of the period, the first billing period spans August 5 to August 30. The next billing date is then updated to August 31. Each new billing period starts the day after the previous one ends. It continues through the day before the next period begins.

If the period boundary is set to day of period, and the period boundary day is 8 with period boundary start month as August, then the first billing period spans from August 5 to August 7. The day of month offers greater flexibility because it allows you to define the exact day for the billing period to begin. For example, if you specify the day as 8, the first billing cycle covers August 5 to August 7. After that, the next billing date is set to August 8 and billing continues from the 8th day of each period based on the configured billing frequency.

For quarterly, semi-annual, or annual billing frequencies, the period boundary, period boundary day, and period boundary start month fields work together to determine when billing cycles begin.

For example, take the same order starting on August 5 with billing frequency set to quarterly and period boundary set to anniversary. In this setup, the initial next billing date is August 5, and the first billing period runs from August 5 to November 4. Once this period ends, the next billing date shifts to November 5 and billing recurs every three months, such as from November 5 to February 4, February 5 to May 4, and so on.

Choose the Right Period Boundary for Your Billing Needs
PERIOD BOUNDARY	DESCRIPTION	BILLING SCENARIOS	USE CASE
Align to Calendar	Billing periods follow the calendar month or year.	

Useful when billing needs to align to standard calendar-based cycles, such as monthly or yearly.

	

Acme Company sells B2B cloud licenses and recognizes revenue annually. They configure the Period Boundary to Align to Calendar, with October as the Period Boundary Start Month. An order starts on August 1. The first billing period spans from August 1 to December 31. If the subscription ends early, say on November 2, the billing schedule adjusts to cover August 1 through November 2. Otherwise, starting January 1, billing continues in full annual periods. This setup ensures invoices and revenue schedules stay aligned with calendar-based business processes.


Anniversary	Billing periods align with the order start day.	

Ideal if customers expect billing to occur on the day the subscription began.

	

Acme Fitness supports multiple billing models to suit different customer needs. One of their clients uses anniversary-based billing period with a monthly billing frequency. When a customer signs up on August 10, their billing periods run from August 10 to September 9, September 10 to October 9, and so on. Each invoice covers one full month starting from the customer’s sign-up date, ensuring consistent and personalized billing throughout the subscription.


Day of Period	Billing begins on a specific day of the billing period. The billing period can be a month, quarter, semiannual, or annual.	

Recommended for use cases where customers want to be billed on a specific day in the billing period.

	

Acme Telecom sells termed products and prefers billing periods that align with standard quarterly cycles. For one such product, the billing period begins on August 1, 2025. It’s configured with Billing Frequency set to Quarterly, Period Boundary as Day of Period, Period Boundary Day as 1, and Period Boundary Start Month as March.

With this setup, quarterly billing periods are aligned to start in March, June, September, and December. The first billing period item covers the partial period from August 1 to August 31, before the regular quarterly cycle begins in September.


Last Day of Period	Billing periods follow the calendar month or year.	

Useful for companies that consolidate all charges and usage data before issuing a final invoice, especially when dealing with variable consumption or compliance rules.

	

Acme Insights, a data analytics platform, bills customers monthly based on the volume of data processed, with invoices generated on the last day of each billing period. For example, if a customer signs up on August 17, their billing periods run from August 17 to August 30, August 31 to September 29, September 30 to October 29, and so on. Invoices are issued on the last day of each billing period, such as August 30 or September 29, to ensure all data usage is captured before billing. This setup provides accurate and transparent invoicing aligned with each customer’s subscription start date and billing cycle.

Proration in Billing

Proration is the process of adjusting charges when a subscription starts or ends partway through a billing period. Proration behavior is defined in the pricing configuration associated with a product. The proration policy includes:

Remainder strategy: Indicates whether any remaining amounts from pricing term calculations are applied at the beginning or end of the billing term.
Allow partial period: Defines whether customers can start or end their subscription partway through a subscription period and pay only for the portion used.
Relation Between Billing Day of Month and Invoice Generation Day

The billing day of the month on the billing schedule determines the day invoices are generated for that month.

If billed in advance, invoices are generated at the start of each billing period.
If billed in arrears, invoices are generated on the last day of each billing period.

The invoice generation depends on the billing frequency and period boundary.
