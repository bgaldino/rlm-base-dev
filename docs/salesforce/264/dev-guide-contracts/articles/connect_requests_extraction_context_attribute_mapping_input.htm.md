---
page_id: connect_requests_extraction_context_attribute_mapping_input.htm
title: Extraction Context Attribute Mapping Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_extraction_context_attribute_mapping_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Extraction Context Attribute Mapping Input

Input representation of attribute mappings used in the extraction context.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attribute​Id` | String | ID of the context attribute mapping required for update. | Required | 61.0 |
| `description` | String | Description of what the attribute maps to. | Optional | 61.0 |

    

    

## JSON Example

      
      

```
{
  "contextAttributeMapping": [
    {
      "attributeId": "11nxx000001hOozAAE",
      "description": "extract startDate from the document"
    },
    {
      "attributeId": "11nxx000001hOozAAV",
      "description": "extract startDate from the document"
    },
    {
      "attributeId": "11nxx000001hOozAAR",
      "description": "extract startDate from the document"
    }
  ]
}
```
