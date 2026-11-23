---
page_id: connect_resources_store_discovery_framework_structure.htm
title: Omniscript
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_store_discovery_framework_structure.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_resources.htm
fetched_at: 2026-11-23
---

# Omniscript

Get the discovery framework structure stored as OmniProcess.

Use this API to get the assessment form layout and submit the assessment data through any
custom-built UI. You can show the questionnaire form, capture assessment responses, and save
the assessment.

## Resource

```
/connect/omniscript/omniScriptId
```

The
`omniScriptId` property is the ID of the Omniscript
to get the discovery framework structure stored as an OmniProcess.

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v60.0/connect/omniscript/CreditCard_DisputeTransaction_English_1?customType=DiscoveryFramework
```

## Available Version

60.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `customType` | String | Custom type of Omniscript. For example, Discovery Framework. | Required | 60.0 |

## Response Body for GET

[Omniscript Output](./connect_responses_omniscript_output.htm.md "Output representation of the details of the Omniscript.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_store_discovery_framework_structure.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
