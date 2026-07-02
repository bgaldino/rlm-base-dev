---
page_id: lookup_tables_flow_metadata_api.htm
title: Flow for Lookup Tables
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/lookup_tables_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# Flow for Lookup Tables

Represents the metadata associated with a flow. With Flow, you can create an
application that navigates users through a series of screens to query and update records in the
database. You can also execute logic and provide branching capability based on user input to
build dynamic applications.

## FlowActionCall

Business Rules Engine exposes additional actionType values for the FlowActionCall Metadata
type. For more information on Flow and FlowActionCall metadata type, see [Flow](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_visual_workflow.htm).

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Lookup Tables include:  - `runDecisionMatrix`—Invoke a   decision matrix in a flow. This value is available in API version 55.0 and   later. |
