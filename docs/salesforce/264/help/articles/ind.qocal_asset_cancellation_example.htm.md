---
article_id: ind.qocal_asset_cancellation_example.htm
title: Asset Cancellation Example
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_cancellation_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amendment_renewal_cancellation_scenarios.htm
fetched_at: 2026-11-23
---

# Asset Cancellation Example

Trace an asset cancellation to see how the asset is retired and billing stops.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To cancel assets:	

InitiateCancellation API permission set

AND

Sales Rep persona permissions

When you cancel a subscription, Revenue Cloud ends the asset's lifecycle, triggers de-provisioning, generates final billing credits, and moves the asset into a terminal state. This scenario traces an example of the full cancellation lifecycle.

Background

Cloud Kicks has decided to discontinue its Cloud Storage Pro subscription. The account currently holds this asset.

Product
Cloud Storage Pro (CLOUD001)
Quantity
1
Monthly recurring price
$50.00/month
Asset status
Active, lifecycle-managed
Current term
Several months remaining on a 12-month term
Billing
Paid through the current billing period

Because the asset is lifecycle-managed, Revenue Cloud tracks its full history on a single asset record with sequential Asset State Periods, from the original sale through any amendments, renewals, and eventual cancellation. This cancellation targets just the Cloud Storage Pro asset. Other assets on the account, such as the Laptop Pro Bundle, remain unaffected.

Business Scenario

Cloud Kicks has migrated to an internal storage solution and no longer needs the Cloud Storage Pro subscription. The account manager needs to cancel the service mid-term. Some key questions are:

Does the customer get a credit for the unused portion of the term?
Does the service stop immediately or at the end of the current billing period?
What happens to the data in the storage service?

The answers depend on the cancellation effective date and the fulfillment configuration. In this scenario, Cloud Kicks cancels effective immediately, not at the end of the term.

Initiate the Cancellation

The account manager goes to the Cloud Storage Pro asset on the Cloud Kicks account and clicks Cancel. The cancellation flow presents the effective date. The two options are:

Immediate cancellation
Effective today. Triggers mid-period proration.
End-of-term cancellation
Effective on the term end date. No proration is needed because the customer uses the full remaining term.

As requested by Cloud Kicks, the account manager selects immediate cancellation. Revenue Management creates a cancellation quote.

Product
Cloud Storage Pro
Quantity
-1 (a negative value is the key indicator of a cancellation)
Effective date
Today
Cancellation reason
Customer migrated to internal solution (optional field)
NOTE A cancellation order uses negative quantities. Where an amendment captures a delta (positive or negative), a cancellation captures the full quantity as negative to signal complete termination of the asset.
Create the Order

The account manager clicks Create Order from the cancellation quote. Revenue Cloud generates a cancellation order.

Order type
Cancellation
Order status
Draft
Line items
1 Cloud Storage Pro, quantity -1
Effective date
Today (mid-term)

The cancellation order captures the effective date from the quote, which determines when billing stops and when de-provisioning begins. When the account manager activates the order, Revenue Cloud triggers both downstream processes.

Order Decomposition

After the cancellation order is activated, Dynamic Revenue Orchestrator (DRO) processes it. Cancellation decomposition differs from new-sale and amendment decomposition. DRO reads the negative-quantity line items and, based on the decomposition rules configured for the cancel action, routes them through de-provisioning steps rather than provisioning steps.

The specific steps that run depend on your design-time decomposition configuration and the scenario rules defined for the cancel action on the order line items and fulfillment order line items. In this example, the configuration for Cloud Storage Pro defines these de-provisioning steps.

Service deactivation
An orchestration item that disables access to the storage service.
Data retention window
A timed step, set per the data retention policy, before permanent deletion.
Access revocation
Removal of user permissions for the storage endpoints.

These steps run in sequence. The service is deactivated immediately, but data retention policies can keep the underlying data available for a grace period.

If Cloud Kicks cancels a hardware product such as the Laptop Pro Bundle, the de-provisioning steps defined in your fulfillment configuration handle the physical return. Those steps can include return authorization, shipping labels, return tracking, and inventory restocking.

Fulfillment Outcome

The fulfillment purpose for a cancellation is de-provisioning. For Cloud Storage Pro:

Access is revoked. API endpoints stop responding. Users who attempt to access cloud storage receive an authorization error.
Data enters retention. Files are preserved for the configured retention period (typically 30 to 90 days, depending on policy) before permanent deletion.
Cloud Kicks has no physical goods to return.

The fulfillment outcome for a cancellation is the reverse of the original new-sale fulfillment. Whatever was provisioned gets de-provisioned. Whatever was shipped triggers a return.

Billing Outcome

Billing handles the financial close-out of the cancelled asset. During a cancellation, billing performs these tasks.

Creates a credit memo for the prorated unused portion of the current billing period.
Terminates the billing schedule. No future invoices are generated.
Issues a final invoice if any unbilled usage exists from the current period before the cancellation date.

For a mid-term cancellation, billing calculates a prorated credit. For example, with 6 months remaining at $50.00/month, the unused service is $300.00. If 10 days remain in the current billing period, the current-period proration adds a credit of (10/30) × $50.00, or $16.67. The total credit is the unused full months plus the current-period proration.

For end-of-term cancellations, no credit is issued. The customer has already paid for and used the full term. Billing simply stops generating invoices after the final period.

NOTE The credit calculation uses the cancellation effective date, not the order activation date. If the account manager creates the cancellation order on July 1 but sets the effective date to July 15, billing charges normally until July 15 and credits from July 15 forward.
Final Asset State

After DRO completes de-provisioning and billing processes the credit, the Cloud Storage Pro asset transitions to its terminal state.

Product
Cloud Storage Pro
Quantity
0
Asset status
Cancelled
Lifecycle end date
Cancellation effective date
Current monthly recurring revenue
$0.00

The Asset State Period (ASP) timeline shows the original state period, from the order date through the cancellation effective date (Active status), followed by the terminal state period, which begins on the cancellation effective date with a quantity of 0 (Cancelled status).

The asset record persists permanently. The Cancelled status and terminal ASP entry serve as the historical record that this service existed and was intentionally terminated. The Asset Actions related list shows the full history of changes to this asset, with each business category reflecting a distinct lifecycle event.

Troubleshooting
Billing doesn't issue a credit
Confirm that the cancellation effective date is before the term end date. End-of-term cancellations don't generate credits because no unused service exists.
Check whether the billing schedule was already terminated by another process, such as a payment failure suspension.
De-provisioning doesn't trigger
Review the decomposition configuration for cancellation orders. If no de-provisioning steps are mapped for this product, DRO marks the orchestration complete without action.
You need to reverse a cancellation
To restore service, the Revive Cancelled Asset feature creates a renewal-type order that reactivates the terminal asset. Alternatively, you can create a new-sale order for the same product.
SEE ALSO
Cancel Assets with the Managed Asset Viewer

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_asset_cancellation_example.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
