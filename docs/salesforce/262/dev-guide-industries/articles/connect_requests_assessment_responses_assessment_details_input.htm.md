---
page_id: connect_requests_assessment_responses_assessment_details_input.htm
title: Assessment Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_responses_assessment_details_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-06-25
---

# Assessment Details Input

Input representation of the assessment details of Assessment Response request.

JSON example
:   ```
    {
        "assessmentDetails": {
            "assessmentReasons": [
                {
                    "referenceRecord": "0jySG0000000qRdxxI"
                },
                {
                    "referenceRecord": "0SqSG00000005HRxxY"
                },
                {
                    "referenceRecord": "0kmSG0000000n7BxxQ",
                    "referenceValue": "Medication Request sample"
                },
                {
                    "referenceValue": "Reference Record not present"
                }
            ],
            "assessmentQuestionsResponseDetails": {
                "First_Name": {
                    "originType": "Auto",
                    "reviewerRole": "0hsSG0000002t8TxxQ",
                    "reviewer": "003SG00000BTzxpxxD"
                },
                "Last_Name": {
                    "originType": "Auto",
                    "reviewerRole": "0hsSG0000002t8TxxQ",
                    "reviewer": "003SG00000BTzxpxxD"
                },
                "Email": {
                    "originType": "Auto",
                    "reviewerRole": "0hsSG0000002t8TxxQ",
                    "reviewer": "003SG00000BTzxpxxD"
                },
                "Phone": {
                    "originType": "Auto",
                    "reviewerRole": "0hsSG0000002t8TxxQ",
                    "reviewer": "003SG00000BTzxpxxD"
                },
                "Multi_Select": {
                    "originType": "Auto",
                    "reviewerRole": "0hsSG0000002t8TxxQ",
                    "reviewer": "003SG00000BTzxpxxD"
                }
            }
        }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `assessmentQuestionsResponseDetails` | Map<String, Object> | The details of the assessment questions response. Only available for Health Cloud users. | Optional | 63.0 |
    | `assessmentReasons` | [List<AssessmentReasonInputRepresentation>](./connect_requests_assessment_responses_assessment_reason_input.htm.md "Input representation of the assessment reason in Assessment Response request.") | Details of the assessment. | Optional | 63.0 |
