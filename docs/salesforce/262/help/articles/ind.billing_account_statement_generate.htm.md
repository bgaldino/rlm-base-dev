---
article_id: ind.billing_account_statement_generate.htm
title: Generate an Account Statement
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_generate.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate an Account Statement

Use the Generate Account Statement quick action on an account to produce a PDF statement without leaving the page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

Account statements use a document template to define the layout of the generated PDF. You can select a custom template created by using Document Generation. If you don’t select a template, the system uses the template defined on the billing profile or the org default template.

From the App Launcher, find and select Accounts.
Open the account record that you want to generate the statement for.
Click Generate Account Statement.
Verify the primary account that you’re generating the statement for.
Select the related accounts to include in the statement.
Select the billing transactions to include by transaction type.
By default, all invoices, credit memos, debit memos, payments, and refunds are selected.
Select a document template.
Select the start date.
The statement reflects the current outstanding balance and can’t calculate the balance for a past end date. Therefore, the end date defaults to today and can’t be changed.
Select how to sort the transactions, and select the sorting order.
Generate the statement.

The system generates the statement asynchronously. When processing completes, the PDF is saved in the Files related list on the account.
