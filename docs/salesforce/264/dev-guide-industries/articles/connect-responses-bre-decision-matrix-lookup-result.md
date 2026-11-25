---
page_id: connect-responses-bre-decision-matrix-lookup-result
title: Decision Matrix Lookup Result
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-bre-decision-matrix-lookup-result.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-responses
legacy_page_id: connect_responses_bre_decision_matrix_lookup_result.htm
fetched_at: 2026-11-25
---

# Decision Matrix Lookup Result

Output representation of the individual output of a decision matrix version lookup.

## JSON Example

```
{
  "outputs": [
    {
      "results": [],
      "error": "Input Data is Missing"
    },
    {
      "results": [
        {
          "name": "premium",
          "value": "2400"
        },
        {
          "name": "tax",
          "value": "300"
        }
      ]
    },
    {
      "results": [],
      "error": "There is no output for the given input data"
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `outputs` | [Decision Matrix Lookup Basic Result](./connect-responses-decision-matrix-lookup-basic-result.md)[] | List of outputs returned by a decision matrix. An output may contain multiple variables. | Small, 55.0 | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-bre-decision-matrix-lookup-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
