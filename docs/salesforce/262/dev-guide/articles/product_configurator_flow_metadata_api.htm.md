---
page_id: product_configurator_flow_metadata_api.htm
title: Flow for Product Configurator
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_configurator_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Product Configurator

Represents the metadata associated with a flow. With Flow, you can create an
application that navigates users through a series of screens to query and update records in the
database. You can also execute logic and provide branching capability based on user input to
build dynamic applications.

## FlowActionCall

Product Configurator exposes additional actionType values for the FlowActionCall Metadata
type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values only for Product Configurator include:   - `runConfigRules`—Run rules for a specific quote or order based on a context ID or   transaction ID, and process other steps that are part of the configuration directly   within a Flow. This action decouples rule execution from configurations to enable   independent execution of rules and for easier retrieval of responses. |
