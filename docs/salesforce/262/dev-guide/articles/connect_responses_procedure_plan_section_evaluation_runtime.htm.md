---
page_id: connect_responses_procedure_plan_section_evaluation_runtime.htm
title: Procedure Plan Section Evaluation Runtime
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_section_evaluation_runtime.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Section Evaluation Runtime

Output representation of the results from the procedure plan evaluation.

JSON example
:   ```
                    "procedurePlanSections": [
                        {
                            "expressionSetApiName": "pricingProcedure_usageType_3",
                            "expressionSetDefinitionId": "9QAZ60000004Ef6OAE",
                            "expressionSetLabel": "pricingProcedure_usageType_3",
                            "sectionType": "PricingProcedure",
                            "sequence": 1,
                            "subSectionType": "Section1",
                            "usageType": "DefaultPricing"
                        },
                        {
                            "expressionSetApiName": "productQualification_usageType_3",
                            "expressionSetDefinitionId": "9QAZ60000004EfFOAU",
                            "expressionSetLabel": "productQualification_usageType_3",
                            "sectionType": "ProductQualificationProcedure",
                            "sequence": 3,
                            "subSectionType": "Section2",
                            "usageType": "ProductQualification"
                        },
                        {
                            "expressionSetApiName": "rating_usageType_2",
                            "expressionSetDefinitionId": "9QAZ60000004EfHOAU",
                            "expressionSetLabel": "rating_usageType_2",
                            "sectionType": "RatingProcedure",
                            "sequence": 2,
                            "subSectionType": "Section3",
                            "usageType": "DefaultRating"
                        }
                    ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `expression​SetApi​Name` | String | API name of the expression set. | Small, 62.0 | 62.0 |
| `expressionSet​Definition​Id` | String | ID of the expression set definition. | Small, 62.0 | 62.0 |
| `expression​SetLabel` | String | Label of the expression set. | Small, 62.0 | 62.0 |
| `readContext​Mapping` | String | Mapping that’s used to read data from the mapped object and populate the context definition. | Small, 62.0 | 62.0 |
| `saveContext​Mapping` | String | Mapping that’s used to save data from the context definition and populate the mapped object. | Small, 62.0 | 62.0 |
| `sectionType` | String | Name of the evaluated section. Valid values are:   - `PricingProcedure` - `ProductDiscoveryProcedure` - `ProductQualificationProcedure` - `PricingDiscoveryProcedure` - `DiscountSpreadServiceProcedure` - `RatingProcedure` - `Custom` - `RatingDiscoveryProcedure` | Small, 62.0 | 62.0 |
| `sequence` | Integer | Sequence that’s followed for the processing of the procedures. | Small, 62.0 | 62.0 |
| `subSection​Type` | String | Name of the evaluated subsection. | Small, 62.0 | 62.0 |
| `usageType` | String | Usage type of the procedure. | Small, 62.0 | 62.0 |
