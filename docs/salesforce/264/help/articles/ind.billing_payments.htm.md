---
article_id: ind.billing_payments.htm
title: Process Payments and Issue Refunds in Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-11-23
---

# Process Payments and Issue Refunds in Revenue Cloud

Complete your cash journey by making payments for posted invoices and issuing refunds when needed. Settle open invoice balances in a timely manner and accurately report cash flow by collecting and applying payments. Refund your customers if they change or cancel products or services that they paid for.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 

This flowchart shows how a user with the Payment Operations User permission set can use Payments in Revenue Cloud.

Payments Data Model in Revenue Cloud
The Payments data model depicts the objects and their relationships to manage the processing of customer payments including a timely collection of these payments and their application to appropriate invoices, and issuing refunds when needed.
Set Up Payment Features for Revenue Cloud
Set up Payments to streamline the management of the entire payment lifecycle. By establishing a secure connection with native and third-party payment providers, you can directly process payments for customer transactions within your Salesforce environment.
Payment Schedules and Payment Schedule Items
Payment schedules contain information about a set of payments that a customer wants to pay at different times for a certain record. A payment schedule contains one or more payment schedule items, where each item represents one payment to be processed.
Schedule Payment Batch Runs to Process Payments
Set up a payment scheduler with specific filters to automatically process payments for your transactions. Payment batch runs process existing payment schedules and payment schedule items to collect the corresponding payments, and then apply them to invoices based on the payment application level.
Payment Batch Run Overview
At the start time of the payment scheduler, payment batch runs start processing payment schedule items based on the defined criteria.
Retry Failed Payments
Failed payments slow down cash flow and can lead to lost customers. When you enable automatic payment retries, Billing handles payment failures seamlessly and reprocesses each failed payment without manual intervention. You define a payment retry strategy that applies to all failed payments, with retry rules based on error categories such as insufficient funds or payment processing issues. For greater control and flexibility, you can define retry rules based on specific payment gateways and gateway-specific error codes. For each rule, you can configure the retry intervals that determine how often Billing can attempt to reprocess the failed payment. Additionally, you can set the maximum number of retry attempts, after which Billing either tries an alternate payment method or marks the payment request as failed.
Issue Refunds and Settle Balances
A refund returns an amount that a customer no longer owes, such as an overpayment or an available credit balance. Billing issues a refund either automatically, after you cancel or reduce a subscription, or on demand, when you want to settle a customer’s available credit balance by using a credit memo.
Send Level 2 and Level 3 Payment Data Through Your Payment Gateways
Level 2 and Level 3 processing data are the additional line-item and transaction-level details passed during credit card authorization. Use Level 2 and Level 3 data mainly for business-to-business and business-to-government corporate card transactions to lower fraud risk and get richer reporting. When Level 2 and Level 3 data support is enabled, Billing automatically includes additional transaction data in payment requests that you send through native and third-party payment gateways.
Process Payments and Issue Refunds by Using APIs
Use a suite of APIs to process payments and issue refunds. Authorize and capture payments by using native payment gateways, reverse payment authorizations, tokenize payment methods, and save card details for processing recurring payments. Create and update payment schedulers, and allocate or unallocate payments. You can process ad hoc payments, and refund your customers if they change or cancel products or services that they paid for.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payments.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
