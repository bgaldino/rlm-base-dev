---
page_id: connect-requests-assessment-responses-assessment-values-input
title: Assessment Values Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-responses-assessment-values-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-requests
legacy_page_id: connect_requests_assessment_responses_assessment_values_input.htm
fetched_at: 2026-11-25
---

# Assessment Values Input

Input representation of the assessment value of Assessment Response request.

## JSON Example

```
{
    "assessmentValues": {
        "Assessment.AssessmentStatus": "Completed",
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
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `Assessment.AssessmentStatus` | String | Status of the assessment. | Optional | 60.0 |
| `assessmentDetails` | [AssessmentDetailsInputRepresentation](./connect-requests-assessment-responses-assessment-details-input.md) | Metadata of the Assessment Questions. | Optional | 63.0 |
| `assessor` | String | Person who carried out the assessment and recorded the responses. | Optional | 63.0 |
| `completedDateTime` | Integer | The date and time when the assessment was completed. | Optional | 63.0 |
| `identifier` | String | Unique identifier of a completed or partially completed assessment in the source system. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-responses-assessment-values-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
