---
article_id: ind.billing_account_statement_generate.htm
title: Generate an Account Statement
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_generate.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_account_statement.htm
fetched_at: 2026-11-23
---

# Generate an Account Statement

Use the Generate Account Statement quick action on an account to produce a PDF statement without leaving the page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To generate statement of account:	

Billing Admin permission set

Or

Billing Operations User permission set


To use the account statement PDF:	

DocGen User permission set

AND

Omnistudio User permission set

For the personas and permission sets for Omnistudio Document Generation, see Personas and Permission Set Licenses for Omnistudio Document Generation.

NOTE Before you generate account statements, turn on Document Generation from Billing Settings.
From the App Launcher, find and select Accounts.
Open the account record that you want to generate the statement for.
Click Generate Account Statement.
Verify the primary account that you’re generating the statement for.
Select the related accounts to include in the statement.
Select the billing transactions to include by transaction type.
By default, all invoices, credit memos, debit memos, payments, and refunds are selected.
Select a document template.
If you don’t select a template, Billing uses the template on the billing profile, or the Default Account Statement Template when the billing profile doesn’t specify one.
Select the start date.
The statement reflects the current outstanding balance and can’t calculate the balance for a past end date. Therefore, the end date defaults to today and can’t be changed.
Select how to sort the transactions, and select the sorting order.
Generate the statement.

The system generates the statement asynchronously. When processing completes, the PDF is saved in the Files related list on the account.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_generate.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
