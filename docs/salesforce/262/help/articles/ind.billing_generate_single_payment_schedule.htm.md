---
article_id: ind.billing_generate_single_payment_schedule.htm
title: Generate a Single Payment Schedule for Multiple Invoices of an Account
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_generate_single_payment_schedule.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate a Single Payment Schedule for Multiple Invoices of an Account

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Generate a Single Payment Schedule for Multiple Invoices of an Account

To consolidate payment schedules for an account’s invoices, configure the payment schedule treatment, set the grouping source as Account, and add a due date window.

Confirm that payment schedule treatments are configured in your Salesforce org. Verify that the invoices you want to consolidate use the same currency and saved payment method.

From the App Launcher, find and select Payment Schedule Treatment.
Select Account as the grouping source to group the invoices by account.
The default value is Invoice, which creates one payment schedule and payment schedule item per invoice.
Enter the number of days to use as the due date window.
Billing calculates each invoice’s due date as the invoice date plus the payment term period. Invoices whose due dates fall within this range are grouped together.
Save your changes.

When you post invoices for the account, Billing automatically evaluates them against the consolidation criteria and creates a consolidated payment schedule for the invoices that qualify the grouping criteria. The total amount on the payment schedule is the sum of all invoice amounts in the grouped invoices. The target payment processing date is the earliest due date among all invoices in the group.
