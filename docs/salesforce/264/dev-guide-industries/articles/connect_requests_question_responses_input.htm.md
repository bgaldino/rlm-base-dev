---
page_id: connect_requests_question_responses_input.htm
title: Question Responses Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_question_responses_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-11-23
---

# Question Responses Input

Input for assessment question responses.

## JSON Example

The properties under `questionResponses` are in the following
format:

```
{
  "questionResponses": {
    "Element_APIName or AssessmentQuestion uniqueIndex 1": "value",
    "Element_APIName or AssessmentQuestion uniqueIndex 2": {
      "Child_element_APIName or Question uniqueIndex 1": "value",
      "Child_element_APIName or Question uniqueIndex 2": "value",
     ...
    }
  }
}
```

For
example:

```
{
  "questionResponses": {
    "ootb__DF_API_MSelect1": "Y;N",
    "ootb__DF_API_MSelect2": "1;2;3",
    "ootb__DF_API_RG1": {
      "ootb__DF_API_Radio1": "Y",
      "ootb__DF_API_Radio2": "N",
      "ootb__DF_API_Radio3": "M"
    },
    "ootb__DF_API_Text": "TestingDF",
    "ootb__DF_API_Select1": "1",
    "ootb__DF_API_Select2": "w",
    "ootb__DF_API_EditBlock2": {
      "ootb__DF_API_Int": 5
    },
    "ootb__DF_API_Boolean": true,
    "ootb__DF_API_Formula": true
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `question​Responses` | Map<String, Object> | Responses map for Assessment Questions. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_question_responses_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
