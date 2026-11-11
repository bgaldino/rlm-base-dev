---
page_id: connect_resources_document_template.htm
title: Document Templates (GET, PATCH, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_template.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_design_document_template_resources.htm
fetched_at: 2026-10-13
---

# Document Templates (GET, PATCH, POST)

Access document template actions, including template creation with the Document Template Designer.

    

## Resource

      
      

```
/connect/docgen/document-templates
```

    

    

## GET Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/docgen/document-templates?offset=${offset}&limit=${limit}&searchString=${searchString}
```

    

    

## PATCH Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/docgen/document-templates?documentTemplateId=${documentTemplateId}
```

    

    

## POST Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/docgen/document-templates?documentTemplateId=${documentTemplateId}&action=${action}
```

    

    

## Available Version

      
      

60.0

    

    

## HTTP Methods

      
      

GET, PATCH, POST

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cloneOnly` | String | Filters the results to return only the document templates that can be cloned. | Optional | 66.0 |
| `limit` | String | Number of document templates per page. The default value is 20. | Optional | 60.0 |
| `offset` | String | Number of records to skip. The default value is 0. | Optional | 60.0 |
| `searchString` | String | Search term that is used to retrieve a list of document templates. | Optional | 60.0 |
| `type` | String | Filters the list of document templates by the file type. | Optional | 66.0 |
| `usageType` | String | Filters the list of document templates by the usage type. | Optional | 66.0 |

    

    

## Response Body for GET

      
      

[Document Template List](./connect_responses_document_template_list.htm.md)

    

    

## Request Body for PATCH

      
      

**JSON Example**

      

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

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
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

    

    

## Request Parameters for PATCH

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentTemplateId` | String | ID of the document template for operations like cloning or creating a new version. | Required | 60.0 |
| `documentTemplateUpdateInput` | Object | Specifies the details to modify an existing document template. | Optional | 64.0 |

    

    

## Response Body for PATCH

      
      

[Document Template](./connect_responses_document_template.htm.md)

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "name": "TemplateName",
  "type": "MicrosoftWord/MicrosoftPowerpoint/Microsoft365Word",
  "tokenMappingMethodType": "OmniDataTransform",
  "tokenMappingType": "JSON",
  "extractOmniDataTransformName": "ExtractName",
  "mapperOmniDataTransformName": "MapperName",
  "contentDocumentId": "069xx0000004CyeAAE",
  "documentGenerationMechanism": "ServerSide",
  "usageType": "Contract_Lifecycle_Management",
  "tokenList": "token1,token2,token3"
}
```

      

This example shows a sample request with `ContextService` as the value of the tokenMappingMethodType property.

      

```
{
  "name": "TemplateName",
  "type": "MicrosoftWord/MicrosoftPowerpoint/Microsoft365Word",
  "tokenMappingMethodType": "ContextService",
  "contextDefinitionName": "QuoteProposal",
  "contextMappingName": "QuoteToContextMapping", 
  "customClassName": "QuoteBundleTransformer", 
  "contextFilterName": "QuoteWithLargeQtyLineItems",
  "contextTransformationName": "QuoteBundleTransformation",
  "tokenMappingType": "JSON",
  "extractOmniDataTransformName": "ExtractName",
  "mapperOmniDataTransformName": "MapperName",
  "contentDocumentId": "069xx0000004CyeAAE",
  "documentGenerationMechanism": "ClientSide",
  "usageType": "Contract_Lifecycle_Management",
  "tokenList": "token1,token2,token3"
}
```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `content​DocumentId` | String | ID of the Document associated with a document template. | Optional | 60.0 |
| `contextDefinition​Name` | String | Name of the context definition that contains the mapping details used for extraction in the Context Service token mapping type. | Required if the tokenMappingMethodTypeproperty is set to `ContextService`. | 64.0 |
| `contextMapping​Name` | String | Name of the context mapping used for extraction in the Context Service token mapping type. | Required if the tokenMappingMethodTypeproperty is set to `ContextService`. | 64.0 |
| `contextFilter​Name` | String | Name of the context filter that’s used to filter, order, or limit the data extracted from the context service at run time. This property is available only when the tokenMappingMethodType property value is `ContextService`. | Optional | 66.0 |
| `contextTransformation​Name` | String | Name of the context transformation that’s used to transform the data extracted from the context service at run time. This property is available only when the tokenMappingMethodType property value is `ContextService`. | Optional | 67.0 |
| `customClass​Name` | String | Name of a custom Apex class that’s used to transform token data before document generation. This property is available only when the tokenMappingMethodType property value is `ContextService`. | Optional | 66.0 |
| `document​Generation​Mechanism` | String | Specifies the method for generating the document. Possible values are `Client-side` or `Server-side`. The default value is `Client-side`. | Optional | 60.0 |
| `extractOmniDataTransformName` | String | Name of the OmniDataTransform bundle of the extract type. | Optional | 60.0 |
| `mapper​OmniData​Transform​Name` | String | Name of the OmniDataTransform bundle of the mapper type. | Optional | 60.0 |
| `name` | String | Name of the document template. | Required | 60.0 |
| `tokenList` | String | List of tokens present in the document template. | Optional | 60.0 |
| `token​Mapping​MethodType` | String | Processing method for the data that can originate from same source object. Possible values are `ContextService` or `OmniDataTransform`. The default value is `ContextService`. | Required | 60.0 |
| `token​Mapping​Type` | String | Mapping type for tokens of the document template. | Required | 60.0 |
| `type` | String | Type of document template. | Required | 60.0 |
| `usageType` | String | Usage type of the document template. | Optional | 60.0 |

    

    

## Request Parameters for POST

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | Action to be performed on the document template. Possible values are `Clone` or `NewVersion`. | Optional | 60.0 |
| `documentTemplate` | Object | Specifies the details of a new document template resource. | Optional | 64.0 |
| `documentTemplateId` | String | ID of the document template for operations like cloning or creating a new version. | Optional | 60.0 |

    

    

## Response Body for POST

      
      

[Document Template](./connect_responses_document_template.htm.md)
