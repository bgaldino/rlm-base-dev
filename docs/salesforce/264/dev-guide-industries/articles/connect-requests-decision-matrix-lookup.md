---
page_id: connect-requests-decision-matrix-lookup
title: Decision Matrix Lookup Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-lookup.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-requests
legacy_page_id: connect_requests_decision_matrix_lookup.htm
fetched_at: 2026-11-25
---

# Decision Matrix Lookup Input

Input representation of the input for a decision matrix lookup.

## JSON Example

```
{
  "inputs": [
    {
      "input": [
        {
          "name": "Premium",
          "value": "2400"
        }
      ]
    },
    {
      "input": [
        {
          "name": "Tenure",
          "value": "10"
        }
      ]
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | [Decision Matrix Input](./connect-requests-decision-matrix-input.md) | List of inputs passed to a decision matrix. An input may contain multiple variables. | Required | 55.0 |
| `options` | [Decision Matrix Options Input](./connect-requests-decision-matrix-options.md) | The lookup options for a decision matrix. | Optional | 55.0 |

Here, `Premium` and `Tenure` are column headers in the matrix, and `2400` and `10` are values of a cell in the column.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-lookup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
