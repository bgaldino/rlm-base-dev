---
article_id: ind.billing_treatment_exclude_from_billing.htm
title: Understand Exclude From Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_treatment_exclude_from_billing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_policies_and_treatments.htm
fetched_at: 2026-09-04
---

# Understand Exclude From Billing

When you set Exclude From Billing on a billing treatment value to Yes, the system skips creating billing schedules, billing schedule groups, and invoices for order items that aren’t ready for billing. Instead of delaying the entire order, you can exclude specific order items and continue processing the rest. When the excluded order items are ready, set Exclude From Billing to No, or assign a billable treatment to the order item, and then reprocess the order so the system reevaluates the items.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Here’s how Exclude From Billing applies to various billing scenarios:

New Sales and Amendments, Renewals, and Cancellations: If you exclude a new sale order item from billing, the system also excludes its related amendment, renewal, or cancellation. The system doesn’t create billing schedules or invoices for those records. If you don’t exclude the related amendment, renewal, or cancellation, the system returns an error because the system can’t find a billing schedule for the original new sale. If the system already processed the new sale, excluding a related amendment, renewal, or cancellation has no effect. The system continues to include that related order item.

Product Bundles: For product bundles where the parent product’s billing treatment has Exclude From Billing set to Yes and child products have it set to No, the system creates billing schedules for the child products only. This behavior applies to new sales and to amendments, renewals, and cancellations.

Ramp Deals: Because multiple segments can be included in ramp deals, the system doesn’t bill or invoice any excluded segment. If you amend a non-billable ramp segment to billable, make sure that the billing reference on the amended order item points to the correct original order item so that billing schedules stay consistent.

Usage-Based Products: For usage-based products, when the order item is excluded from billing, no billing schedule groups or billing schedules are created regardless of the binding type.

To configure this value when you create a treatment, see Create Billing Treatments.
