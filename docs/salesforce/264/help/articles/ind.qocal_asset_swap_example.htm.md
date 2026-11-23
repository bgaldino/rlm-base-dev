---
article_id: ind.qocal_asset_swap_example.htm
title: Asset Swap Example
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_swap_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amendment_renewal_cancellation_scenarios.htm
fetched_at: 2026-11-23
---

# Asset Swap Example

Trace a product swap to see how Revenue Cloud replaces one lifecycle-managed asset with another and orchestrates both sides of the change.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To swap assets:	

InitiateAmendment API permission set

AND

Sales Rep persona permissions

What Happens During a Swap

A swap replaces one product with another on a customer account in a single commercial transaction. On the swap order, the outgoing product's action uses the Subtype SwapOut and the incoming product's action uses SwapIn.

This scenario traces the full swap lifecycle: the starting asset, the swap order and its two order actions, how Dynamic Revenue Orchestrator (DRO) decomposes and orchestrates the swap across two fulfillment lanes, the net billing impact, and the final state of both assets.

Scenario 1: Downgrade Hardware with a Swap

An Acme field engineer recently joined the company and needs a computer. However, the ordering manager didn't realize the engineer needed a travel-ready laptop, and the desktop was shipped in error.

Instead of canceling the desktop and placing a new order for a laptop, the account manager swaps the desktop for a laptop in one transaction. Keeping it as a single swap preserves the link between the retired and new products for auditing, and billing nets the credit and the charge together.

Starting asset (swap out):

Product
ARC Desktop Pro
Quantity
1
Price
US$2,400

Target product (swap in):

Product
ARC Laptop Pro
Quantity
1
Price
$1,600

The laptop costs less than the desktop, so this swap is a downgrade that nets a credit to the customer.

NOTE The Total Lifecycle Amount column shows the asset's value. The Current Amount and MRR columns read $0 because these are one-time hardware products with no recurring charge. That's expected, not an error.
Initiate the Swap

From the Acme account's Managed Assets, the account manager selects the ARC Desktop Pro asset, opens the action menu, and selects Swap. In the swap flow, the account manager sets the ARC Laptop Pro as the incoming product. To initiate a swap from the asset record, see Swap, Upgrade, or Downgrade Assets.

Revenue Cloud recognizes the transaction as a swap. On the same quote, the outgoing product has a negative quantity and the incoming product has a positive quantity, and the two are linked by the Swaps business category.

Create the Order

The account manager clicks Create Order from the swap quote. Revenue Cloud generates a single order that carries both sides of the swap as two order actions.

PRODUCT	QUANTITY	ORDER ACTION	SUBTYPE	AMOUNT
ARC Desktop Pro	−1	Amend	SwapOut	−$2,400
ARC Laptop Pro	+1	Add	SwapIn	+$1,600

The swap isn't a distinct Swap order action type. Revenue Cloud models it as an Amend action for the outgoing product and an Add action for the incoming product. Each action carries a swap Subtype (SwapOut or SwapIn). The order's total net amount is −$800, a credit to the customer.

The account manager activates the order.

Order Decomposition

When the activated swap order is submitted, DRO orchestrates the swap. In the order's Decomposition Details tab, the Fulfillment Plan shows Completed and the Order Product panel lists both order actions.

DRO routes each order action to a fulfillment lane:

The SwapIn routes to the provisioning lane, which runs the steps that provision the new product, such as allocation, configuration, and shipping.
The SwapOut routes to the de-provisioning lane, which runs the steps that retire the old product, such as return authorization, hardware return, and restock.

The orchestration plan shows both lanes completed. This dual-lane result is the heart of the swap: one path provisions the new product and the other de-provisions the old one. To see the plan details, click View Orchestration Plan in the Decomposition Details tab of the order.

NOTE The specific steps in each lane depend on your org's DRO configuration. The de-provisioning lane fires for the SwapOut only if you configure a fulfillment scenario for the SwapOut's order action. The SwapOut is an Amend action, so you need a fulfillment scenario that maps the outgoing product plus the Amend action to your de-provisioning lane. Without that scenario, only the provisioning lane runs. The outgoing asset is still retired by assetization, but DRO generates no de-provisioning steps such as return or restock.
Billing Outcome

Both sides of the swap are on the same order, so billing nets them:

SwapOut credit: −$2,400 for the returned ARC Desktop Pro
SwapIn charge: +$1,600 for the ARC Laptop Pro
Net: −$800 credit to the customer

Both products are one-time transactions, not subscriptions, so there's no proration and no recurring schedule change. Billing nets the one-time credit and charge into a single net amount.

