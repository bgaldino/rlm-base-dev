---
article_id: ind.billing_setup_credit_memo_features_enable.htm
title: Set Up Credit Memo Features
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_credit_memo_features_enable.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Credit Memo Features

Set up Billing to automatically create credit memos from negative invoice lines and apply them to settle outstanding invoice balances, and to configure whether credits apply to invoices or invoice lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To enable Billing features:	Billing Admin permission set
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
To automatically convert all negative invoice lines to credit memo and credit memo lines after the related invoices are posted, turn on Conversion of Negative Invoice Lines to Credit Memo and Credit Memo Lines.
To automatically apply all converted credit memo and credit memo lines to the related invoice and invoice lines, turn on Application of Converted Credit Memo and Credit Memo Lines to Invoice and Invoice Lines.
Select the credit application level. If your Salesforce org has the Agentforce Revenue Management Billing license, the label of this setting is Credit and Payment Application Level.
To apply credits to a specific line on invoices, select Invoice Line.

To apply credits to the total rolled-up balance of invoices, select Invoice.

To automatically apply available credit memo balances to posted invoices, turn on Apply Credits to Posted Invoices.
Select the default flow used to apply the credit memo to invoices.
Select the credit memo and payment application rules.
See Define Rules and Order to Apply Credit Memo and Payments.

After you set up credit memo features, your Credit Memo Operations users can manage credit memos.

SEE ALSO
Automatic Conversion of Negative Invoice Lines into Credit Memo Lines
Automatic Application of Credits to Settle Invoice Balances
Results of Credit Memo Application
