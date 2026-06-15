---
page_id: connect_resources_create_procedure_plan_version_record.htm
title: Procedure Plan Version (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_procedure_plan_version_record.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Procedure Plan Version (POST)

Create records of a procedure plan version with
details.

Resource
:   ```
    /connect/procedure-plan-definitions/procedurePlanDefinitionId/version
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com​/services/data​/v67.0/connect/​procedure-plan-definitions​/1FNxx0000004EsOGAU/​version
    ```

Available version
:   62.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "active": false,
          "developerName": "sample_version_input",
          "effectiveFrom": "2024-07-09T00:00:00.000Z",
          "contextDefinition": "SalesTransactionContext__stdctx",
          "procedurePlanSections": [
            {
              "isInherited": false,
              "procedurePlanOptions": [
                {
                  "saveContextMapping": "AssetToSalesTransactionMapping",
                  "expressionSetDefinition": "9QAZ60000004ECOOA2",
                  "expressionSetLabel": "Revenue_Default_Pricing_Procedure",
                  "expressionSetApiName": "Revenue Default Pricing Procedure",
                  "logic": "1 AND 2 AND 3",
                  "priority": 1,
                  "procedurePlanCriterion": [
                    {
                      "conditionSequence": 1,
                      "fieldObject": "BillingCountry",
                      "fieldPath": "BillingCountry",
                      "literalValue": "test",
                      "operator": "Equals",
                      "dataType": "Text"
                    },
                    {
                      "conditionSequence": 2,
                      "fieldObject": "BillingPostalCode",
                      "fieldPath": "BillingPostalCode",
                      "literalValue": "sample",
                      "operator": "Equals",
                      "dataType": "Text"
                    },
                    {
                      "conditionSequence": 3,
                      "fieldObject": "LastActivityDate",
                      "fieldPath": "LastActivityDate",
                      "literalValue": "2024-07-14",
                      "operator": "LessThan",
                      "dataType": "Date"
                    }
                  ]
                }
              ],
              "resolutionType": "RuleBased",
              "sectionType": "PricingProcedure",
              "sequence": 1,
              "subSectionType": "PricingProcedure",
              "recordId": "1FRZ60000008OIAOA2"
            }
          ],
          "rank": 1,
          "readContextMapping": "ProductDiscoveryContextMapping",
          "saveContextMapping": "OrderEntitiesMapping"
        }
        ```

        ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

        #### Note

        The properties that aren’t specified in the input are deleted when updating the
        record.

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `active` | Boolean | Indicates whether this procedure plan definition version is active (`true`) or not (`false`). You can’t edit or delete a procedure plan version that’s in the active state. | Required | 62.0 |
        | `context​Definition` | String | Context definition that’s associated with the procedure plan definition version record. | Required | 62.0 |
        | `developer​Name` | String | Unique developer name of the procedure plan definition version. | Required | 62.0 |
        | `effective​From` | String | Date and time from when the procedure plan definition version comes into effect. | Required | 62.0 |
        | `effective​To` | String | Date and time from when the procedure plan definition version is no longer in effect. | Required | 62.0 |
        | `inherited​From` | String | Template this procedure plan definition version is created from. | This property is read-only. | 62.0 |
        | `procedure​PlanSections` | [Procedure Plan Section Input](./connect_requests_procedure_plan_section_input.htm.md "Input representation of the details of a procedure plan section.")[] | Procedure setup sections for a procedure plan definition. Each section enables the setup of a procedure type by using a rule-based criteria.  Keep these considerations in mind when you modify this property.   - You can edit or delete a procedure plan section if it isn’t associated   with an active procedure plan version. - You can create a procedure plan section with rule-based resolution type   if the primary object isn’t empty in the definition. | Required | 62.0 |
        | `rank` | Integer | Current rank of the procedure plan definition version that’s used to decide the sequence of execution of a procedure plan definition version. | Required | 62.0 |
        | `readContext​Mapping` | String | Mapping that’s used to read data from the mapped object and populate the context definition.  This property value must be associated with a context definition. | Optional | 62.0 |
        | `recordId` | String | ID of the procedure plan definition version record. | Required | 62.0 |
        | `saveContext​Mapping` | String | Mapping that’s used to save data from the context definition and populate the mapped object.  This property value must be associated with a context definition. | Optional | 62.0 |
        | `status` | String | Status of the procedure plan definition version record. | Optional | 62.0 |

Response body for POST
:   [Procedure Plan
    Generic](./connect_responses_procedure_plan_generic_output.htm.md "Output representation of the details of the created procedure plan definition record.")
