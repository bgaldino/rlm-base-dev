---
page_id: connect-requests-context-attr-hydration-details-input
title: Context Attribute Hydration Details Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-attr-hydration-details-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_attr_hydration_details_input.htm
fetched_at: 2026-11-25
---

# Context Attribute Hydration Details Input

Input representation of context attribute hydration detail.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `childDetails` | Context Attribute Hydration Details Input[] | Child of hydration details. | Required | 59.0 |
| `contextAttrHydrationDetailId` | String | ID of the hydration detail record. This field is required for the update request. | Optional | 59.0 |
| `parentAttributeMappingId` | String | ID of the parent context attribute mapping record. | Required | 59.0 |
| `parentDetailId` | String | ID of the parent context attribute hydration detail record. | Required | 59.0 |
| `queryAttribute` | String | Query attribute. | Optional | 59.0 |
| `sObjectDomain` | String | SObject domain. | Optional | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-attr-hydration-details-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
