---
page_id: connect_resources_get_procedure_plan_definition_records.htm
title: Procedure Plan Definitions (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_procedure_plan_definition_records.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-09-29
---

# Procedure Plan Definitions (GET, POST)

Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition.

    

## Resource

      
      

```
/connect/procedure-plan-definitions
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com​/services/data​/v68.0/connect/​procedure-plan-definitions?​isTemplate=true
```

    

    

## Available Version

      
      

62.0

    

    

## HTTP Methods

      
      

GET, POST

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isTemplate` | Boolean | Indicates whether to return a list of file-based definitions (`true`) or not (`false`). This API request returns a list of database-based definitions, by default. | Optional | 62.0 |

    

    

## Response Body for GET

      
      

[Procedure Plan Definitions](./connect_responses_procedure_plan_definitions_output.htm.md)

    

    

## Request Body for POST

      
      

**JSON Example**

      

This example shows a sample request to create a procedure plan definition record by using the Procedure Plan Definitions (POST) API.

      

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

    

    

## Response Body for POST

      
      

[Procedure Plan Generic](./connect_responses_procedure_plan_generic_output.htm.md)
