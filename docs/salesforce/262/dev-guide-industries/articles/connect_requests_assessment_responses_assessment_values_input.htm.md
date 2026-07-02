---
page_id: connect_requests_assessment_responses_assessment_values_input.htm
title: Assessment Values Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_responses_assessment_values_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-06-25
---

# Assessment Values Input

Input representation of the assessment value of Assessment Response request.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `Assessment.AssessmentStatus` | String | Status of the assessment. | Optional | 60.0 |
    | `assessmentDetails` | [AssessmentDetailsInputRepresentation](./connect_requests_assessment_responses_assessment_details_input.htm.md "Input representation of the assessment details of Assessment Response request.") | Metadata of the Assessment Questions. | Optional | 63.0 |
    | `assessor` | String | Person who carried out the assessment and recorded the responses. | Optional | 63.0 |
    | `completedDateTime` | Integer | The date and time when the assessment was completed. | Optional | 63.0 |
    | `identifier` | String | Unique identifier of a completed or partially completed assessment in the source system. | Optional | 63.0 |
