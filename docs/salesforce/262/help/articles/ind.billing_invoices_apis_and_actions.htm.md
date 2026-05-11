---
article_id: ind.billing_invoices_apis_and_actions.htm
title: Manage Invoices by Using APIs or Flow Actions
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoices_apis_and_actions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Manage Invoices by Using APIs or Flow Actions

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Manage Invoices by Using APIs or Flow Actions

Use APIs or Flow actions to generate and update invoices, recover the latest generated invoices for billing schedules, void posted invoices, and send emails with posted invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
GOAL	API
Create or update an invoice scheduler to automatically generate invoices.	Batch Invoice Scheduler API
Generate an invoice for an account, order, or a list of billing schedules.	Invoice Creation API
Ingest or generate an invoice from an internal or external billing transaction data.	Invoice Ingestion API
Update the status of an invoice from Draft to Posted.	

Invoice Draft to Posted Status API

To automate the process of updating the status of an invoice from Draft to Posted, build a custom flow and use the Post Draft Invoice action.


Update a batch of invoices from Draft to Posted status for a credit memo application.	

Batch Invoices Draft to Posted Status API

To automate the process of updating the status of a batch of invoices from Draft to Posted for a credit memo application, build a custom flow and use the Post Draft Invoice Batch Run action.


Recover the latest generated invoice associated with the billing schedules in the Error or Processing status.	

Billing Schedule Recovery List API

To automate the process of recovering one or more billing schedules in the Error or Processing status, build a custom flow and use the Recover Billing Schedules action.


Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the Processing, Void In Progress, or Error status.	Invoice Run Recovery API
Void a posted invoice to rebill the customer.	Void a Posted Invoice API
Send emails for the posted invoices of a specified invoice batch run ID.	Send Emails for Posted Invoices API
