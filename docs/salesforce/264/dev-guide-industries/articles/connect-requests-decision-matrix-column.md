---
page_id: connect-requests-decision-matrix-column
title: Decision Matrix Column Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-column.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-requests-1
legacy_page_id: connect_requests_decision_matrix_column.htm
fetched_at: 2026-11-25
---

# Decision Matrix Column Input

Input representation of the information required to add, update, or delete columns in a decision matrix.

## Properties

- 
- 

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | The type of action you want to perform on a column. Possible values are: `delete``update` | Required Note: Leave this field blank if you’re adding a column in a decision matrix. | 53.0 |
| `apiName` | String | The API name of a column. | Optional | 53.0 |
| `columnType` | String | The type of a column. Possible values are: `Input``Output` | Required | 53.0 |
| `dataType` | String | The data type of a column. | Optional | 53.0 |
| `displaySequence` | Integer | The display sequence of a column. | Optional | 53.0 |
| `id` | String | The ID of the column record to be updated or deleted. | Required Note: Leave this field blank if you’re adding a column in a decision matrix. | 53.0 |
| `name` | String | The name of a column. | Required | 53.0 |
| `rangeValues` | String | The range values of a column. The range columns contain a sorted list of comma-separated values, which are updated whenever a row is added to the Decision Matrix Version. | Optional | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-column.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
