---
article_id: ind.billing_payment_reconciliation.htm
title: Automate Payment Reconciliation
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-09-04
---

# Automate Payment Reconciliation

Accelerate cash collection by automating payment reconciliation between the payment advice records your customers send and the payment proofs your bank confirms. Billing uses Document AI to extract payment data from payment advice documents, lockbox files, or emails, and automatically matches the payment data against payment proofs such as bank statements. Your accounts receivable team can then review all matched and unmatched transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Payment Reconciliation Workflow

When a customer pays, you often receive two kinds of documents–a payment advice and a payment proof. A payment advice such as a remittance advice lists what the customer claims to pay. A payment proof, such as a bank statement, confirms what the bank received. Payment reconciliation ingests both document types, extracts the data, and compares it with your invoices. It then matches a customer’s payment advice with the bank’s payment proof and with open invoices, so that each payment can be applied to the correct account and invoice amount.

The end-to-end process involves these stages.

Set up a Salesforce CRM connection in a Data 360 org.
Ingest payment advice and payment proof documents from an external source, such as Google Drive, into Data 360.
Use Document AI in Data 360 to extract structured data from the unstructured documents.
Create a custom batch data transform to transform the text and numeric data parsed by Document AI into valid data types required for payment reconciliation in Billing.
Map the output of the custom batch data transform to the out-of-the-box data model objects (DMO).
Create a vector search index to enhance searchability of the data.
Deploy the payment reconciliation data kit.
Run the batch data transforms.
Review the matched and unmatched results.
Understand How Payment Reconciliation Evaluates a Match
Payment reconciliation first checks whether the currency ISO code matches between the payment advice and payment proof documents. If yes, then it compares each payment against three criteria and records how closely the values align, so your accounts receivable team can review the results.
Understand Why Document AI Extracts a Payment Advice Into Two Tables
When Document AI processes a payment advice, it writes the data into two related tables, but it writes a payment proof into one. Understand why before you configure the output data lake objects (DLOs).
Understand How Document AI Maps the Payment Advice Into Tables and Columns
Consider the sample payment advice (such as a remittance advice) and the sample payment proof (such as a bank statement) for a single $10,000 ACH payment from Acme Corp against two invoices. Document AI reads each document and writes the values into the corresponding columns.
Set Up Payment Reconciliation
Set up payment reconciliation by preparing your payment data in Data 360 and deploying the payment reconciliation data kit that Billing uses to match payments against your invoices.
Reconcile Payment Advice and Payment Proof with Bank Data
Payment reconciliation connects the data you prepared in Data 360 with your billing records. After you share your payment advice and payment proof documents through the connector of your choice, Data 360 ingests them, Document AI extracts the data, and your batch data transforms convert it into the fields that Billing needs. When you run the reconciliation transforms, Billing pulls in this data, matches each payment advice against the bank’s payment proof and your open invoices, and creates reconciliation records. Your accounts receivable team then reviews the matched and unmatched records.
