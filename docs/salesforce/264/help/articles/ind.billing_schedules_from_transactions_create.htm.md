---
article_id: ind.billing_schedules_from_transactions_create.htm
title: Generate Billing Schedules from Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedules_from_transactions_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_from_orders.htm
fetched_at: 2026-11-23
---

# Generate Billing Schedules from Orders

Generate billing schedules from orders by using a flow or an API. To automatically trigger the generation of billing schedules when the order is activated, use the Order to Billing Schedule flow. To generate billing schedules for orders by using API, use Create Billing Schedules for Orders API or Create Standalone Billing Schedules API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
The Order To Billing Schedule flow template and Create Billing Schedules for Orders API are available with the Revenue Cloud Advanced license or the Revenue Cloud Billing license.
USER PERMISSIONS
NEEDED
To use Order To Billing Schedule flow template:	

Billing Admin permission set

AND

Billing Operations User permission set


To use Create Billing Schedules for Orders API:	

Create Billing Schedules From Billing Transactions API permission

AND

Context Service Runtime permission set


To generate billing schedules for usage-based charge types:	

Product Catalog Management Viewer permission set

OR

Usage Management Runtime permission set

IMPORTANT

Use the Order to Billing Schedules API and Order to Billing Schedules flow for any new sale, amendments, renewals, or cancellations that originate from Revenue Cloud orders and assets.

Use Order to Billing Schedule Flow

Use the Order to Billing Schedule flow to automatically generate billing schedules and billing schedule groups from order items as soon as orders are activated.

Save a version of the out-of-the-box Order to Billing Schedule flow and activate it. When you clone the flow, we recommend that you include Custom in the name to distinguish it from out-of-the-box flows.

When an order is activated, two flows—Order to Asset and Order to Billing Schedule—are triggered. The Order to Billing Schedule flow then generates a billing schedule group and a billing schedule for the order.

NOTE As a best practice, we recommend that you use only one active flow to generate billing schedules. If there are multiple active flows, duplicate billing schedules get generated for the same order.
NOTE To generate billing schedules with correct addresses after State and Country/Territory Picklists are enabled, edit legal entities that already have an address. Select the country and state from the picklists, and then save. See Create Legal Entities.
Use Create Billing Schedules for Orders API

Use Create Billing Schedules for Orders API to generate billing schedules from orders.

Before using Create Billing Schedules for Orders API, select the context definition and the context mapping from the Billing settings page or create a custom procedure plan definition.

Create a custom procedure plan definition with these values.
Select Billing as the process type.
Select the object that you want to generate billing schedules for as the primary object.
Select the context definition extended from BillingContext as the context definition.
Update and activate the procedure plan definition.
Open the procedure plan definition and select a read context mapping for the primary object.
Activate the procedure plan definition.
To create billing schedules from orders, use Create Billing Schedules for Orders API.

To automate this process for external transactions or Salesforce objects, design a custom flow and add the Create Billing Schedules From Billing Transaction action.

Generate invoices from these billing schedules by scheduling invoice runs, from the Order record pages, or by using an API.

Use Create Standalone Billing Schedules API

For one-time, termed, and evergreen products, use Create Standalone Billing Schedules API to generate billing schedules from orders and order items.

In the request body of Create Standalone Billing Schedules API, specify the BillingContext standard context definition as the contextDefinitionName property value.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_schedules_from_transactions_create.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
