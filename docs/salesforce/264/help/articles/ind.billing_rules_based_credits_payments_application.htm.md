---
article_id: ind.billing_rules_based_credits_payments_application.htm
title: Invalid Match ID During Payment Application
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_rules_based_credits_payments_application.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_credit_memos_payments_application_rules.htm
fetched_at: 2026-09-04
---

# Invalid Match ID During Payment Application

When a payment is applied using the Match ID rule, the invoice ID specified on the payment record is validated. If the referenced invoice is deemed invalid, the payment is applied to the next available invoice based on the subsequent rule in the sequence.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

An invoice is considered invalid for the Match ID rule in these scenarios.

The Invoice ID specified on the Payment record is in Draft status.
The referenced invoice is posted but has a zero balance.
The legal entity of the referenced invoice and the payment are different.
The related account of the referenced invoice and the payment are different.
The currency ISO code of the referenced invoice and the payment are different.
