---
article_id: release-notes.rn_billing_schedules_arrangements.htm
title: Billing Schedules and Billing Arrangements
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_schedules_arrangements.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-09-30
---

# Billing Schedules and Billing Arrangements

Amend billing frequencies on existing subscriptions or orders. Bill weekly or bill at custom intervals that span longer periods. Skip charges for periods that fall within a future-dated suspension, surface ramp segment identifiers on billing schedules for new-sale ramp deals, and automatically compute price uplifts on multiyear ramp deals.

Change Billing Frequency on Active Subscriptions Anytime
Your sales reps can now update the billing frequency of an active subscription, from any cadence to any other, such as monthly to annual billing or vice versa, without canceling or recreating the subscription. When your sales reps make a zero-quantity amendment to update the billing frequency, Billing automatically prorates the charges and applies the new billing cadence from the effective date. With the Revenue Cloud Billing license, your billing ops team can also update the frequency by using the Create Standalone Billing Schedules API with added flexibility to set the billing start month.
Support Flexible Billing With Weekly Cadences
Serve customers who prefer frequent billing cycles, whether it’s every week or every 6 weeks, by selecting weekly frequency on quotes and orders. Billing automatically prorates the billing period amounts and generates billing schedules for the chosen weekly cadence.
Bill Every Few Weeks, Months, or Years Instead of Every Term
Your sales reps can now set up flexible subscriptions billing terms whether it's every three weeks, every five months, or every two years. For example, to bill a subscription every three months, your sales reps can set the billing frequency to monthly and billing term to 3 on the order product. Billing automatically calculates the correct amount for the combined period and sets the next billing date accordingly.
Honor Future-Dated Billing Suspensions During Invoicing
Process future-dated invoices while honoring billing suspensions as of the target date rather than the run date. If the target date falls in the suspension time frame, billing period items aren't created for the suspended period, eliminating the need to backdate suspensions to prevent charges during suspension.
Track Ramp Deal Details on Billing Schedules
See ramp identifiers on billing schedules for new-sale ramp deals. Billing populates ramp-specific fields, such as Ramp ID, Segment ID, Segment Name, and Segment Type, to identify ramp segments and explain pricing details.
Automate Compound Price Uplifts for Multiyear Ramp Deals
Compound uplift builds each ramp segment's price on the net price of the segment before it, not the original list price. Multiyear deals no longer need manual, error-prone uplift calculations outside Salesforce, and deal approvers get an accurate number right away. The same compounding logic carries through amendments and renewals, and billing schedules reflect the compounded price automatically once you activate the order.
