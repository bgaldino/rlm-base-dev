---
article_id: ind.billing_payments_consolidate_invoices_example.htm
title: "Example: Generate Single Payment Schedule and Payment Schedule Item for Multiple Invoices"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments_consolidate_invoices_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments_consolidate_invoices.htm
fetched_at: 2026-11-23
---

# Example: Generate Single Payment Schedule and Payment Schedule Item for Multiple Invoices

Let’s consider an example of the Acme account with an associated billing schedule group and payment term.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.

Before you generate invoices for the account:

The billing schedules use a common currency and payment method, with payment term periods outlined in the table.

BILLING SCHEDULE	BILLED AMOUNT	PAYMENT TERM PERIOD (IN DAYS)	INVOICE	INVOICE AMOUNT	PAYMENT DUE DATE ON INVOICE	INCLUDED IN CONSOLIDATED PAYMENT REQUEST
A	$500	5	Invoice A	$500	April 6	Yes
B	$100	20	Invoice B	$100	April 21	Yes
C	$400	40	Invoice C	$400	May 10	No
Make sure to turn on Create Payment Schedules and Payment Schedule Items on the Billing Settings page.
Update the default payment schedule treatment to set the grouping source as Account and due date window to 30.

Now, when you generate invoices for the account on April 1 in Posted status:

Billing generates three invoices: Invoice A, Invoice B, and Invoice C.
Billing sorts the invoices in an ascending order. Starting with the invoice having the earliest due date, Billing groups all invoices within the defined due date window. In the example, Invoice A and Invoice B are grouped together.
Billing creates a single Payment Schedule and Payment Schedule Item record for both Invoice A and Invoice B because they meet the grouping criteria for matching account, payment method, and currency, and they have payment due dates that fall within the due date window of 30 days.
The total requested amount on the Payment Schedule record is $600, which is equal to the sum of Invoice A ($500) and Invoice B ($100).
The target payment processing date on the Payment Schedule Item record is April 6, which is the earlier date among Invoice A and Invoice B.
Billing also generates a separate payment schedule and payment schedule item for Invoice C with a total requested amount of $400 and a target payment processing date of May 10.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payments_consolidate_invoices_example.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
