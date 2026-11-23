---
page_id: connect_resources_save_assessment_responses.htm
title: Assessment Responses
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_save_assessment_responses.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_resources.htm
fetched_at: 2026-11-23
---

# Assessment Responses

Save assessment responses from an OmniScript built with the Assessment Questions
app.

## Resource

```
/connect/discovery-framework/assessment-responses/omniScriptId
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
{
  "inputs": {
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
  },
  "contextId": "0U3B00000004IhWKAU",
  "assessmentValues": {
    "Assessment.AssessmentStatus": "Completed"
  },
  "completedDateTime": "2024-10-23T14:45:29.123+05:30",
  "assessor": "001SG00000laIWPYA2",
  "identifier": "Test identifier",
  "assessmentDetails": {
    "assessmentReasons": [
      {
        "referenceRecord": "0jySG0000000qRdYAI"
      },
      {
        "referenceRecord": "0SqSG00000005HR0AY"
      },
      {
        "referenceRecord": "0kmSG0000000n7BYAQ",
        "referenceValue": "Medication Request sample"
      },
      {
        "referenceValue": "Reference Record not present"
      }
    ],
    "assessmentQuestionsResponseDetails": {
      "First_Name": {
        "originType": "Auto",
        "reviewerRole": "0hsSG0000002t8TYAQ",
        "reviewer": "003SG00000BTzxpYAD"
      },
      "Last_Name": {
        "originType": "Auto",
        "reviewerRole": "0hsSG0000002t8TYAQ",
        "reviewer": "003SG00000BTzxpYAD"
      },
      "Email": {
        "originType": "Auto",
        "reviewerRole": "0hsSG0000002t8TYAQ",
        "reviewer": "003SG00000BTzxpYAD"
      },
      "Phone": {
        "originType": "Auto",
        "reviewerRole": "0hsSG0000002t8TYAQ",
        "reviewer": "003SG00000BTzxpYAD"
      },
      "Multi_Select": {
        "originType": "Auto",
        "reviewerRole": "0hsSG0000002t8TYAQ",
        "reviewer": "003SG00000BTzxpYAD"
      }
    }
  }
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assessment​Values` | [Assessment Values Input>](./connect_requests_assessment_responses_assessment_values_input.htm.md "Input representation of the assessment value of Assessment Response request.")[] | Values of Assessment fields. | Optional | 60.0 |
| `contextId` | String | Context record for the OmniScript. | Optional | 60.0 |
| `inputs` | [Question Responses Input](./connect_requests_question_responses_input.htm.md "Input for assessment question responses.")[] | Responses for Assessment Questions. | Optional | 60.0 |

## Response Body for POST

[Assessment Responses Output](./connect_responses_assessment_responses_output.htm.md "Output of assessment responses.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_save_assessment_responses.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
