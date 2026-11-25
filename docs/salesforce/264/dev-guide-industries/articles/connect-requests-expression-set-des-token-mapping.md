---
page_id: connect-requests-expression-set-des-token-mapping
title: Expression Set DES Token Mapping Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-des-token-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_des_token_mapping.htm
fetched_at: 2026-11-25
---

# Expression Set DES Token Mapping Input

Input representation of the DES token mapping in an expression set version step.

## Root XML tag

`<ExpressionSetDesTokenMappingInput>`

## JSON Example

```
"passedMessageTokenMappings": [
{
"expressionSetMessageToken": "price",
"resourceReference": "DM1__Price"
}
],
"failedMessageTokenMappings": [
{
"expressionSetMessageToken": "model",
"resourceReference": "Model"
}
],

"noResultMessageTokenMappings": [
{
"expressionSetMessageToken": "year",
"resourceReference": "Year"
}
]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `resource​Reference` | String | Name of the expression set resource that’s mapped to a token, such as Variable, Constant, or FiledAlias. | Required | 59.0 |
| `expressionSet​MessageToken` | String | Name of the explainability message template token. | Required | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-des-token-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
