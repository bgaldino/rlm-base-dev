---
page_id: connect_requests_assessment_responses_assessment_reason_input.htm
title: Assessment Reasons Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_responses_assessment_reason_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-11-23
---

# Assessment Reasons Input

Input representation of the assessment reason in Assessment Response request.

## JSON Example

```
{
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
        ]
        }
    }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceRecord` | String | Reason for the assessment. | Optional | 63.0 |
| `referenceValue` | String | The supporting information when there is no Salesforce record to be added as the reference record. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_responses_assessment_reason_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
