---
article_id: ind.billing_payment_terms_usecase.htm
title: "Examples: Payment Terms"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_terms_usecase.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_terms.htm
fetched_at: 2026-09-04
---

# Examples: Payment Terms

Explore two examples that demonstrate how payment terms determine the payment due dates for invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Net 30 Payment Term

A software company provides a subscription service and wants to use the Net 30 payment term for its subscription service. The company's Salesforce admin creates a draft payment term and a related payment term item with these values:

Type: Period-Based
Period: 30
Payment Timeframe: Standard
Period Unit: Days

The admin then activates the payment term and assigns it to the relevant order. When invoices are posted for that order, the due date is calculated by adding 30 days to the invoice date. For example, if an invoice is posted on July 1, the due date is calculated by adding 30 days, making the payment due by July 31.

Net 45 EOM Payment Term

A construction company completes a phase of a project and wants to use the Net 45 EOM payment term for the project. The company's Salesforce admin creates a draft payment term and a related payment term item with these values:

Type: Derive End of Month and Add Period
Period: 45
Payment Timeframe: Standard
Period Unit: Days

The admin then activates the payment term and assigns it to the relevant order. When invoices are posted for that order, the due date is calculated by adding 45 to the last day of the month in which the invoice is posted. For example, if an invoice is posted on April 15, the system first finds the last day of the month (April 30) and then adds 45 days. This makes the payment due by June 14.
