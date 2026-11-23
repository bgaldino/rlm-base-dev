---
article_id: ind.billing_issue_unreferenced_refund.htm
title: Issue Refund Against a Credit Memo
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_issue_unreferenced_refund.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_unreferenced_refunds.htm
fetched_at: 2026-11-23
---

# Issue Refund Against a Credit Memo

Return an available credit balance to a customer by issuing a refund against a credit memo, paid to a saved payment method on a third-party gateway.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To issue an unreferenced refund:	

Payment Admin permission set

OR

Payment Operations User permission set

Before you issue an unreferenced refund, confirm that the customer has an available credit balance on the credit memo, that the account uses a supported third-party payment gateway, and the payment gateway supports processing of unreferenced refunds. Also, make sure that a saved card payment method is available on the credit memo or billing account.

Open the credit memo that has the available credit balance you want to refund.
Confirm the available credit balance and the saved payment method on the credit memo.
If no saved payment method is stamped on the credit memo, Billing resolves one from the billing account. To refund to a specific card, select the saved payment method on the credit memo.
Issue the refund against the credit memo or a credit memo line, and enter the refund amount.
With header-level application, the refund applies to the credit memo as a whole. With line-level application, Billing distributes the refund amount across the credit memo charge lines that have an open balance, starting with the line that has the largest open balance.
Submit the refund.
Billing sends the refund to the saved payment method through the third-party payment gateway and reduces the outstanding credit balance. On a synchronous gateway, the refund status changes to Processed. On an asynchronous gateway, the status stays Pending until the gateway confirms the refund, and then changes to Processed.
EXAMPLE

A customer has an available credit balance of $200 on a credit memo set for header-level application. You issue an unreferenced refund of $200 against the credit memo, paid to the customer's saved card. Billing reduces the credit memo's pending balance by $200 and sets the refund balance to zero.

To confirm the refund reached the customer, check the refund status. If the status stays Pending on an asynchronous gateway, wait for the gateway to confirm the refund before you take further action.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_issue_unreferenced_refund.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
