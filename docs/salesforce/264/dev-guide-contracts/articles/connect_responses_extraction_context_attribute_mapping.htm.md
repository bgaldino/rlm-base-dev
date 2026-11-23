---
page_id: connect_responses_extraction_context_attribute_mapping.htm
title: Extraction Context Attribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_attribute_mapping.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Extraction Context Attribute

Output representation of extraction context attribute mapping.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attribute​Id` | String | ID of the extraction context attribute. | Small, 61.0 | 61.0 |
| `attribute​Name` | String | Name of the extraction context attribute. | Small, 61.0 | 61.0 |
| `description` | String | Description of the extraction attribute mapping. | Small, 61.0 | 61.0 |
| `isCustom` | Boolean | Indicates whether the attribute is a custom field (`true`) or not `false`. | Small, 61.0 | 61.0 |
| `target​ObjectField` | String | Target object field mapped to the attribute. | Small, 61.0 | 61.0 |

## Sample Response

```
{
  "contextAttributeMapping": [
    {
      "attributeName": "ContractName",
      "attributeId": "11nxx000001hOozAAE",
      "targetObjectField": "Contract",
      "description": "extract startDate from the document",
      "isCustom": false
    },
    {
      "attributeName": "ContractCustomField",
      "attributeId": "11nxx000001hOozAAE",
      "targetObjectField": "Contract",
      "description": "extract startDate from the document",
      "isCustom": true
    },
    {
      "attributeName": "Description",
      "attributeId": "11nxx000001hOozAAE",
      "targetObjectField": "Contract",
      "description": "extract startDate from the document",
      "isCustom": false
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_attribute_mapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
