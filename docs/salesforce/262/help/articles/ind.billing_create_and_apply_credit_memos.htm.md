---
article_id: ind.billing_create_and_apply_credit_memos.htm
title: Create and Apply Credit Memos to Invoice Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_create_and_apply_credit_memos.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Create and Apply Credit Memos to Invoice Lines

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Create and Apply Credit Memos to Invoice Lines

Generate credit memos for an account and apply them to invoice and invoice lines that belong to the same account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create credit memos:	

Billing Admin permission set

OR

Credit Memo Operations User permission set

From the App Launcher, find and select Invoices.
Open a posted invoice that includes the invoice lines.
Go to the Invoice Lines tab and select one or more invoice lines to which you want to apply the credit memo
Click Create and Apply Credit Memo.
For each invoice line, enter the credit amount value greater than or equal to zero, and less than or equal to the invoice line balance.
Define the tax calculation strategy.
To calculate taxes automatically based on the credit amount, select Enable tax calculation.
To use the amount in the Credit Tax Amount field instead of automatic tax line calculation, deselect Enable tax calculation and enter a credit tax amount.
To ignore the tax lines, deselect Enable tax calculation and leave the Credit Tax Amount field blank.
Click Create and Apply.
SEE ALSO
Billing Account Overview
