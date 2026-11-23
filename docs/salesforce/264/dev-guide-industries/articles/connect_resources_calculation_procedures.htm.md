---
page_id: connect_resources_calculation_procedures.htm
title: Calculation Procedures
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedures.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-11-23
---

# Calculation Procedures

Get a list of expression sets (also known as calculation procedure)
based on a search text. The API returns a maximum of ten expression set records that contain
the specified keyword.

## Resource

```
/connect/omnistudio/evaluation-services
```

## Example URI

```
/services/data/v53.0/connect/omnistudio/evaluation-services?searchKey=Expression
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
| `searchKey` | String | The user-entered search text to retrieve a list of expression sets. | Required | 53.0 |

## Response Body for GET

[Calculation Procedure List Output](./connect_responses_calculation_procedure_list_output.htm.md "Output representation of the expression set result list.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedures.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
