---
page_id: connect_responses_clause_categories_respons.htm
title: Clause Library Category Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_clause_categories_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Clause Library Category Response

Output representation of the request to retrieve the clause library
category configuration.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `clauseCategories` | [Clause Category Response[]](./connect_responses_clause_category_respons.htm.md "Output representation of the field-level details for a clause category.") | The list of clause category configurations. | Small, 57.0 | 57.0 |

## JSON Example

```
{
  "clauseCategories": [
    {
      "id": "0zMRO000000001s", //not a required response field
      "name": "Confidential",
      "usageType": "Contract Clause Category"
    },
    {
      "name": "Environment",
      "usageType": "Disclosure Category"
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_clause_categories_respons.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
