---
article_id: ind.billing_payment_terms.htm
title: Create Payment Terms
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_terms.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_policies_and_treatments.htm
fetched_at: 2026-05-11
---

# Create Payment Terms

Create Payment Terms

Negotiate and define payment terms to set a due date for payments and collect payments in a timely manner. You can anticipate or enforce the date by when payments for outstanding invoices must be paid.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create payment terms and payment term items:	Billing Admin permission set
Create Payment Terms

A payment term is a formal agreement that defines the date by which an invoice must be paid.

From the App Launcher, find and select Payment Terms.
Click New.
Enter a name for the payment term.
Select a status.

When you create payment terms, you can select the status as either Draft or Inactive. If you select the status as Inactive, you can't change it to Draft.

You can't select the status as Active without creating a related payment term item.

To make this the default payment term for your Salesforce org, select Default.
If necessary, enter a description.
Save your changes.

After you create a payment term, create a corresponding payment term item.

Create Payment Term Items

Payment term items define the specific configuration for payment terms.

From the App Launcher, find and select Payment Terms.
Open the Payment Term record for which you want to create an item.
On the Payment Term Items related list, click New.
Select a type for the payment term item.
To calculate the invoice due date by adding the period to the invoice date, select Period-Based.
To calculate the invoice due date by adding the period to the last day of the month in which the invoice date falls, select Derive End of Month and Add Period.
Enter the period.
When the type of the payment term item is Derive End of Month and Add Period, to set the due date as the last day of the month in which the invoice is posted, enter 0 as the period.
To indicate that the payment term is for a standard payment, select Standard as the payment timeframe.
Each payment term can have only one payment term item with a Standard payment timeframe.
If you have entered a period, select the unit of measurement for the period.
If necessary, enter a description.
Save your changes.

After you create the payment term item, complete these steps:

Change the status of the payment term to Active. Only active payment terms can be used to determine the due dates of invoices.
Go to the Order records and specify the relevant payment term.
NOTE If you don't specify payment terms for orders, the default payment term for your Salesforce org is used.

The same payment terms are autopopulated for the billing schedules that are generated for these orders, and eventually used to determine the due dates of the invoices.

Payment Terms Use Case

Explore two examples that demonstrate how payment terms determine the payment due dates for invoices.

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
