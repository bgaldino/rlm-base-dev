---
page_id: connect_responses_procedure_plan_definitions_output.htm
title: Procedure Plan Definitions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_definitions_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Procedure Plan Definitions

Output representation of the details of procedure plan definitions.

        
          

**JSON example**

          
: 
            

```
{
            "isSuccess": true,
            "procedurePlanDefinitions": [
                {
                    "description": "test description",
                    "developerName": "sample_test",
                    "name": "sample_test",
                    "primaryObject": "Account",
                    "procedurePlanDefinitionVersions": [
                        {
                            "active": false,
                            "developerName": "sample_test",
                            "effectiveFrom": "2024-07-09T00:00:00.000Z",
                            "contextDefinition": "SalesTransactionContext__stdctx",
                            "procedurePlanSections": [],
                            "rank": 1,
                            "readContextMapping": "ProductDiscoveryContextMapping",
                            "recordId": "1CvZ60000008OIaKAM",
                            "success": true
                        }
                    ],
                    "recordId": "1FNZ60000004CAHOA2",
                    "success": true
                },
                {
                    "developerName": "PriceAdjustmentSchedule",
                    "name": "PriceAdjustmentSchedule",
                    "primaryObject": "PriceAdjustmentSchedule",
                    "procedurePlanDefinitionVersions": [
                        {
                            "active": false,
                            "developerName": "PriceAdjustmentSchedule",
                            "effectiveFrom": "2024-07-10T00:00:00.000Z",
                            "contextDefinition": "SalesTransactionContext__stdctx",
                            "procedurePlanSections": [],
                            "rank": 1,
                            "recordId": "1CvZ6000000CaRbKAK",
                            "success": true
                        }
                    ],
                    "recordId": "1FNZ6000000CaSAOA0",
                    "success": true
                }
                ]
            }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md)[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `procedure​PlanDefinitions` | [Procedure Plan Definition](./connect_responses_procedure_plan_definition_output.htm.md)[] | Details of a single procedure plan definition. | Small, 62.0 | 62.0 |
