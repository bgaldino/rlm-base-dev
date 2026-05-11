---
article_id: ind.billing_payments_consolidate_invoices.htm
title: Group Multiple Invoices into a Single Payment Request
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments_consolidate_invoices.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Group Multiple Invoices into a Single Payment Request

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Group Multiple Invoices into a Single Payment Request

Reduce payment gateway calls and gateway transaction fees by combining multiple invoices of an account into a single payment request. When you post invoices for an account, Billing automatically consolidates qualifying invoices into one payment schedule and one payment schedule item.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
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
Due Date Window: Specifies the time frame in days based on which the account’s invoices are grouped. All invoices with payment due dates that fall within the due date window are considered for grouping. The payment due date is calculated by adding the period on the payment term item of the associated billing schedule group to the date when the invoice is posted. For example, if an invoice is posted on March 5 and the period is 20, then the payment due date is March 25. For more information, see Create Payment Terms.

Now, when you generate invoices for the account by using the payment batch run, Billing creates a single, consolidated payment schedule and payment schedule item for all of the account’s invoices whose payment due dates fall within the due date window. Billing also populates these fields for the grouped invoices.

The total amount in the Payment Schedule record is the sum of all invoices in the group.
The target payment processing date in the Payment Schedule Item record is the earliest due date among the grouped invoices.

For any invoices whose payment due dates don’t fall within the due date window, Billing generates separate payment schedule and payment schedule items.

Example: Generate Single Payment Schedule and Payment Schedule Item for Multiple Invoices

Let’s consider an example of the Acme account with an associated billing schedule group and payment term. The billing schedules use a common currency and payment method, with payment term periods outlined in the table.

BILLING SCHEDULE	BILLED AMOUNT	PAYMENT TERM PERIOD (IN DAYS)	INVOICE	INVOICE AMOUNT	PAYMENT DUE DATE ON INVOICE	INCLUDED IN CONSOLIDATED PAYMENT REQUEST
A	$500	5	Invoice A	$500	April 6	Yes
B	$100	20	Invoice B	$100	April 21	Yes
C	$400	40	Invoice C	$400	May 10	No

Before you generate invoices for the account:

Make sure to turn on Create Payment Schedules and Payment Schedule Items on the Billing Settings page.
Update the default payment schedule treatment to set the grouping source as Account and due date window to 30.

Now, when you generate invoices for the account on April 1 in Posted status:

Billing generates three invoices: Invoice A, Invoice B, and Invoice C.
Billing sorts the invoices in an ascending order. Starting with the invoice having the earliest due date, Billing groups all invoices within the defined due date window. In the example, Invoice A and Invoice B are grouped together.
Billing creates a single Payment Schedule and Payment Schedule Item record for both Invoice A and Invoice B because they meet the grouping criteria for matching account, payment method, and currency, and they have payment due dates that fall within the due date window of 30 days.
The total requested amount on the Payment Schedule record is $600, which is equal to the sum of Invoice A ($500) and Invoice B ($100).
The target payment processing date on the Payment Schedule Item record is April 6, which is the earlier date among Invoice A and Invoice B.
Billing also generates a separate payment schedule and payment schedule item for Invoice C with a total requested amount of $400 and a target payment processing date of May 10.
Generate a Single Payment Schedule for Multiple Invoices of an Account
To consolidate payment schedules for an account’s invoices, configure the payment schedule treatment, set the grouping source as Account, and add a due date window.
