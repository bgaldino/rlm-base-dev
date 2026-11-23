---
page_id: connect_responses_lookup_table_details.htm
title: Lookup Table Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_lookup_table_details.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-11-23
---

# Lookup Table Details

Output representation of the basic details of a lookup
table.

## JSON Example

```
  "lookupTables":[{
    "apiName":"DM_1",
    "id":"0lIxx0000000001EAA",
    "lookupTableDefinitionId":"9QNxx0000004C92GAE",
    "lookupTableType":"DecisionMatrix",
    "name":"DM_1"
  },
  {
    "apiName":"DT_2",
    "id":"0lIxx000000003FEAQ",
    "lookupTableDefinitionId":"0lDxx000000001dEAA",
    "lookupTableType":"DecisionTable",
    "name":"DT_2"
  }]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `apiName` | String | Unique developer name of the Decision Table or Decision Matrix. | Small, 59.0 | 59.0 |
| `id` | String | ID of the lookup table record. | Small, 59.0 | 59.0 |
| `lookupTable​DefinitionId` | String | ID of the Decision Table or Decision Matrix record. | Small, 59.0 | 59.0 |
| `lookupTable​Type` | String | Type of the lookup table, such as Decision Table or Decision Matrix. | Small, 59.0 | 59.0 |
| `name` | String | Name of the Decision Table or Decision Matrix. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_lookup_table_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
