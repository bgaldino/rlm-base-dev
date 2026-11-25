---
page_id: connect-responses-os-element-discovery-framework-output
title: Omniscript Element Discovery Framework Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-os-element-discovery-framework-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-responses
legacy_page_id: connect_responses_os_element_discovery_framework_output.htm
fetched_at: 2026-11-25
---

# Omniscript Element Discovery Framework Output

Output representation of the custom type details of the Omniscript elements for Discovery Framework.

## JSON Example

```
      "discoveryFramework": {
       "questionText": "Can you provide more details about the transaction"
    }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description of the question for the Discovery Framework question type element. | Small, 63.0 | 63.0 |
| `displayTextCategory` | String | The category of the display text when the data type is Text Block. This field valued is returned for Health Cloud customers only. | Small, 63.0 | 63.0 |
| `question​Category` | String | Category of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​DataType` | String | Data type of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Developer​Name` | String | Developer name of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Namespace` | String | Namespace of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Text` | String | Text of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |

**Note:**

When you receive a GET response, HTML replaces reserved characters with their corresponding entities. For example, “What’s your address” will appear as “What&#39;s your address.”

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-os-element-discovery-framework-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