For an upgrade, the same netting applies, but the net is a charge instead of a credit.

Final Asset State After a Hardware Swap

After the swap order is fulfilled, two asset changes occur on the Acme account.

Outgoing asset, ARC Desktop Pro:

Current Quantity: 0 (retired)
The asset record persists for history. Its lifecycle-managed quantity drops to 0.

Incoming asset, ARC Laptop Pro:

A new asset record is created on the account.
Current Quantity: 1

The link between the SwapOut and SwapIn is preserved on the order, which gives a complete audit trail of what replaced what.

Troubleshoot a Swap
The old asset's quantity didn't drop to 0
Confirm the SwapOut line has a negative quantity. A swap with quantity 0 on the outgoing product doesn't retire the asset.
The de-provisioning lane didn't run
Add a fulfillment scenario that maps the outgoing product plus the Amend action to your de-provisioning lane. The SwapOut routes through the Amend action, so a scenario keyed only to Cancel doesn't fire.
The Decomposed Line Items panel is empty
That result is expected in this example fulfillment model. Check the orchestration plan for the fulfillment steps instead.
Billing didn't net the credit and charge
Confirm both line items are in the same order. Billing nets within an order, not across orders.
Scenario 2: Upgrade a Subscription to a Higher Tier

A subscription swap uses the same SwapOut and SwapIn order actions as a hardware swap, applied to a recurring product instead of one-time hardware. This variant swaps a monthly support subscription for a higher tier: Basic Support at $50/month is replaced by Signature Support at $150/month, mid-subscription.

Two things behave differently from the hardware swap:

The money is recurring. The swap changes the monthly recurring revenue (MRR), and billing prorates the partial month.
The asset state is time-aware. Each subscription tracks Asset State Periods with start and end dates, so the swap closes one period and opens another.
Scenario Setup

Acme has been using Basic Support for two months, but now needs a faster response-time SLA and a dedicated support contact. Basic Support doesn't include these features, so Acme upgrades to Signature Support.

The starting subscription details are:

Product
Basic Support
Selling model
Monthly (evergreen)
Quantity
1
Rate
$50/month
Asset State Period Start Date
July 28

The new subscription details are:

Product
Signature Support
Selling model
Monthly (evergreen)
Quantity
1
Rate
$150/month
Asset State Period Start Date
September 28
The Swap Order

The account manager swaps Basic Support for Signature Support from Managed Assets, and then clicks Create Order. As with the hardware swap, the order carries both sides as two order actions.

PRODUCT	QUANTITY	ORDER ACTION	SUBTYPE	MRR CHANGE
Basic Support	−1	Amend	SwapOut	−$50
Signature Support	+1	Add	SwapIn	+$150

There's no Upgrade order action, and no UpgradeFrom or UpgradeTo subtype. A subscription tier change driven from the asset Swap action uses the same Amend/SwapOut and Add/SwapIn pattern as any other swap. The upgrade is visible in the money, not in a special action type. The MRR steps from $50 to $150.

The account manager activates the order, and DRO orchestrates it across these two lanes: the SwapIn provisions Signature Support, and the SwapOut de-provisions Basic Support.

Recurring Billing and Proration

Unlike the one-time hardware swap, a subscription swap changes a recurring schedule:

Basic Support stops billing at $50/month as of the swap date.
Signature Support starts billing at $150/month as of the swap date.
Billing prorates the swap date's partial month so the customer isn't charged twice for the same days.

The net recurring change is +$100/month.

Time-Aware Asset State

Each asset tracks Asset State Periods that record what was true for a span of time. The swap closes the outgoing period and opens the incoming one at the same boundary.

ASSET	PERIOD START	PERIOD END	QUANTITY	MRR
Basic Support	July 28	September 27	1	$50
Basic Support	September 28	(open)	0	$0
Signature Support	September 28	(open)	1	$150

The Basic Support period runs from the original start date to the day before the swap, and then closes. The Signature Support period opens on the swap date with no gap and no overlap. Read together, the periods show the tier change as a clean transition on the timeline, with the recurring value stepping from $50 to $150 at the boundary.

Final Asset State After a Tier Upgrade
Basic Support: Current Quantity 0, MRR $0. The asset persists for history with a closed state period.
Signature Support: a new asset at Current Quantity 1, MRR $150.
Each asset carries an Asset Action in the Swaps category. Basic Support records a Change action with Subtype SwapOut and an MRR change of −$50. Signature Support records a Generate action with Subtype SwapIn and an MRR change of +$150.
SEE ALSO
Swap Assets
Backdate Asset Transactions

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_asset_swap_example.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
