---
article_id: ind.billing_schedules_standalone_api.htm
title: Generate Billing Schedules from External Transactions or Salesforce Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedules_standalone_api.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_and_schedule_groups.htm
fetched_at: 2026-11-23
---

# Generate Billing Schedules from External Transactions or Salesforce Objects

Use the Create Standalone Billing Schedules API to generate billing schedules directly from transactions in external systems, or from any Salesforce object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
The Create Standalone Billing Schedules API is available with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To generate billing schedules for usage-based charge types:	

Product Catalog Management Viewer permission set

OR

Usage Management Runtime permission set

Generate billing schedules on-demand and eliminate the need for importing or replicating complex data by using the Create Standalone Billing Schedules API. The API supports various transaction types, including original, amended, canceled, renewed, ramped, bundled, or usage-based transactions.

To automate this process for external transactions or Salesforce objects, design a custom flow and add the Create Standalone Billing Schedules action.

Starting Summer ‘26, you can use the enhanced Create Standalone Billing Schedules API to pass minimal, intent-based requests for amendments, renewals, cancellations, and any changes to price, quantity, or end dates. Billing automatically computes the required fields such as unit price and total price by using historical transaction context or Billing Schedule Group IDs.

IMPORTANT When a billing schedule group is linked to an asset, initiate any new sale, amend, renew, or cancel actions directly from the order or asset. In such cases, use the Order to Billing Schedule flow or Create Billing Schedules for Orders API, and not the Create Standalone Billing Schedules API.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_schedules_standalone_api.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
