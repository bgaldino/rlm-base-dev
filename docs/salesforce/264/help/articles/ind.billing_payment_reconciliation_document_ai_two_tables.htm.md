---
article_id: ind.billing_payment_reconciliation_document_ai_two_tables.htm
title: Understand Why Document AI Extracts a Payment Advice Into Two Tables
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_document_ai_two_tables.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-09-04
---

# Understand Why Document AI Extracts a Payment Advice Into Two Tables

When Document AI processes a payment advice, it writes the data into two related tables, but it writes a payment proof into one. Understand why before you configure the output data lake objects (DLOs).

A single payment advice can claim to pay one or more invoices with one payment. For example, a customer sends one $10,000 payment that settles several open invoices. To represent that relationship, the payment advice output DLO uses two tables in a one-to-many relationship.

A header table holds the payment-level details that apply to the whole payment: who paid, how much, when, and by what payment method.
An invoice-level table holds one record per invoice that the payment covers, with the amount applied to each invoice and any deduction applied.

This two-table extraction layer mirrors the reconciliation layer that consumes it. The extraction objects PaymentAdvice (payment header) and PaymentAdviceLineInvoice (invoices) populate the reconciliation objects PaymentAdviceReconciliation (payment header) and PaymentAdviceInvoiceRecile (invoices). Both layers use the same payment and invoice relationship, with a one-to-many structure that runs from the payment extraction process through to the payment reconciliation process.

Here are the columns that you need to add when you configure the output DLOs for payment advice. They map to the PaymentAdvice and PaymentAdviceLineInvoice data model objects.

Add these columns to the payment advice header table.

Payment Advice Id
Payer Name
Payment Amount
Payment Date
Reference Number
Source Document
Transaction Description
Payment Method
Processing Status
Account

Add these columns to the payment advice invoice-level table.

Payment Advice Line Invoice Id
Payment Advice
Invoice Number
Applied Amount
Gross Amount
Deduction Amount
Deduction Code
Created Date Time
Last Modified Date Time
Invoice

However, in case of the payment proof, the output DLO is a single table. A bank statement confirms one transaction that the bank received, which results in one record per confirmed payment. Here are the columns you need to add when you configure the output DLO for payment proof.

Add these columns to the payment proof table.

Payment Proof Id
Transaction Reference Number
Payer Name
Payment Amount
Booking Date
Value Date
Statement Date
Source Document Name
Source Document URL
Credit Debit Indicator
Payment Description
Processing Status
Created Date Time
Last Modified Date Time
Proof Type
Account
