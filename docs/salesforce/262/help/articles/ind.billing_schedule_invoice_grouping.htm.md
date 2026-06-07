---
article_id: ind.billing_schedule_invoice_grouping.htm
title: Define Invoice Grouping on a Billing Schedule
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedule_invoice_grouping.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Define Invoice Grouping on a Billing Schedule

Generate grouped or split invoices by configuring default, custom, or billing schedule group types on billing schedules.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To edit billing schedules:	

Billing Admin permission set

OR

Billing Operations User permission set

On the billing schedule, define the invoice grouping type. Consolidated or individual invoice records are created based on the invoice grouping type.

From the App Launcher, find and select Billing Schedule Groups.
Open the billing schedule group that your billing schedule belongs to.
Go to the Billing Schedules related list and open the billing schedule.
On the Detail tab of the Billing Schedule record, go to the Invoice Group Information section and select an invoice group type:
To generate a consolidated invoice based on the default group, select Default. The billing account, bill-to-contact, currency ISO code, payment term, tax engine, legal entity, and saved payment method of the billing schedule group make up the default group.
To generate a separate invoice for the billing schedule, select Billing Schedule.
To generate a consolidated invoice based on your own grouping criteria, select Custom.
If you select Custom as the invoice group type, enter a custom invoice group key.
The custom invoice group key isn't case-sensitive. The key can be contract number, purchase order number, account, legal entity, or your own value. Consolidated invoices are generated when the billing schedules have the same default group and custom invoice group key. While grouping invoices during invoice generation process, the default group is considered first, followed by the custom invoice group key.
EXAMPLE A billing operations user selects specific invoice group types for five billing schedules of an order.
BILLING SCHEDULES	INVOICE GROUP TYPE	CUSTOM INVOICE GROUP KEY
Billing Schedule 1	Default	

—


Billing Schedule 2	Billing Schedule	

—


Billing Schedule 3	Custom	00000101 [Contract Number]
Billing Schedule 4	Default	

—


Billing Schedule 5	Custom	00000101 [Contract Number]

Three separate invoices are generated based on the Invoice Group Type field, and the Custom Invoice Group Key field:

A consolidated invoice is generated for Billing Schedule 1 and Billing Schedule 4 because both of them have the same default invoice group.
A separate invoice is generated for Billing Schedule 2 because its invoice group type is Billing Schedule, which results in generating an individual invoice.
A consolidated invoice is generated for Billing Schedule 3 and Billing Schedule 5 because both of them have the same default invoice group and custom invoice group key.
