---
page_id: connect-responses-decision-matrix-result-list
title: Decision Matrix Result List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-matrix-result-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses-1
legacy_page_id: connect_responses_decision_matrix_result_list.htm
fetched_at: 2026-11-25
---

# Decision Matrix Result List

Output representation of the decision matrix result list.

**Sample Response**

: 

```
{
   "code" : "200",
   "decisionMatrices" : [ {
      "id" : "0lIx0000000001TEAQ",
      "name" : "Decision_Matrix_Test1"
   }, {
      "id" : "0lIx0000000000pEAA",
      "name" : "Decision_Matrix_Test2”
   }, {
      "id" : "0lIx0000000001OEAQ",
      "name" : "Decision_Matrix_Test3”
   } ],
   "isSuccess" : true,
   "message" : ""
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `decisionMatrices` | [Decision Matrix Basic[]](./connect-responses-decision-matrix-basic.md) | The list of the decision matrices. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-matrix-result-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
