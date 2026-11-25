---
page_id: connect-requests-question-responses-input
title: Question Responses Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-question-responses-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-requests
legacy_page_id: connect_requests_question_responses_input.htm
fetched_at: 2026-11-25
---

# Question Responses Input

Input for assessment question responses.

## JSON Example

The properties under `questionResponses` are in the following format:

```
{
  "questionResponses": {
    "ELEMENT_API_NAME OR ASSESSMENT_QUESTION UNIQUE_INDEX 1": "value",
    "ELEMENT_API_NAME OR ASSESSMENT_QUESTION UNIQUE_INDEX 2": {
      "CHILD_ELEMENT_API_NAME OR QUESTION UNIQUE_INDEX 1": "value",
      "CHILD_ELEMENT_API_NAME OR QUESTION UNIQUE_INDEX 2": "value",
     ...
    }
  }
}
```

For example:

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-question-responses-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
