---
article_id: ind.billing_setup_additional_features.htm
title: Set Up Additional Billing Features
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_additional_features.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Set Up Additional Billing Features

Beyond the core functionality, you can set up and configure various additional Billing features to extend its capabilities. This allows you to tailor Billing to your specific business requirements.

Set Up Milestone Plans for Amendments
Create or link billing milestone plans to amendment billing schedules and recalculate milestone dates and amounts from the amendment start date.
Set Up Financial Accounting Features
Make sure that every billing transaction is compliant with double-entry accounting principles by automatically generating dual transaction journals, each containing both a credit and a debit entry to maintain balanced records. Select a default Data Processing Engine definition that's run to close legal entity accounting periods when your Billing operations user initiates their closure. Set up Billing to show transaction amounts in both the transactional currency and your corporate currency.
Turn On Invoice PDF Document Generation and Account Statement
Before Billing can create PDF documents for invoices, invoice previews, and account statements, enable server-side and batch document generation, then turn on Document Generation in Billing Settings. Batch document generation is required to generate invoice PDF documents from an invoice batch run.
Turn On Email Delivery of Invoices
Send emails with invoice information along with invoice PDF documents to your customers.
Turn On Sequential Numbering Features
Apply unique, gapless sequence numbers to transaction records to ensure financial compliance and a clear audit trail. You can also mandate assigning an invoice number to every posted invoice.
Set Up Credit Memo Features
Set up Billing to automatically create credit memos from negative invoice lines and apply them to settle outstanding invoice balances, and to configure whether credits apply to invoices or invoice lines.
Set Up Invoice Risk Scoring to Predict Risk Scores for Invoices (Pilot)
A risk score for an invoice predicts the likelihood that payment for an open invoice is delayed beyond its due date. The score estimates the probability of late payment based on patterns and signals such as historical payment behavior, invoice aging, outstanding balances, customer payment trends, dispute history, and other relevant account characteristics.
Set Up Payment Features for Revenue Management
Set up Payments to streamline the management of the entire payment lifecycle. By establishing a secure connection with native and third-party payment providers, you can directly process payments for customer transactions within your Salesforce environment.
Define Rules and Order to Apply Credit Memo and Payments
Define the rules and the order in which credit memos and payments are applied to settle the balances of posted invoices or invoice lines within the same account.
Self-Service Billing Portal
The self-service billing portal is a customer-facing Experience Cloud site that enables end users and community users to raise and track their billing inquiries and disputes. Your customers can view and download invoice PDF documents and quickly pay the outstanding balances of invoices by using supported payment methods. The self-service portal minimizes manual intervention and improves cash flow and customer satisfaction.
