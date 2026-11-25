---
page_id: billing-overview
title: Billing
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-overview.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
legacy_page_id: billing_overview.htm
fetched_at: 2026-11-25
---

# Billing

Automate processes related to billing, credit application, and invoice generation. Generate billing schedules by using context service, and create invoices from a billing schedule.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Unlimited**, and **Developer** Editions |

- 

**[Billing Standard Objects](./billing-std-objects-parent.md)**

The Billing data model provides objects and fields to manage billing and tax configurations, credit memos, and invoices, and accounting periods for legal entities.

- 

**[Billing Fields on Standard Objects](./billing-extended-standard-object-fields.md)**

Billing adds standard fields to some standard Salesforce objects of other features to represent information specific to Billing. These fields are available only in orgs where Billing is enabled.

- 

**[Salesforce Payments Objects in Billing](./billing-payments-objects.md)**

Billing provides access to some standard Salesforce Payments objects that you can use to authorize payments, connect to an external payment gateway, group all the payment transactions that are processed for a particular transaction, and store payment methods. You can access these objects with the Revenue Cloud Billing license.

- 

**[Billing Platform Events](./billing-pfrm-evnt-parent.md)**

Salesforce publishes standard platform events in response to an action that occurred in the org or to report errors. For example, the InvoiceProcessedEvent platform event sends notification to the customer when the billing invoice activity is complete. You can subscribe to a standard platform event by using the subscription mechanism that the event supports.

- 

**[Billing Standard Invocable Actions](./billing-invocable-actions-parent.md)**

Use standard invocable actions to automate processes such as credit application, billing schedules creation, and invoice management.

- 

**[Billing Business APIs](./billing-business-api-overview.md)**

Use the Billing Business APIs to manage credit application and to handle billing scenarios.

- 

**[Billing Apex Reference](./billing-apex-reference.md)**

Billing provides the `ConnectApi` namespace (also called Connect in Apex) that contains classes for accessing the same capabilities that are available in the Billing Business APIs. Additionally, you can use other built-in Apex classes and interfaces grouped by namespace.

- 

**[Billing Metadata API Types](./billing-metadata-api-parent.md)**

Metadata API enables you to access some types and feature settings that you can customize in the user interface.

**See Also**

- [*Salesforce Help*: Assign Permissions to Access Billing Features](https://help.salesforce.com/s/articleView?id=ind.billing_permission_sets.htm&type=5)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
