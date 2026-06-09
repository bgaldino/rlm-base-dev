---
page_id: qoc_flow_metadata_api.htm
title: Flow for Transaction Management
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/qoc_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Transaction Management

The flow for Transaction Management represents the metadata associated with a flow.
With Flow, you can create an application that takes users through a series of pages to query and
update the records in the database. You can also run logic and provide branching capability
based on user input to build dynamic applications.

## FlowActionCall

Transaction Management exposes additional actionType
values for the FlowActionCall metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values for Transaction Management are:   - `createContract`—Create a contract from a specific quote record. - `createOrderFromQuote`—Create an order from a quote record. - `createServiceDocument`—Create   service documents from work orders, work order line items, or service   appointments. - `deepCloneSalesTransaction`—Clone a quote or an order, including full object graph with related   objects, selected lines, or selected groups. Added in API version 67.0 and later. - `getRenewableAssetsSummary`—Retrieve details about renewable assets in a given order. You can   use this information to create renewal opportunities. Added in API version 64.0 and later. - `createOrUpdateAssetFromOrder`—Create an asset for each order item in the specified order. New   assets are created for a new order. Modify existing assets for change order requests,   such as a renewal or a cancellation. - `createOrUpdateAssetFromOrderItem`—Create assets from individual order items within an order. Track   assets after the individual line items of an order reach a certain stage in their   lifecycle, such as submitted, fulfilled, or provisioned. If the order item is part of a   renewal, an amendment, or a cancellation, existing assets are changed. - `initiateAmendment`—Initiate and execute the amendment of an asset. - `initiateRenewal`—Initiate and execute the renewal of an asset. - `initiateCancellation`—Initiate and execute the cancellation of an asset. - `initiateRollBackLastAction`—Initiate the reversal of the last action on an asset to rectify any   transactional errors or to meet changing business requirements. - `createOrdersFromQuote`—Create multiple orders from a single quote instead of a single   order, ensuring easier order management and fulfillment operations. - `initiateTransfer`—Transfer an asset or multiple assets from one account to   another. |

/
