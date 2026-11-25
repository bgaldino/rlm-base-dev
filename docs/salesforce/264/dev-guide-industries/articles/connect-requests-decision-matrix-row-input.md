---
page_id: connect-requests-decision-matrix-row-input
title: Decision Matrix Row Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-row-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-requests-1
legacy_page_id: connect_requests_decision_matrix_row_input.htm
fetched_at: 2026-11-25
---

# Decision Matrix Row Input

Input representation of the information required to add, update, or delete rows in a decision matrix version.

## Properties

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | Type of action you want to perform on a row. Possible values are: `delete``update` | Required Note: Leave this field blank if you’re adding a row in a decision matrix version. | 53.0 |
| `id` | String | The ID of the row record to be updated or deleted. | Required Note: Leave this field blank if you’re adding a row to a decision matrix version. | 53.0 |
| `name` | String | Name of the row. | Optional | 53.0 |
| `rowData` | Map<String, Object> | The key-value pair for the row. All column values are required for update and delete operations. | Required | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-row-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
