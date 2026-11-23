---
article_id: ind.billing_payments_consolidate_invoices.htm
title: Group Multiple Invoices into a Single Payment Request
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments_consolidate_invoices.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_schedules_and_payment_schedule_items_auto_manual.htm
fetched_at: 2026-11-23
---

# Group Multiple Invoices into a Single Payment Request

Reduce payment gateway calls and gateway transaction fees by combining multiple invoices of an account into a single payment request. When you post invoices for an account, Billing automatically consolidates qualifying invoices into one payment schedule and one payment schedule item.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To generate a consolidated payment schedule and payment schedule item for multiple invoices on an account:	

Payment Admin permission set

OR

Payment Operations User permission set

How Invoice Grouping Works

When you turn on Create Payment Schedules and Payment Schedule Items on the Billing Settings page, Billing automatically creates a single payment schedule and payment schedule item for each posted invoice associated with an account. You can also generate a consolidated payment schedule and payment schedule item for invoices that match the grouping criteria.

Invoices with the same currency and payment method
Invoices with payment due dates that fall within the predefined due date window

Before you generate a consolidated payment schedule and payment schedule item for a set of invoices for an account, update the default payment schedule treatment for these values.

Grouping Source: Indicates whether to generate payment schedules and payment schedule items per invoice or per account. To group invoices by account, set the grouping source as Account. The default grouping source is Invoice, which creates one payment schedule and payment schedule item per posted invoice.

When you set the grouping source to Account, Billing records the payment schedule in the Payment Schedule field on the invoice, even when payment of only one invoice is processed for a payment schedule item.

Due Date Window: Specifies the time frame in days based on which the account’s invoices are grouped. All invoices with payment due dates that fall within the due date window are considered for grouping. The payment due date is calculated by adding the period on the payment term item of the associated billing schedule group to the date when the invoice is posted. For example, if an invoice is posted on March 5 and the period is 20, then the payment due date is March 25. For more information, see Create Payment Terms.

Now, when you generate invoices for the account by using the payment batch run, Billing creates a single, consolidated payment schedule and payment schedule item for all of the account’s invoices whose payment due dates fall within the due date window. Billing also populates these fields for the grouped invoices.

The total amount in the Payment Schedule record is the sum of all invoices in the group.
The target payment processing date in the Payment Schedule Item record is the earliest due date among the grouped invoices.

For any invoices whose payment due dates don’t fall within the due date window, Billing generates separate payment schedule and payment schedule items.

Generate a Single Payment Schedule for Multiple Invoices of an Account
To consolidate payment schedules for an account’s invoices, configure the payment schedule treatment, set the grouping source as Account, and add a due date window.
Example: Generate Single Payment Schedule and Payment Schedule Item for Multiple Invoices
Let’s consider an example of the Acme account with an associated billing schedule group and payment term.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payments_consolidate_invoices.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
