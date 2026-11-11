---
page_id: connect_resources_extraction_context_mappings_get_delete_patch.htm
title: Extraction Context Mappings (DELETE, GET, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_extraction_context_mappings_get_delete_patch.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_context_mapping_parent.htm
fetched_at: 2026-10-13
---

# Extraction Context Mappings (DELETE, GET, PATCH)

Delete extraction context mapping details based on the specified
      context use case mapping ID. Get extraction context mapping details based on the specified
      context use case mapping ID. Update extraction context mapping details based on the specified
      context use case mapping ID.

    

## Resource

      
      

```
/connect/clm/extraction-context-mappings/${contextUseCaseMappingId}
```

    

    

## Available Version

      
      

61.0

    

    

## HTTP Methods

      
      

DELETE GET PATCH

    

    

## Example for DELETE

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/extraction-context-mappings/11jSB000002XTWjYAO
```

    

    

## Example for GET

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/extraction-context-mappings/11jSB000002XTWjYAO
```

    

    

## Example for PATCH

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/extraction-context-mappings/11jSB000002XTWjYAO
```

    

    

## Response Body for GET

      
      

[Extraction Context Mapping](./connect_responses_extraction_context_mapping_output.htm.md)

    

    

## Request Body for PATCH

      
      

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

    

    

## Response Body for PATCH

      
      

[Extraction Context Mappings](./connect_responses_extraction_context_mappings_output.htm.md)
