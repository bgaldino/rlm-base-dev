---
page_id: dynamic_revenue_orchestrator_flow_metadata_api.htm
title: Flow for Dynamic Revenue Orchestrator
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Dynamic Revenue Orchestrator

Represents the metadata associated with a flow. With Flow, you can create an
application that navigates users through a series of screens to query and update records in the
database. You can also execute logic and provide branching capability based on user input to
build dynamic applications.

## FlowActionCall

Dynamic Revenue Orchestrator exposes additional actionType values for the FlowActionCall
Metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values only for Dynamic Revenue Orchestrator include:   - `decomposeSalesTransaction`—Decompose a sales transaction, such as a quote, order, or   order summary. - `freezeSalesTransaction`—Freeze a sales transaction to disable the modification of a line   item. - `getPointOfNoReturn`—Get details about the point of no return milestone for each line   item in a sales transaction. - `orchestrateSalesTransaction`—Initiate the orchestration process for a sales   transaction. - `orchestrateTransaction`—Orchestrate a transaction for any   domain-specific object, such as a collection plan for Revenue billing, that requires the   composition and execution of a fulfillment plan. - `submitOrder`—Submit an order to Dynamic Revenue Orchestrator (DRO) for   fulfillment. - `submitSalesTransaction`—Initiate the fulfillment process of any sales transaction, such as a   quote, an order, or an order summary. - `unfreezeSalesTransaction`—Unfreeze a sales transaction to enable the modification of a line   item. |
