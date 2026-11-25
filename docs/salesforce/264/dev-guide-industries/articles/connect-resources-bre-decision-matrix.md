---
page_id: connect-resources-bre-decision-matrix
title: Decision Matrix Lookup (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-decision-matrix.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-table-resources
legacy_page_id: connect_resources_bre_decision_matrix.htm
fetched_at: 2026-11-25
---

# Decision Matrix Lookup (POST)

Performs a lookup on decision matrix rows based on the input values provided, and returns the row’s output.

## Resource

```
/connect/business-rules/decision-matrices/${matrixName}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/vXX.X/connect
/business-rules/decision-matrices/InsurancePremium
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

55.0

## Requires Chatter

No

## HTTP Methods

POST

## Request Body for POST

### JSON Example

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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | [Decision Matrix Input](./connect-requests-decision-matrix-input.md) | List of inputs passed to a decision matrix. An input may contain multiple variables. | Required | 55.0 |
| `options` | [Decision Matrix Options Input](./connect-requests-decision-matrix-options.md) | The lookup options for a decision matrix. | Optional | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-decision-matrix.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
