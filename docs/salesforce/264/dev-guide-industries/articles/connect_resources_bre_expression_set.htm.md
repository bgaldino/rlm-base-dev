---
page_id: connect_resources_bre_expression_set.htm
title: Expression Set Invocation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-11-23
---

# Expression Set Invocation (POST)

Invokes expression sets in Business Rule Engine.

## Resource

```
/connect/business-rules/expressionSet/expressionSetName
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/vXX.X/connect
/business-rules/expressionSet/expressionSetName
```

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

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

You can use more than one `actionContextCode`
for multiple sets of inputs, passed in a single API call.

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | Map<String, Object>[] | List of inputs passed to an expression set. An input may contain multiple variables. Note:  - If the expression set uses a field alias as a variable, append Id to   the object alias to which the field alias belongs, and pass the ID of   the source object linked to the object alias. - If the expression set uses a context definition, append Id to the   context definition developer name and pass the context ID as the   value. | Required | 55.0 |
| `options` | [Expression Set Options Input](./connect_requests_options.htm.md "Input representation of the options for executing an expression set.") | The options for executing an expression set. | Optional | 55.0 |

## Response Body for POST

[Business Rules Result](./connect_responses_business_rules_result.htm.md "Output representation of executing an expression set.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
