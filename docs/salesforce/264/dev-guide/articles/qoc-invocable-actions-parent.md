---
page_id: qoc-invocable-actions-parent
title: Transaction Management Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-invocable-actions-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-overview
legacy_page_id: qoc_invocable_actions_parent.htm
fetched_at: 2026-11-25
---

# Transaction Management Standard Invocable Actions

Learn more about the standard invocable actions available with Transaction Management.

- 

**[Create Contract Action](./actions-obj-create-contract-from-quote.md)**

Create a contract from a specific quote record.

- 

**[Create or Update Asset From Order Action](./actions-obj-create-update-asset-from-order.md)**

Create an asset for each order item in the specified order. New assets are created for a new order. Modify existing assets for change order requests, such as a renewal or a cancellation.

- 

**[Create or Update Asset From Order Item Action](./actions-obj-create-update-asset-from-order-item.md)**

Create assets from individual order items within an order. Track assets after the individual line items of an order reach a certain stage in their lifecycle, such as submitted, fulfilled, or provisioned. If the order item is part of a renewal, an amendment, or a cancellation, existing assets are changed.

- 

**[Create Order From Quote Action](./actions-obj-create-order-from-quote.md)**

Create a draft order from a quote record.

- 

**[Create Orders From Quote Action](./actions-obj-create-orders-from-quote.md)**

Create multiple orders from a single quote instead of a single order, ensuring easier order management and fulfillment operations.

- 

**[Deep Clone Sales Transaction](./actions-obj-deep-clone-sales-transaction.md)**

Clone a quote or an order, including full object graph with related objects, selected lines, or selected groups.

- 

**[Get Renewable Assets Summary Action](./actions-obj-get-renewable-assets-summary.md)**

Retrieve details about renewable assets in a given order. You can use this information to create renewal opportunities.

- 

**[Initiate Amendment Action](./actions-obj-amend-assets.md)**

Initiate and execute the amendment of an asset.

- 

**[Initiate Cancellation Action](./actions-obj-cancel-assets.md)**

Initiate and execute the cancellation of an asset.

- 

**[Initiate Renewal Action](./actions-obj-renew-assets.md)**

Initiate and execute the renewal of an asset.

- 

**[Initiate Rollback on Last Action](./actions-obj-initiate-rollback-last-action.md)**

Initiate the reversal of the last action on an asset to rectify any transactional errors or to meet changing business requirements.

- 

**[Initiate Transfer Action](./actions-obj-initiate-transfer.md)**

Transfer an asset or multiple assets from one account to another.

- 

**[Sync Quote to Opportunity Action](./actions-obj-sync-quote-opportunity.md)**

Sync quote line items to the matching opportunity line items so that forecasts stay up to date.

**See Also**

- [*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_intro_overview.htm)

- [*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_actions_invocable_standard.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-invocable-actions-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
