---
article_id: ind.billing_frequency_change_flow_impact.htm
title: Manage Billing Frequencies
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_frequency_change_flow_impact.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_and_schedule_groups.htm
fetched_at: 2026-09-04
---

# Manage Billing Frequencies

You can set a product’s billing frequency to be different from its pricing frequency. For example, you can bill a customer on an annual basis even if the order or subscription is priced monthly.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Key Terms

Review these terms that define how often a customer is billed and how the billing periods are calculated.

Billing Frequency
The time period that indicates how often an order product is billed. The billing frequency indicates the cadence, such as Weekly, Monthly, Quarterly, Semi-Annual, Annual, or Milestone Plan, that determines how often a billing period item is generated.
Billing Period

The duration or span of time over which an order product is billed.

Billing Period Item
The specific billing information for a billing period. The billing period item record contains billing information, such as the amount, billing period start date, and billing period end date, that’s passed to an invoice line during the invoice batch run.
Billing Term Unit

The unit of time, such as Week, Month, Quarter, Semiannual, or Year, that’s used to measure the billing term. The billing term unit indicates the billing frequency such as Weekly, Monthly, Quarterly, and so on.

Billing Term

The number of billing term units to combine into a single billing period item. The default value is 1 and the maximum value is 1,200.

How Billing Frequency is Carried Into Billing Schedules

When you set the billing frequency on an order product, or change it from the frequency inherited from the product’s pricing, and then activate the order, Billing automatically generates updated billing schedules for the selected billing frequency. These billing schedules are picked up by the invoice batch run to generate invoices.

Considerations

Here are a few things to keep in mind when you change the billing frequency on orders and subscriptions.

On existing orders or active subscriptions, you can change the billing frequency only through a zero-quantity, amend transaction that uses the field amendment subtype, and not during a renew or cancel transaction.
You can’t change the billing frequency from weekly to any other frequency and vice versa.
You can’t change the billing term on the quote line item or order products during amendments, renewals, or cancellations, or when you use Create Standalone Billing Schedules API.
You can’t change the billing term on existing billing schedules.
For an evergreen subscription, consider the following behavior before changing the billing frequency. For example, a product priced at $100 per year when billed monthly prorates to $8.3333 per month, which Billing bills as $8.33. Over 12 months, the total billed amount adds up to $99.96, which is $0.04 less than the $100 original annual price.
About Period Boundaries and Billing Day of Month
You can adjust when billing periods start and how charges are calculated by using flexible date settings that align with your business model and customer preferences. You can use the Period Boundary, Period Boundary Day, and Period Boundary Start Month fields on the order product, to define when billing begins, how billing periods are segmented, and how proration is applied. The period boundary on the order product ‌defines how the billing period is calculated. The Billing Day of the Month field on the Billing Schedule record specifies the day you expect to bill the customer. Together, these fields define how billing periods align with the transaction timeline and how Billing in Revenue Management calculates and groups charges on invoice lines.
Change Billing Frequency on New and Existing Subscriptions
You can update the billing frequency of a subscription at any time, such as by switching from monthly to annual or from annual to monthly. On active subscriptions, you can update the billing frequency from any cadence to any other, such as monthly to annual billing or vice versa, without canceling or recreating the subscription. To achieve this, sales reps make a zero-quantity, field amendment for the asset, to update the billing frequency, Billing automatically prorates the charges and applies the new billing cadence from the effective date.
Field Combination Requirements
The combination of billing frequency, period boundary, period boundary day, and period boundary start month determines billing behavior.
