---
page_id: connect-requests-document-decision-input
title: Document Decision Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-document-decision-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-requests
legacy_page_id: connect_requests_document_decision_input.htm
fetched_at: 2026-11-25
---

# Document Decision Input

Input representation of the Document Decision request.

## JSON Example

```
{
  "inputs": [
    {
      "Country": "USA",
      "State": "CA"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | List<Map<String, Object>> | List of inputs passed to Decision Table. Each key is a Decision Table field name, and each value is valid for that field. | Required | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-document-decision-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
