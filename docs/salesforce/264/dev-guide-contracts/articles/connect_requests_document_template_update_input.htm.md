---
page_id: connect_requests_document_template_update_input.htm
title: Document Template Update Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_document_template_update_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Document Template Update Input

Input representation to update a document template.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              
              

              
              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `content​Document​Id` | String | ID of the document associated with a document template. | Optional | 60.0 |
| `contextDefinition​Name` | String | Name of the context definition that contains the mapping details used for extraction in the Context Service token mapping type. | Required if the tokenMappingMethodTypeproperty is set to `ContextService`. | 64.0 |
| `contextMapping​Name` | String | Name of the context mapping used for extraction in the Context Service token mapping type. | Required if the tokenMappingMethodTypeproperty is set to `ContextService`. | 64.0 |
| `contextFilter​Name` | String | Name of the context filter that’s used to filter, order, or limit the data extracted from the context service at run time. This property is available only when tokenMappingMethodType property value is `ContextService`. | Optional | 66.0 |
| `contextTransformation​Name` | String | Name of the context transformation that’s used to transform the data extracted from the context service at run time. This property is available only when tokenMappingMethodType property value is `ContextService`. | Optional | 67.0 |
| `customClass​Name` | String | Name of a custom Apex class that’s used to transform token data before document generation. This property is available only when tokenMappingMethodType property value is `ContextService`. | Optional | 66.0 |
| `document​Generation​Mechanism` | String | Specifies the method for generating the document. Possible values are `Client-side` or `Server-side`. The default value is `Client-side`. | Optional | 60.0 |
| `extract​OmniData​Transform​Name` | String | Name of the OmniDataTransform bundle of the extract type. | Optional | 60.0 |
| `isActive` | Boolean | Indicates whether the document template is set to active (`true`) or inactive (`false`). | Optional | 60.0 |
| `mapper​OmniData​Transform​Name` | String | Name of the OmniDataTransform bundle of the mapper type. | Optional | 60.0 |
| `should​Display​Unmapped​Token` | Boolean | Indicates whether the document template unmapped tokens be displayed (`true`) or not (`false`). | Optional | 60.0 |
| `status` | String | Status to be set for the document template. | Optional | 60.0 |
| `tokenList` | String | List of tokens present in the document template. | Optional | 60.0 |
| `token​Mapping​MethodType` | String | Processing method for data that can originate from the same source object. Possible values are `ContextService` or `OmniDataTransform`. The default value is `ContextService`. | Required | 60.0 |
| `usageType` | String | Usage type of the document template. | Optional | 60.0 |

    

    

## JSON Example

      
      

```
{
  "isActive": "false",
  "status": "Draft",
  "documentGenerationMechanism": "ClientSide",
  "extractOmniDataTransformName": "Extractor",
  "mapperOmniDataTransformName": "Mapper",
  "shouldDisplayUnmappedToken": "false",
  "tokenList": "token1,token2,token3",
  "tokenMappingMethodType": "ContextService",
  "contextDefinitionName": "QuoteProposal",
  "contextMappingName": "QuoteToContextMapping",
  "customClassName": "QuoteBundleTransformer", 
  "contextFilterName": "QuoteWithLargeQtyLineItems",
  "contextTransformationName": "QuoteBundleTransformation",
  "usageType": "Contract_Lifecycle_Management",
  "contentDocumentId": "069xxxxxxxxxxxxxxx"
}
```
