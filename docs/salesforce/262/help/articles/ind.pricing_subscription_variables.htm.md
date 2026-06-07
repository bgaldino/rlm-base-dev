---
article_id: ind.pricing_subscription_variables.htm
title: Common Proration Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_subscription_variables.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Common Proration Examples

These examples demonstrate how various proration settings impact the final subscription price for a product with a Selling Model Type of TermDefined.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
Key terminologies
AlignToCalendar: The billing period starts on the first day of the calendar period (e.g., the 1st of the month for monthly subscriptions, or January 1st for annual subscriptions). If a business wants all monthly subscriptions to be billed from the 1st of the month, they would set this to AlignToCalendar.
Anniversary: The billing period starts on the subscription start date (the Effective From date).
DayOfPeriod: The billing period starts on a specific day of the month (and specific month for annual subscriptions) defined by the administrator. The parameters Start Proration Day and Start Proration Month are relevant and used only if Start Proration Period = DayOfPeriod.
EndOfPeriod: The billing period starts on the last day of the period.
Annual Proration Examples
Demonstrates how the system calculates pricing based on a yearly billing cycle.
Semi-Annual Proration Examples
Demonstrates how the system calculates pricing based on 6-month billing intervals.
Quarterly Proration Examples
Demonstrates how the system calculates pricing based on 3-month billing intervals.
Monthly Proration Examples
Demonstrates how the system calculates pricing based on a monthly billing cycle.
Annual Proration Examples for Leap Years
Review calculations for annual billing cycles, and learn how the total days adapt to leap years. Salesforce Pricing uses a specific design convention to handle end-of-month anniversary dates. Rather than relying on simple date increments, Salesforce Pricing adjusts period end dates to accommodate the presence or absence of February 29 so that it calculates full periods logically based on date availability.
Monthly Proration Examples for Leap Years
Review calculations for monthly billing cycles, and learn how the total days adapt to leap years and varying month lengths. For a monthly product selling model, Salesforce Pricing anchors exactly to the numerical start date. If an anniversary subscription starts on the 29th, 30th, or 31st, and that exact date doesn't exist in the following month, Salesforce Pricing uses a design convention: it aligns the next period to the latest available day of that subsequent month. All full periods behave as "month-end to month-end minus one.
