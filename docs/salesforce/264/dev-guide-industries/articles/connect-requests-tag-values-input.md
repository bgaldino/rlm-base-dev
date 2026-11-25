---
page_id: connect-requests-tag-values-input
title: Tag Values Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-tag-values-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_tag_values_input.htm
fetched_at: 2026-11-25
---

# Tag Values Input

Input representation of the list of Tag Names to be updated and their values.

## JSON Example

```
                {
                    "tagName": "Name",
                    "tagValue": "updatedAccount"
                },
                {
                    "tagName": "City",
                    "tagValue": "Bangalore"
                }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `tagName` | String | Name of tag thats need to be updated. | Required | 63.0 |
| `tagValue` | String | Updated value of tags. | Required | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-tag-values-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
