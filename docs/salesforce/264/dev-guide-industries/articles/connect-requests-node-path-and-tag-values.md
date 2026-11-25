---
page_id: connect-requests-node-path-and-tag-values
title: Node Path and Tag Values Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-node-path-and-tag-values.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_node_path_and_tag_values.htm
fetched_at: 2026-11-25
---

# Node Path and Tag Values Input

Input representation of the node path which needs to update with tag details.

## JSON Example

```
{
            "nodePath": {
                "dataPath": [
                    "001xx000003GbQSAA0"
                ]
            },
            "tagValues": [
                {
                    "tagName": "Name",
                    "tagValue": "updatedAccount"
                },
                {
                    "tagName": "City",
                    "tagValue": "Bangalore"
                }
            ]
        }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `nodePath` | String | Path of Context Data Record. | Required | 63.0 |
| `tagValues` | [List<Context​TagValueInput​Representation](./connect-requests-tag-values-input.md) | List of Tag Names to be updated and their values. | Required | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-node-path-and-tag-values.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
