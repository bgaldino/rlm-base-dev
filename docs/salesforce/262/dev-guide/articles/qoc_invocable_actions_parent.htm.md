---
page_id: qoc_invocable_actions_parent.htm
title: Transaction Management Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/qoc_invocable_actions_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_overview.htm
fetched_at: 2026-06-09
---

# Transaction Management Standard Invocable Actions

Learn more about the standard invocable actions available with Transaction
Management.

- **[Create Contract Action](./actions_obj_create_contract_from_quote.htm.md)**  
  Create a contract from a specific quote record.
- **[Create or Update Asset From Order Action](./actions_obj_create_update_asset_from_order.htm.md)**  
  Create an asset for each order item in the specified order. New assets are created for a new order. Modify existing assets for change order requests, such as a renewal or a cancellation.
- **[Create or Update Asset From Order Item Action](./actions_obj_create_update_asset_from_order_item.htm.md)**  
  Create assets from individual order items within an order. Track assets after the individual line items of an order reach a certain stage in their lifecycle, such as submitted, fulfilled, or provisioned. If the order item is part of a renewal, an amendment, or a cancellation, existing assets are changed.
- **[Create Order From Quote Action](./actions_obj_create_order_from_quote.htm.md)**  
  Create an order from a quote record.
- **[Create Orders From Quote Action](./actions_obj_create_orders_from_quote.htm.md)**  
  Create multiple orders from a single quote instead of a single order, ensuring easier order management and fulfillment operations.
- **[Deep Clone Sales Transaction](./actions_obj_deep_clone_sales_transaction.htm.md)**  
  Clone a quote or an order, including full object graph with related objects, selected lines, or selected groups.
- **[Get Renewable Assets Summary Action](./actions_obj_get_renewable_assets_summary.htm.md)**  
  Retrieve details about renewable assets in a given order. You can use this information to create renewal opportunities.
- **[Initiate Amendment Action](./actions_obj_amend_assets.htm.md)**  
  Initiate and execute the amendment of an asset.
- **[Initiate Cancellation Action](./actions_obj_cancel_assets.htm.md)**  
  Initiate and execute the cancellation of an asset.
- **[Initiate Renewal Action](./actions_obj_renew_assets.htm.md)**  
  Initiate and execute the renewal of an asset.
- **[Initiate Rollback on Last Action](./actions_obj_initiate_rollback_last_action.htm.md)**  
  Initiate the reversal of the last action on an asset to rectify any transactional errors or to meet changing business requirements.
- **[Initiate Transfer Action](./actions_obj_initiate_transfer.htm.md)**  
  Transfer an asset or multiple assets from one account to another.

#### See Also

- [*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_intro_overview.htm "Actions Developer Guide: Overview - HTML (New Window)")
- [*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/resources_actions_invocable_standard.htm "REST API Developer Guide: Invocable Actions Standard - HTML (New Window)")
