---
page_id: connect-requests-assessment-links-input
title: Assessment Links Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-links-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-requests
legacy_page_id: connect_requests_assessment_links_input.htm
fetched_at: 2026-11-25
---

# Assessment Links Input

Associated assessments including id, category, reason and sequence.

## Root XML tag

`<assessmentLinks>`

## JSON Example

```
  {
    "id": "0U3SG00000068Cb0AI",
    "category": "0iPSG0000024n0z2AA",
    "reason": "0iPSG0000024n0z2AA",
    "sequence": 333
  }
]
```

## Properties

| Name | Type | Description | Required | Available Version |
| --- | --- | --- | --- | --- |
| `category` | String | The category that the supporting content belongs to. | No | 63.0 |
| `id` | String | The assessment used as the supporting content. | Yes | 55.0 |
| `reason` | String | The reason why the supporting content is required. | No | 63.0 |
| `sequence` | String | The sequence number of the content when multiple contents are available. | No | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-assessment-links-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
