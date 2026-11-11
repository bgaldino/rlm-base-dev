---
page_id: connect_resources_extraction_context_mapping.htm
title: Extraction Context Mapping (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_extraction_context_mapping.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_context_mapping_parent.htm
fetched_at: 2026-10-13
---

# Extraction Context Mapping (POST)

Create extraction context-mapping details that show how extracted
      data is associated with Salesforce fields.

    

## Resource

      
      

```
/connect/clm/extraction-context-mappings
```

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/extraction-context-mappings
```

    

    

## Available Version

      
      

61.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "ContextUsecaseMapping": {
    "templateName": "ContractExtractionTemplate",
    "contextDefinitionDeveloperName": "ContractExtractionContextDefinition",
    "mappingName": "ContractExtractionMappingName",
    "targetObject": "Contract",
    "recordType": "CLM",
    "additionalUseCaseInput": "{\"ModelName\":\"OpenAI\"}"
  },
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

      

**Properties**

      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​AttributeMapping` | [Extraction Context Attribute Mapping Input[]](./connect_requests_extraction_context_attribute_mapping_input.htm.md) | List of attributes and their mappings. | Yes | 61.0 |
| `context​UseCase​Mapping` | [Extraction Context Use Case Mapping Input](./connect_requests_extraction_context_use_case_mapping_input.htm.md) | Details of the use case for which the mapping is defined. | Yes | 61.0 |

    

    

## Response Body for POST

      
      

[Extraction Context Mappings](./connect_responses_extraction_context_mappings_output.htm.md)
