---
page_id: context_service_flow_metadata_api.htm
title: Flow for Context Service
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/context_service_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# Flow for Context Service

Represents the metadata associated with a flow. Use a flow to create an application
that takes users through a series of pages to query and update records in the database. You can
also execute logic and provide branching capability based on user input to build dynamic
applications.

## FlowActionCall

Context Service exposes additional actionType values for the FlowActionCall Metadata
type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid value only for Context Service include:   - `deleteContextCache`—Deletes the   context instance from the context cache using specified context ID. This value   is available in API version 64.0 and later. - `queryContextTags`—Queries context   instance tags associated with a context definition. This value is available in   API version 64.0 and later. - `updateContextAttributes`—Updates   attributes on the context instance using context tags. This value is available   in API version 64.0 and later. |
