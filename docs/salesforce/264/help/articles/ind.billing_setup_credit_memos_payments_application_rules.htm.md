---
article_id: ind.billing_setup_credit_memos_payments_application_rules.htm
title: Define Rules and Order to Apply Credit Memo and Payments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_credit_memos_payments_application_rules.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-09-04
---

# Define Rules and Order to Apply Credit Memo and Payments

Define the rules and the order in which credit memos and payments are applied to settle the balances of posted invoices or invoice lines within the same account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To enable Billing features:	Billing Admin permission set
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
Select the order in which credit memos and payments are applied.
The default selection is Payments First, which applies payments to the posted invoices before credits.
Select these predefined rules in the sequence in which you want to run them.
To apply credit memos or payments only if an invoice is specified on the Reference Entity field of the Credit Memo record or on the Invoice field within the Payment record's payment initiation source, select Match ID. Select this rule only if the invoice is referenced on the Credit Memo or Payment records.
To apply credit memos and payments to invoices that have the same balance, select Match Balance.
To apply credit memos or payments to the invoice with the oldest posted date, select Prioritize Oldest Invoices.
To apply credit memos or payments to the invoice with the highest current outstanding balance, select Prioritize Highest Balance Invoices. When the credit and payment application level is Invoice Line, Billing uses the selected rules to match the invoice. It then applies the credit memo line or payment with highest balance to the invoice line with highest balance on that invoice.
NOTE When there are more than 2000 invoices to be processed, Billing applies only the first rule selected for credit and payment application.
Turn on Rule-Based Credit and Payment Application.
You can enable this feature only if you select the application order and rules.
NOTE When both Rule-Based Credit and Payment Application and Apply Credits to Posted Invoices features are turned on, Rule-Based Credit and Payment Application takes precedence.

The balance of credit memos and payments are applied to settle the balances of posted invoices based on these rules and the credit, refunds, and payment application level when your users perform one of these tasks.

Schedule an invoice batch run
Generate invoices for accounts or orders
Use Post Draft Invoices in Batch API
Run the Post Draft Invoice Batch Run action

To apply rule-based credit and payment application on existing invoices of an account, use Rules Application API.

Invalid Match ID During Payment Application
When a payment is applied using the Match ID rule, the invoice ID specified on the payment record is validated. If the referenced invoice is deemed invalid, the payment is applied to the next available invoice based on the subsequent rule in the sequence.
Example: Apply Rule-Based Credits and Payments
Explore an example to understand the setup of rule-based credits and payments in your Salesforce org, and how credit memos and payments are applied to posted invoices of the same account.
