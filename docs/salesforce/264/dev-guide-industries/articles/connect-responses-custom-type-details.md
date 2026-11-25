---
page_id: connect-responses-custom-type-details
title: Custom Type Details
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-custom-type-details.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-responses
legacy_page_id: connect_responses_custom_type_details.htm
fetched_at: 2026-11-25
---

# Custom Type Details

Output representation of the custom type details of the Omniscript elements.

## JSON Example

```
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Can you provide more details about the transaction"
            }
          }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `discovery​Framework` | [OS Element Discovery Framework](./connect-responses-os-element-discovery-framework-output.md)[] | Custom type details for the Omniscript element for Discovery framework. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-custom-type-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
