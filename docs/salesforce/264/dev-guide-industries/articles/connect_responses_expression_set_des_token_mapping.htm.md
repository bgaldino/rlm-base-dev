---
page_id: connect_responses_expression_set_des_token_mapping.htm
title: Expression Set DES Token Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_des_token_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-11-23
---

# Expression Set DES Token Mapping

Output representation of the DES token mapping in an expression set
version step.

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

"noResultTokenMappings": [
{
"expressionSetMessageToken": "year",
"resourceReference": "Year"
}
]
```

## Properties

| Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `resource​Reference` | String | Name of the expression set resource that’s mapped to a token, such as Variable, Constant, or FiledAlias. | Small, 59.0 | 59.0 |
| `expressionSet​MessageToken` | String | Name of the explainability message template token. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_des_token_mapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
