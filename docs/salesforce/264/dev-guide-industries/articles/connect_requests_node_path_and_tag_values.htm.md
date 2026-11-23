---
page_id: connect_requests_node_path_and_tag_values.htm
title: Node Path and Tag Values Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_node_path_and_tag_values.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Node Path and Tag Values Input

Input representation of the node path which needs to update with tag
details.

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
| `tagValues` | [List<Context​TagValueInput​Representation](./connect_requests_tag_values_input.htm.md "Input representation of the list of Tag Names to be updated and their values.") | List of Tag Names to be updated and their values. | Required | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_node_path_and_tag_values.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
