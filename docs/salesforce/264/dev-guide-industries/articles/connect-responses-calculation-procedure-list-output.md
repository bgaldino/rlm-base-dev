---
page_id: connect-responses-calculation-procedure-list-output
title: Calculation Procedure List Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-calculation-procedure-list-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_calculation_procedure_list_output.htm
fetched_at: 2026-11-25
---

# Calculation Procedure List Output

Output representation of the expression set result list.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**Sample Response**

: 

```
{
   "calculationProcedures" : [ {
      "id" : "0k0x0000000008ZAAQ",
      "description" : "Test calculation set",
      "name" : "Expression_Set_1"
   },{
      "id" : "0k0x000000000BQAAY",
      "description" : "Test procedure set",
      "name" : "Expression_Set_2"
   } ],
   "code" : "200",
   "isSuccess" : true,
   "message" : ""
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `calculationProcedures` | [Calculation Procedure Output[]](./connect-responses-calculation-procedure-output.md) | The list of the expression sets. | Small, 53.0 | 53.0 |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `success` | Boolean | Indicates whether the request was successful. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-calculation-procedure-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
