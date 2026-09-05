---
article_id: ind.billing_payment_reconciliation_document_ai_tables_columns.htm
title: Understand How Document AI Maps the Payment Advice Into Tables and Columns
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_document_ai_tables_columns.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-09-04
---

# Understand How Document AI Maps the Payment Advice Into Tables and Columns

Consider the sample payment advice (such as a remittance advice) and the sample payment proof (such as a bank statement) for a single $10,000 ACH payment from Acme Corp against two invoices. Document AI reads each document and writes the values into the corresponding columns.

Here’s the remittance advice document for Acme Corp.

ELEMENT IN THE SAMPLE PAYMENT ADVICE	EXTRACTS TO	TABLE
Payer “Acme Corp”	Payer Name	Header
Total payment amount $10,000	Payment Amount	Header
Payment date March 15, 2026	Payment Date	Header
Remittance reference ACME-RA-20260315	Reference Number	Header
Payment method ACH	Payment Method	Header
INV-1001—$6,000 invoice, $6,000 applied, no deduction	Invoice Number, Gross Amount, Applied Amount	Invoice-level (record 1)
INV-1002—$4,200 invoice, $4,000 applied, $200 EARLYPAY	Adds Deduction Amount and Deduction Code	Invoice-level (record 2)

In INV-1001, the Gross Amount is the invoice’s stated amount, Applied Amount is what the payment actually remits or pays against that invoice, and the difference between them is captured in INV-1002 as Deduction Amount and Deduction Code. So, INV-1001 is a complete match and INV-1002 is a short payment with a deduction.

Here’s the account statement (payment proof) document for Acme Corp.

ELEMENT IN THE SAMPLE PAYMENT PROOF	EXTRACTS TO
Incoming credit from Acme Corp for $10,000	Payer Name, Payment Amount, Credit Debit Indicator (CRDT)
Transaction reference TXN-88231, “ACH CREDIT ACME CORP”	Transaction Reference Number, Payment Description
Booking and value date March 18, 2026; statement dated March 31, 2026	Booking Date, Value Date, Statement Date
Source file AcmeBank_Statement_Mar2026.pdf	Source Document Name, Source Document URL

The payment proof table captures how the bank categorizes the payment, which is what reconciliation matches the payment advice against. For example, Credit Debit Indicator records the direction of funds: CRDT (credit) means money came in, which is what you expect for a customer payment. Payer Name and Payment Amount are the values that reconciliation compares against the payment advice to confirm that the same party paid the same amount. The three dates serve different purposes: Booking Date is when the bank posted the entry, Value Date is when the funds became available, and Statement Date is when the statement was issued. Payment reconciliation compares the payment date on the advice with the date the bank confirmed the payment to calculate the date variance. The date variance, in this case, indicates the normal settlement time gap between when a customer intends to pay and when the funds are actually settled.
