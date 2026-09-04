---
article_id: ind.billing_policies_and_treatments.htm
title: Define Billing Policies and Billability Rules
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_policies_and_treatments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Define Billing Policies and Billability Rules

Define billing policies, treatments, and treatment items to generate invoices that suit your sales models. Specify product billability rule criteria to define whether you want to bill your products in advance or in arrears, whether specific products are billed, and other conditions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Create Billing Policies, Treatments, and Treatment Items
Define billing policies, treatments, and treatment items to generate invoices that suit your sales models.
Understand Exclude From Billing
When you set Exclude From Billing on a billing treatment value to Yes, the system skips creating billing schedules, billing schedule groups, and invoices for order items that aren’t ready for billing. Instead of delaying the entire order, you can exclude specific order items and continue processing the rest. When the excluded order items are ready, set Exclude From Billing to No, or assign a billable treatment to the order item, and then reprocess the order so the system reevaluates the items.
Understand Billing Treatment Resolution
The billing treatment field of an order product determines how it is billed. If the billing treatment is missing on the order product, an attempt is made to resolve the issue and assign an active billing treatment during the resolution.
