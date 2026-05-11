---
article_id: ind.billing_credit_application_results.htm
title: Results of Credit Memo Application
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_credit_application_results.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Results of Credit Memo Application

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Results of Credit Memo Application

After posted invoices are generated, credits are applied based on the credit application level.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Applying a credit memo or credit memo line reduces the balance of an invoice or an invoice line. For example, applying a $100 credit memo line to a $500 invoice line reduces the invoice line’s balance to $400.

After the credits are applied, the balance amounts and applied credit amounts are automatically updated as shown in this table.

CREDIT APPLICATION LEVEL	UPDATED CREDIT FIELDS	UPDATED INVOICE FIELDS	NEW RECORD
Invoice	

Credit Memo fields:

Net Credits Applied
Settlement Level is Top Level
	

Invoice fields:

Balance
Net Credits Applied
Settlement Level is Invoice
	Credit Memo Invoice Application record
Invoice Line	

Credit Memo Line fields:

Line Amount
Net Credits Applied

Credit Memo fields:

Net Credits Applied
Settlement Level is Line Level
	

Invoice Line fields:

Line Amount
Net Credits Applied

Invoice fields:

Balance
Net Credits Applied
Settlement Level is Invoice Line
	Credit Memo Line Invoice Line record
SEE ALSO
Credit Application Level
