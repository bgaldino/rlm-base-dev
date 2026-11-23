---
page_id: connect_responses_decision_model_export_output.htm
title: Decision Model Export Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_model_export_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-11-23
---

# Decision Model Export Output

Output representation of a completed DMN (Decision Model Notation)
export request.

## JSON Example

```
{
   "message":"OK",
   "success":true,
   "errors":[
      {
         "errorCode":"BAD_REQUEST",
         "errorMessage":"We couldn’t find this record. Specify a valid ID for decisionModelEntityIds parameter.",
         "recordId":"0lNRO00000004fsdfAA"
      }
   ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Decision Model Export Error](./connect_responses_decision_model_export_error.htm.md "Error representation of a failed DMN (Decision Model Notation) export request.")[] | List of errors corresponding to a failed export request. | Small, 58.0 | 58.0 |
| `message` | String | Response message from the completed export request. | Small, 58.0 | 58.0 |
| `success` | Boolean | Indicates whether the export request was successful (`true`) or not (`false`). | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_model_export_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
