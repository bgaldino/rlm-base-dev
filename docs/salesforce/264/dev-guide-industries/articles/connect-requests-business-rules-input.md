---
page_id: connect-requests-business-rules-input
title: Business Rules Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-business-rules-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_business_rules_input.htm
fetched_at: 2026-11-25
---

# Business Rules Input

Input representation of an expression set.

## JSON Example

```
{
  "inputs": [
    {
      "age": "25",
      "state": "CA",
      "PatientId": "001xx000003GYjnAAG"
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z",
    "useDatesOnly": "true",
    "actionContextCode": "9QLxx0000004C92GAE",
    "explainabilitySpecName": "ES_One_Explainability"
  }
}
```

```
{
  "inputs": [
    {
      "age": "25",
      "state": "CA",
      "PatientId":"001xx000003GYjnAAG",
      "__actionContextCode":"001xx000003GYjnAAG"
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z",
    "useDatesOnly": "true"
  }
}
```

**Note:**

You can use more than one `actionContextCode` for multiple sets of inputs, passed in a single API call.

## Properties

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | Map<String, Object>[] | List of inputs passed to an expression set. An input may contain multiple variables. Note: If the expression set uses a field alias as a variable, append Id to the object alias to which the field alias belongs, and pass the ID of the source object linked to the object alias.If the expression set uses a context definition, append Id to the context definition developer name and pass the context ID as the value. | Required | 55.0 |
| `options` | [Expression Set Options Input](./connect-requests-options.md) | The options for executing an expression set. | Optional | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-business-rules-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
