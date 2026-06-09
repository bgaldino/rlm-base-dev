---
page_id: billing_overview.htm
title: Billing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_overview.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
fetched_at: 2026-06-09
---

# Billing

Automate processes related to billing, credit application, and invoice generation.
Generate billing schedules by using context service, and create invoices from a billing
schedule.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Unlimited**, and **Developer** Editions |

- **[Billing Standard Objects](./billing_std_objects_parent.htm.md)**  
  The Billing data model provides objects and fields to manage billing and tax configurations, credit memos, and invoices, and accounting periods for legal entities.
- **[Billing Fields on Standard Objects](./billing_extended_standard_object_fields.htm.md)**  
  Billing adds standard fields to some standard Salesforce objects of other features to represent information specific to Billing. These fields are available only in orgs where Billing is enabled.
- **[Salesforce Payments Objects in Billing](./billing_payments_objects.htm.md)**  
  Billing provides access to some standard Salesforce Payments objects that you can use to authorize payments, connect to an external payment gateway, group all the payment transactions that are processed for a particular transaction, and store payment methods. You can access these objects with the Revenue Cloud Billing license.
- **[Billing Platform Events](./billing_pfrm_evnt_parent.htm.md)**  
  Salesforce publishes standard platform events in response to an action that occurred in the org or to report errors. For example, the InvoiceProcessedEvent platform event sends notification to the customer when the billing invoice activity is complete. You can subscribe to a standard platform event by using the subscription mechanism that the event supports.
- **[Billing Standard Invocable Actions](./billing_invocable_actions_parent.htm.md)**  
  Use standard invocable actions to automate processes such as credit application, billing schedules creation, and invoice management.
- **[Billing Business APIs](./billing_business_api_overview.htm.md)**  
  Use the Billing Business APIs to manage credit application and to handle billing scenarios.
- **[Billing Apex Reference](./billing_apex_reference.htm.md)**  
  Billing provides the `ConnectApi` namespace (also called Connect in Apex) that contains classes for accessing the same capabilities that are available in the Billing Business APIs. Additionally, you can use other built-in Apex classes and interfaces grouped by namespace.
- **[Billing Metadata API Types](./billing_metadata_api_parent.htm.md)**  
  Metadata API enables you to access some types and feature settings that you can customize in the user interface.

#### See Also

- [*Salesforce Help*: Assign Permissions to Access Billing Features](https://help.salesforce.com/s/articleView?id=ind.billing_permission_sets.htm&type=5&language=en_US "Salesforce Help: Assign Permissions to Access Billing Features - HTML (New Window)")
