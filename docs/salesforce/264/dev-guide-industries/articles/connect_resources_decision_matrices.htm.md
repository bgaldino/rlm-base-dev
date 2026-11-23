---
page_id: connect_resources_decision_matrices.htm
title: Decision Matrices
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrices.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-11-23
---

# Decision Matrices

Get a list of decision matrices ( also known as calculation matrix)
based on a search text. The API returns a maximum of ten decision matrices records that
contain the specified keyword.

## Resource

```
/connect/omnistudio/decision-matrices
```

## Example URI

```
/services/data/v53.0/connect/omnistudio/decision-matrices?searchKey=Test
```

## Available Version

53.0

## Requires Chatter

No

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `searchKey` | String | The user-entered search text to retrieve a list of decision matrices. |  | 53.0 |

## Response Body for GET

[Decision Matrix Result List](./connect_responses_decision_matrix_result_list.htm.md "Output representation of the decision matrix result list.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrices.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
