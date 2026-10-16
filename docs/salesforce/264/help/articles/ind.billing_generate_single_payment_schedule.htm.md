---
article_id: ind.billing_generate_single_payment_schedule.htm
title: Generate a Single Payment Schedule for Multiple Invoices of an Account
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_generate_single_payment_schedule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments_consolidate_invoices.htm
fetched_at: 2026-09-04
---

# Generate a Single Payment Schedule for Multiple Invoices of an Account

To consolidate payment schedules for an account’s invoices, configure the payment schedule treatment, set the grouping source as Account, and add a due date window.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
The Salesforce Payments feature is available with the Revenue Management Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Management Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.

Confirm that payment schedule treatments are configured in your Salesforce org. Verify that the invoices you want to consolidate use the same currency and saved payment method.

From the App Launcher, find and select Payment Schedule Treatment.
Select Account as the grouping source to group the invoices by account.
The default value is Invoice, which creates one payment schedule and payment schedule item per invoice.
Enter the number of days to use as the due date window.
Billing calculates each invoice’s due date as the invoice date plus the payment term period. Invoices whose due dates fall within this range are grouped together.
Save your changes.

When you post invoices for the account, Billing automatically evaluates them against the consolidation criteria and creates a consolidated payment schedule for the invoices that qualify the grouping criteria. The total amount on the payment schedule is the sum of all invoice amounts in the grouped invoices. The target payment processing date is the earliest due date among all invoices in the group.
