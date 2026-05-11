---
article_id: ind.billing_permission_sets.htm
title: Assign Permissions to Access Billing Features
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_permission_sets.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup.htm
fetched_at: 2026-05-11
---

# Assign Permissions to Access Billing Features

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Assign Permissions to Access Billing Features

Assign your users the required permission sets based on their persona, and for the APIs for which they need access.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


The Billing Collections and Recovery Specialist permission set, the Payment Admin permission set, and the Payment Operations User permission set are available only with the the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

All the other permission sets are available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

Create Users and Profiles

To begin, create users for Billing in Agentforce Revenue Management. Then assign users the appropriate permission sets. To help you plan, use the permission set table for Billing. When you create a user, you must also assign a profile to define the default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

Billing Permission Sets by Persona

Billing is managed by users who have different roles and expertise. The permission sets based on personas combine specific permissions that outline each user's responsibilities. All these permission sets are part of the Billing User permission set license. The Billing Customer Service User permission set is included in both Billing and Billing Advanced permission set licenses.

PERSONA	PERMISSION SET	PERMISSIONS
Billing Admin	Billing Admin	Assign permissions, configure billing policies, billing treatment, legal entities, sequential numbering, and manage default records.
Billing Operations User	Billing Operations User	Schedule invoice runs and manage invoice-related operations.
Billing Customer Service User	Billing Customer Service User	Generate invoices on demand for accounts and transactions, suspend and resume billing, resolve service requests for billing suspension, invoice due date extension, updating bill-to contact, and invoice charge correction.
Credit Memo Operations User	Credit Memo Operations User	Create, edit, and monitor credit memos.
Tax Admin	Tax Admin	Configure the tax engine, establish tax policies, and define tax treatment for billing.
Accounts Receivables Admin	Accounts Receivables Admin	Set up accounting periods and legal entities accounting periods, close legal entities accounting periods and accounting periods, and manage general ledger accounts and general ledger account assignment rules.
Billing Collections and Recovery Specialist	Billing Collections and Recovery Specialist	Create collection plans and collection plan items for unpaid or partially paid invoices. Collect payment promises for the collection plan items and create payment schedule and payment schedule items.
Payment Admin	Payment Admin	Set up payment merchant accounts through supported native and third-party payment gateways and create saved payment methods. Automatically create payment schedules and payment schedule items based on default payment schedule policy, payment schedule treatment, payment schedule treatment detail, and payment schedule distribution method. Retry failed payments, and apply credits and payments to settle the balances of invoices or invoice lines. Generate Pay Now payment links to associate payments with business accounts.
Payment Operations User	Payment Operations User	Manually create and manage payment schedules and payment schedule items. Schedule payment batch runs to process payment schedule items for collecting and applying payments to invoices.
Billing Experience Cloud User	Billing Experience Cloud User	View and download invoices, and select a payment method or add a saved payment method for making payments on outstanding invoice balances. Raise service requests related to billing inquiries or invoice-related disputes.
Billing Permission Sets by API

Assign the API permission sets individually to users based on their role. You can also combine them with persona-based permission sets by creating permission set groups.

API NAME	PERMISSION SET	PERMISSIONS
Create Billing Schedules for Orders API	Create Billing Schedules From Billing Transactions API and Context Service Runtime	Create billing schedules by passing a list of order IDs.
Generate Invoices From Billing Schedule API	Generate Invoices From Billing Schedule API	Generate invoices on demand by using the billing schedules.
Tax Calculation API	CalculateTaxes API	Calculate the tax for a transaction.
Invoice Run Recovery API	Manage Errors Using Invoice Error Recovery API	Detect and correct invoicing errors, automate error resolution, and provide tools for manual overrides and detailed diagnostics.
Void a Posted Invoice API	Void a Posted Invoice API	Void posted invoices if there are errors.
SEE ALSO
View and Manage Users
Create or Clone Profiles
Manage Permission Set Assignments
