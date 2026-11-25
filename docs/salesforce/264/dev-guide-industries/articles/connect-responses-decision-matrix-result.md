---
page_id: connect-responses-decision-matrix-result
title: Decision Matrix Result
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-matrix-result.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses-1
legacy_page_id: connect_responses_decision_matrix_result.htm
fetched_at: 2026-11-25
---

# Decision Matrix Result

Output representation of the decision matrix details.

**Sample Response**

: 

```
{
   "code" : "200",
   "id" : "0lIx0000000000zEAA",
   "inputVariables" : [ {
      "dataType" : "Number",
      "id" : "0lJx0000000000zEAA",
      "name" : "IN1"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000010EAA",
      "name" : "IN2"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000011EAA",
      "name" : "IN3"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000012EAA",
      "name" : "IN4"
   } ],
   "isSuccess" : true,
   "message" : "",
   "name" : "DescisionMatrix2",
   "outputVariables" : [ {
      "dataType" : "Text",
      "id" : "0lJx00000000013EAA",
      "name" : "OUT1"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000014EAA",
      "name" : "OUT2"
   } ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `description` | String | The description of the decision matrix. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the decision matrix record. | Small, 53.0 | 53.0 |
| `inputVariables` | [Decision Matrix Variable[]](./connect-responses-decision-matrix-variable.md) | The list of input variables of the decision matrix. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `name` | String | The name of the decision matrix. | Small, 53.0 | 53.0 |
| `outputVariables` | [Decision Matrix Variable[]](./connect-responses-decision-matrix-variable.md) | The list of output variables of the decision matrix. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-matrix-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
