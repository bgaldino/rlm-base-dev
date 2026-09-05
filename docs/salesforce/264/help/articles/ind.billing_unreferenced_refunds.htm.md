---
article_id: ind.billing_unreferenced_refunds.htm
title: Refund Available Credit Balances to Customer Accounts
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_unreferenced_refunds.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_refunds_overview.htm
fetched_at: 2026-09-04
---

# Refund Available Credit Balances to Customer Accounts

Refund a customer’s available credit balance against a credit memo or credit memo line without referencing an original payment.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Header-Level and Line-Level Application

The refund application level determines how Billing applies a refund to a credit memo. In Setup, find and select Billing Settings. In the Credits, Payments, and Refunds section, set Credit, Payment, and Refund Application to the level you want. Select Header Level to refund against credit memos, or Line Level to refund against credit memo lines.

With header-level application, the refund amount applies to the credit memo as a whole. Billing creates a junction record, reduces the credit memo’s pending balance by the refund amount, and sets the refund balance to zero.
With line-level application, Billing distributes the refund amount across the credit memo lines that have an open balance, starting with the line that has the largest open balance, and reduces each line’s balance to zero. Because line-level application distributes the refund automatically, you enter the total refund amount once and Billing allocates it across the lines.
How Billing Resolves the Payment Method

Billing pays an unreferenced refund to a saved payment method. To determine the saved payment method, Billing checks the sources in this order.

First, the payment method that’s passed directly in the API request.
Next, the saved payment method that’s stamped on the credit memo.
Finally, the saved payment method resolved from the associated billing account or billing arrangement.
Synchronous and Asynchronous Payment Gateways

The payment gateway determines when a refund reaches its final status. A synchronous gateway returns a response immediately, so the refund status changes to Processed and Billing applies the refund to the credit memo. An asynchronous gateway doesn’t return an immediate response, so the refund status stays in Pending status. When the gateway confirms the refund, the status changes to Processed and Billing applies the refund to the credit memo.

Issue Refund Against a Credit Memo
Return an available credit balance to a customer by issuing a refund against a credit memo, paid to a saved payment method on a third-party gateway.
