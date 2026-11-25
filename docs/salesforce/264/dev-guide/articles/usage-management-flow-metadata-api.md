---
page_id: usage-management-flow-metadata-api
title: Flow for Usage Management
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-flow-metadata-api.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-metadata-api-parent
legacy_page_id: usage_management_flow_metadata_api.htm
fetched_at: 2026-11-25
---

# Flow for Usage Management

Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Usage Management exposes additional actionType values for the FlowActionCall Metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| `actionType` | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Usage Management include `invokeSummaryCreationService`—Invoke the service that creates various summaries, such as usage, ratable, and liable summaries where the usage amount is zero. The service also checks and updates the billing period of the usage entitlement account if the billing period is expired; `processConsumptionOverages`—Process consumption overages for the usage summary records with `SummaryComplete` status. This action uses the entitlement service to process the overages; `refreshUsageEntitlementBucket`—Refresh entitlements by evaluating the usage entitlement bucket records and creating a new usage entitlement entry; or `retriggerEntlCreaProc`—Retrigger entitlement creation process for failed or unprocessed assets. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-flow-metadata-api.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
