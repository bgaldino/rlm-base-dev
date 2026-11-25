---
page_id: connect-requests-expression-set-input
title: Expression Set Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_input.htm
fetched_at: 2026-11-25
---

# Expression Set Input

Input representation of the expression set create and update request.

## Root XML tag

`<ExpressionSetInput>`

## JSON Example

```
{
  "name": "CTX Mapping ES",
  "apiName": "CTX_Mapping_ES_1",
  "description": "...",
  "usageType": "Bre",
  "contextDefinitions": [
    {
      "id": "11Oxx0000006PcLEAU"
    }
  ],
  "versions": [
    {
      "name": "CTX_Mapping_ES_1 V1",
      "apiName": "CTX_Mapping_ES_1_V1",
      "description": "Sample CTX Mapping",
      "startDate": "2022-11-14T20:31:47.000+0000",
      "endDate": "2022-11-14T20:31:47.000+0000",
      "versionNumber": 1,
      "rank": 1,
      "enabled": true,
      "showExplExternally": false,
      "steps": [
        {
          "name": "Condition1",
          "description": "Condition step for conditions w.r.t product",
          "sequenceNumber": 1,
          "resultIncluded": true,
          "stepType": "Condition",
          "conditionExpression": {
            "expression": "productName == 'iPhone' && productColor == 'Red'",
            "resultParameter": "condition_output__1"
          }
        }
      ],
      "variables": [
        {
          "name": "productName",
          "collection": false,
          "dataType": "Text",
          "description": "productName",
          "input": true,
          "output": false,
          "type": "Variable"
        },
        {
          "name": "productColor",
          "collection": false,
          "dataType": "Text",
          "description": "productColor",
          "input": true,
          "output": false,
          "type": "Variable"
        },
        {
          "name": "condition_output__1",
          "dataType": "Boolean",
          "description": "condition_output__1",
          "input": false,
          "output": true,
          "resultStep": "Condition1",
          "type": "Variable"
        }
      ]
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `apiName` | String | Unique name of the expression set. | Required | 58.0 |
| `context​Definitions` | [Context Definition Input](./connect-requests-context-definition-input.md) | List of context definitions in an expression set. | Optional | 58.0 |
| `description` | String | Description of the expression set. | Optional | 58.0 |
| `name` | String | Name of the expression set. | Required | 58.0 |
| `usage​Type` | String | Usage type of the expression set. Valid value is `Bre`. The default value is `Bre`. When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Required | 58.0 |
| `versions` | [Expression Set Version Input](./connect-requests-expression-set-version.md)[] | List of the expression set versions. | Optional | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
