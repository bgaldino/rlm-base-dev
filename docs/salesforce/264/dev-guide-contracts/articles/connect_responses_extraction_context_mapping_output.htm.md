---
page_id: connect_responses_extraction_context_mapping_output.htm
title: Extraction Context Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_mapping_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Extraction Context Mapping

Output representation of extraction context mapping.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Attribute​Mapping` | [Context Attribute Mapping[]](./connect_responses_extraction_context_attribute_mapping.htm.md) | List of extraction context attribute mappings.. | Small, 61.0 | 61.0 |
| `context​UseCase​Mapping` | [Extraction Context Use Case Mapping](./connect_responses_extraction_context_use_case_mapping.htm.md) | Details of extraction context use case mapping. | Small, 61.0 | 61.0 |
| `context​UseCase​Mapping​Id` | String | Record ID of the context use case mapping. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the retrieval of mapping was successful (`true`) or not `false`. | Small, 61.0 | 61.0 |

    

    

## Sample Response

      
      

```
{
  "contextUseCaseMapping": {
    "templateName": "ContractExtractionTemplate",
    "targetObject": "Contract",
    "recordType": "CLM",
    "contextDefinitionName": {
      "id": "11Oxx0000007MnhEAE",
      "developerName": "David Taylor",
      "name": "Dav"
    },
    "contextMapping": {
      "id": "11Oxx0000007MnhEAE",
      "name": "David Taylor"
    },
    "additionalUseCaseInput": "{\"ModelName\":\"OpenAI\"}"
  },
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
  ],
  "isSuccess": true,
  "contextUseCaseMappingId": "ContextUseCaseMappingId"
}
```
