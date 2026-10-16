---
page_id: connect_responses_extraction_context_use_case_mapping.htm
title: Extraction Context Use Case Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_use_case_mapping.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Extraction Context Use Case Mapping

Output representation of extraction context use case mapping.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additional​UseCase​Input` | String | Stores the additional input required to execute the selected use case. For example, this property can store the LLM model associated with a template for the Extract Contract Details use case, such as `{"ModelName":"OpenAI"}`. | Small, 67.0 | 67.0 |
| `context​Definition` | [Extraction Context Definition](./connect_responses_extraction_context_definition.htm.md) | Details of the extraction context definition. | Small, 61.0 | 61.0 |
| `context​Mapping` | [Extraction Context Mapping](./connect_responses_extraction_context_mapping.htm.md) | Details of the extraction context mapping. | Small, 61.0 | 61.0 |
| `record​Type` | String | Name of the record type associated with the use case mapping. | Small, 61.0 | 61.0 |
| `target​Object` | String | Name of the target object for the use case mapping. | Small, 61.0 | 61.0 |
| `template​Name` | String | Name of the template associated with the use case mapping. | Small, 61.0 | 61.0 |

    

    

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
  }
}
```
