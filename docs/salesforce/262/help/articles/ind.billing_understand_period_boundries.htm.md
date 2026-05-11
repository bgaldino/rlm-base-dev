---
article_id: ind.billing_understand_period_boundries.htm
title: Period Boundary and Proration in Billing Cycles
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_understand_period_boundries.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Period Boundary and Proration in Billing Cycles

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Period Boundary and Proration in Billing Cycles

You can adjust when billing periods start and how charges are calculated by using flexible date settings that align with your business model and customer preferences.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Period Boundaries and Billing Day of Month
You can use the Period Boundary, Period Boundary Day, and Period Boundary Start Month fields on transactions, such as order product, to define when billing begins, how billing periods are segmented, and how proration is applied. The period boundary on the order product ‌defines how the billing period is calculated. The Billing Day of the Month field on the Billing Schedule record specifies the day you expect to bill the customer. Together, these fields define how billing periods align with the transaction timeline and how Billing in Agentforce Revenue Management calculates and groups charges on invoice lines.
Field Combination Requirements
The combination of billing frequency, period boundary, period boundary day, and period boundary start month determines billing behavior.
