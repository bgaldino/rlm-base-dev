---
page_id: connect-responses-calculation-procedure-detail-output
title: Calculation Procedure Detail Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-calculation-procedure-detail-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_calculation_procedure_detail_output.htm
fetched_at: 2026-11-25
---

# Calculation Procedure Detail Output

Output representation of the expression set details.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**Sample Response**

: 

```
{
   "code" : "200",
   "id" : "0k0x000000000BQAAY",
   "inputVariables" : [ {
      "dataType" : "Number",
      "name" : "var1"
   } ],
   "isSuccess" : true,
   "message" : "",
   "name" : "RuleWith100Conditions42",
   "outputVariables" : [ {
      "dataType" : "Number",
      "name" : "var2"
   } ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `description` | String | The description of the expression set. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the expression set record. | Small, 53.0 | 53.0 |
| `inputVariables` | [Calculation Procedure Variable Output[]](./connect-responses-calculation-procedure-variable-output.md) | The list of input variables of the expression set. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `name` | String | The name of the expression set. | Small, 53.0 | 53.0 |
| `outputVariables` | [Calculation Procedure Variable Output[]](./connect-responses-calculation-procedure-variable-output.md) | The list of output variables of the expression set. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-calculation-procedure-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
