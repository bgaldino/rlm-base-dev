---
page_id: connect-requests-assessment-responses-assessment-details-input
title: Assessment Details Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-responses-assessment-details-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-requests
legacy_page_id: connect_requests_assessment_responses_assessment_details_input.htm
fetched_at: 2026-11-25
---

# Assessment Details Input

Input representation of the assessment details of Assessment Response request.

## JSON Example

```
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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assessmentQuestionsResponseDetails` | Map<String, Object> | The details of the assessment questions response. Only available for Health Cloud users. | Optional | 63.0 |
| `assessmentReasons` | [List<AssessmentReasonInputRepresentation>](./connect-requests-assessment-responses-assessment-reason-input.md) | Details of the assessment. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-responses-assessment-details-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
