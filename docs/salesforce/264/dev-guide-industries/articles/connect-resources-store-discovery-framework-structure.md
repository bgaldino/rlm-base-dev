---
page_id: connect-resources-store-discovery-framework-structure
title: Omniscript
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-store-discovery-framework-structure.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-resources
legacy_page_id: connect_resources_store_discovery_framework_structure.htm
fetched_at: 2026-11-25
---

# Omniscript

Get the discovery framework structure stored as OmniProcess.

Use this API to get the assessment form layout and submit the assessment data through any custom-built UI. You can show the questionnaire form, capture assessment responses, and save the assessment.

## Resource

```
/connect/omniscript/{omniScriptId}
```

The `omniScriptId` property is the ID of the Omniscript to get the discovery framework structure stored as an OmniProcess.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v60.0/connect/omniscript/CREDIT_CARD_DISPUTE_TRANSACTION_ENGLISH_1?customType=DiscoveryFramework
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

60.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `customType` | String | Custom type of Omniscript. For example, Discovery Framework. | Required | 60.0 |

## Response Body for GET

[Omniscript Output](./connect-responses-omniscript-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-store-discovery-framework-structure.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
