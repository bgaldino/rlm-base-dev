---
page_id: connect_resources_get_procedure_plan_definition_records.htm
title: Procedure Plan Definitions (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_procedure_plan_definition_records.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Procedure Plan Definitions (GET, POST)

Get the records of procedure plan definitions. Additionally, create a
      record of a procedure plan definition.

    
      
        
          

**Resource**

          
: 
            

```
/connect/procedure-plan-definitions
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com​/services/data​/v68.0/connect/​procedure-plan-definitions?​isTemplate=true
```

          

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: GET, POST

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isTemplate` | Boolean | Indicates whether to return a list of file-based definitions (`true`) or not (`false`). This API request returns a list of database-based definitions, by default. | Optional | 62.0 |

          

        
        
          

**Response body for GET**

          
: [Procedure Plan
              Definitions](./connect_responses_procedure_plan_definitions_output.htm.md)

        
        
          

**Request body for POST**

          
: 
            
              
                

**JSON example**

                
: This example shows a sample request to
            create a procedure plan definition record by using the Procedure Plan Definitions (POST)
            API.

```
  {
  "description": "Definition for Quote",
  "developerName": "Quote_Definition_Sample",
  "name": "Quote_Definition_Sample",
  "processType": "Default",
  "primaryObject": "BusinessHours",
  "procedurePlanDefinitionVersions": [
    {
      "active": false,
      "contextDefinition": "SalesTransactionContext__stdctx",
      "readContextMapping": "QuoteEntitiesMapping",
      "saveContextMapping": "QuoteEntitiesMapping",
      "effectiveFrom": "2024-07-15T10:15:30.000Z",
      "developerName": "Quote_Definition_V1",
      "rank": 1
    }
  ]
}
```

              
              
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 
- 
- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description of the procedure plan definition. | Optional | 62.0 |
| `developer​Name` | String | Developer name of the procedure plan definition. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](#). | 62.0 |
| `name` | String | Name of the procedure plan definition. | Optional | 62.0 |
| `primary​Object` | String | Source object that’s used to create a procedure with rule-based criteria. This property value must be a valid object name and must be unique in the ProcedurePlanDefinition object. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](#) and if you’re creating a procedure with rule-based criteria. | 62.0 |
| `procedurePlan​Definition​Versions` | [Procedure Plan Definition Version Input](./connect_requests_procedure_plan_definition_version_input.htm.md)[] | List of versions of a procedure plan definition. | Required | 62.0 |
| `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values are: `Billing` `DRO` `DeepClone` `ProductDiscovery` `Revenue Cloud` These values can be used based on the available license. If unspecified, the value is set to `Default`. | Required | 63.0 |
| `recordId` | String | ID of the procedure plan definition record. | Required if you’re invoking the [Procedure Plan Definition By ID API (PATCH)](./connect_resources_get_procedure_plan_definition_by_ID.htm.md). | 62.0 |

          

        
            

          

        
        
          

**Response body for POST**

          
: [Procedure Plan
              Generic](./connect_responses_procedure_plan_generic_output.htm.md)
