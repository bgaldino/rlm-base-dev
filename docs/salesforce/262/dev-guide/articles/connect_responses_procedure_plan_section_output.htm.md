---
page_id: connect_responses_procedure_plan_section_output.htm
title: Procedure Plan Section
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_section_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Section

Output representation of the details of a procedure plan section.

JSON example
:   ```
                    "procedurePlanSections": [
                  {
                     "isInherited": false,
                     "isSuccess": true,
                     "procedurePlanOptions": [
                       {
                         "expressionSetApiName": "Revenue_Mgmt_Default_Pricing_Procedure",
                         "expressionSetDefinition": "9QAZ60000004ECOOA2",
                         "expressionSetLabel": "Revenue Management Default Pricing Procedure",
                         "isSuccess": true,
                         "logic": "1 AND 2 AND 3",
                         "primaryObject": "Account",
                         "priority": 1,
                         "procedurePlanCriterion": [
                           {
                             "conditionSequence": 1,
                             "dataType": "Text",
                             "fieldObject": "BillingCountry",
                             "fieldPath": "BillingCountry",
                             "isSuccess": true,
                             "literalValue": "test",
                             "operator": "Equals",
                             "recordId": "1FiZ60000004C9cKAE"
                            },
                            {
                             "conditionSequence": 2,
                             "dataType": "Text",
                             "fieldObject": "BillingPostalCode",
                             "fieldPath": "BillingPostalCode",
                             "isSuccess": true,
                             "literalValue": "pramit",
                             "operator": "Equals",
                             "recordId": "1FiZ60000004C9dKAE"
                             },
                             {
                               "conditionSequence": 3,
                               "dataType": "Date",
                               "fieldObject": "LastActivityDate",
                               "fieldPath": "LastActivityDate",
                               "isSuccess": true,
                               "literalValue": "2024-07-14",
                               "operator": "LessThan",
                               "recordId": "1FiZ60000004C9eKAE"
                              }
                            ],
                           "recordId": "1FYZ6000000000fOAA",
                           "saveContextMapping": "AssetToSalesTransactionMapping"
                            }
                            ],
                          "recordId": "1FRZ60000008OIAOA2",
                          "resolutionType": "RuleBased",
                          "sectionType": "PricingProcedure",
                          "sequence": 1,
                          "subSectionType": "PricingProcedure"
                        }
                    ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md "Output representation of the error details related to the procedure plan definitions.")[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `isInherited` | Boolean | Indicates whether the procedure plan section is inherited from a template (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `procedure​PlanOptions` | [Procedure Plan Option](./connect_responses_procedure_plan_option_output.htm.md "Output representation of the details of a procedure plan option.")[] | List of procedure plan options. | Small, 62.0 | 62.0 |
| `recordId` | String | ID of the procedure plan option record. | Small, 62.0 | 62.0 |
| `resolution​Type` | String | Type of resolution that’s used to filter the procedure. | Small, 62.0 | 62.0 |
| `section​Type` | String | Type of section. Valid values are:   - `PricingProcedure` - `ProductDiscoveryProcedure` - `ProductQualificationProcedure` - `PricingDiscoveryProcedure` - `DiscountSpreadServiceProcedure` - `RatingProcedure` - `Custom` - `RatingDiscoveryProcedure` | Small, 62.0 | 62.0 |
| `sequence` | Integer | Sequence that’s followed for the processing of the procedures. | Small, 62.0 | 62.0 |
| `subSection​Type` | String | Subsection that’s added to the procedure plan definition. | Small, 62.0 | 62.0 |
