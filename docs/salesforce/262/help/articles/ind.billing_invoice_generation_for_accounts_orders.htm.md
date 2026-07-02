---
article_id: ind.billing_invoice_generation_for_accounts_orders.htm
title: Generate Invoices for Accounts or Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_generation_for_accounts_orders.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate Invoices for Accounts or Orders

Generate all the pending invoices of your customers in one go and on-demand. You can also generate consolidated invoices on-demand based on the invoice group type of the related billing schedules.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To generate invoices for accounts or orders:	

Billing Operations User permission set

OR

Billing Customer Service User permission set

The Generate Invoices quick action is available by default on the Account object's page layout. To generate invoices for orders, add the quick action to the Order object's page layout.

From the App Launcher, find and select Accounts or Orders.
Open the Account or Order record that you want to generate an invoice for.
From the quick actions menu, click Generate Invoices.
Select a target date.
Invoices are generated for all the related billing schedules that have the next billing date before the target date, and also have the status as Ready for Invoicing.
Select the date that you want to show on the invoice.
Select whether you want to generate draft invoices or posted invoices.
Click Generate.

A Create Invoices By Using Billing Schedules API request is created. After the request is processed, users are notified of the response.

Invoices generated for accounts appear in the Invoices related list of the Account records. Invoices generated for orders appear in the All Invoices related list of the Order records.

The All Invoices related list on the Order record page is available from Spring ’26. For the Salesforce orgs created in or upgraded to Spring ’26, perform a one-time task of adding the All Invoices related list on the Order page layout.

Invoices aren’t generated for any related billing schedules that are suspended for billing. If multiple billing schedules are processed at a time for generating invoices and any of them are suspended for billing, invoices aren’t generated for any of those billing schedules. When invoices aren't generated for billing schedules because they’re invalid or suspended for billing, Revenue Transaction Error Log records are created. These records appear in the Revenue Transaction Error Logs related list of the Account or Order record.

SEE ALSO
Define Invoice Grouping on a Billing Schedule
Suspend and Resume Billing
