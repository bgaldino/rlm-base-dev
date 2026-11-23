---
page_id: connect_resources_clause_category_configurations.htm
title: Clause Category List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_clause_category_configurations.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clause_library_resources.htm
fetched_at: 2026-11-23
---

# Clause Category List

Access list of clause categories from the configuration.

## Resource

```
/connect/clause-library/clause-category-configurations
```

## Example URI

```
https://YOUR_INSTANCE.salesforce.com/services/data/68.0/connect/clause-library/clause-category-configurations
```

## Available Version

57.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `name` | String | The name of the clause category. | Required | 57.0 |
| `usageType` | String | The usage type for the clause category. Valid values are `Contract Clause Category`  or `Disclosure Category`. | Required | 57.0 |

## Response Body for GET

[Clause Library Category Response](./connect_responses_clause_categories_respons.htm.md "Output representation of the request to retrieve the clause library category configuration.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_clause_category_configurations.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
