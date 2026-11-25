---
page_id: connect-resources-bre-search-lookup-tables
title: Lookup Tables (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-search-lookup-tables.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-table-resources
legacy_page_id: connect_resources_bre_search_lookup_tables.htm
fetched_at: 2026-11-25
---

# Lookup Tables (GET)

Retrieve lookup tables.

## Resource

```
/connect/business-rules/lookup-tables
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre&lookupTypes=DecisionTable,DecisionMatrix
```

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre
```

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre&lookupTypes=DecisionTable&businessKnowledgeModelName=ManualDiscount
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET

## Request Parameters for GET

- 
- 

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lookupTypes` | String | Type of lookup table. Valid values are: `DecisionMatrix``DecisionTable` | Optional | 59.0 |
| `searchKey` | String | The search text entered by the user to retrieve a list of lookup tables. | Required | 59.0 |
| `usageType` | String | Usage type of the lookup table. Valid value is `Bre`. The default value is `Bre`. When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Required | 59.0 |

## Response Body for GET

[Lookup Tables Result List](./connect-responses-lookup-tables-result-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-search-lookup-tables.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
