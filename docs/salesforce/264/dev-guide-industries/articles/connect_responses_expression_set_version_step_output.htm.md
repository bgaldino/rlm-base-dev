---
page_id: connect_responses_expression_set_version_step_output.htm
title: Expression Set Version Step
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_version_step_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Version Step

Output representation of a step in an expression set
    version.

                        
                            

                            

                            

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                        
                            

                            

                            

- 
- 
- 
- 
- 
- 

                            

                            

                        

                        
                            

                            

                            

                            

                            

                        

                    

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `action​Type` | String | Business Knowledge Model of the expression set.Valid values are: `AiAccelerator​SubscriberChurn​Prediction` `AssignBadge​ToMember` `AssignParameter​Values` `Automated​Claims​Processing​Validation` `BreAggregator` `BreAggregator​Assignment` `ChangeMember​Tier` `CheckMember​BadgeAssignment` `CreditPoints` `Crud` `DebitPoints` `Evaluate​Qualification` `Evaluate​Disqualification` `GetMember​Attributes​Values` `GetMember​PointBalance` `GetMember​Promotions` `GetMemberTier` `GetOutputs​FromDecision​Matrix` `GetOutputs​FromDecision​Table` `GetUser​Data` `IncreaseUsage​ForCumulative​Promotion` `IssueVoucher` `List​Group​Calculation` `PriceList` `RecordAlert` `Redeem​Voucher` `Redeem​Voucher` `RunFlow` `RunProgram​Process` `SampleBusiness​ElementWith​Context` `SampleDynamic​Custom​Element` `SendMail` `TestCustom​Element` `UpdateCurrent​ValueFor​MemberAttribute` `UpdatePoint​Balance` `UpdateUsage​ForCumulative​Promotion` `VolumeDiscount` | Small, 58.0 | 58.0 |
| `advanced​Condition` | [Expression Set Advanced Condition Step](./connect_responses_expression_set_advanced_condition_step_output.htm.md) | Details of the advanced condition in case of an advanced condition step. | Small, 58.0 | 58.0 |
| `aggregation` | [Expression Set Aggregation Step](./connect_responses_expression_set_aggregation_step_output.htm.md) | Details of the aggregation step in case of an aggregation step. | Small, 58.0 | 58.0 |
| `assignment` | [Expression Set Assignment Step](./connect_responses_expression_set_assignment_step_output.htm.md) | Details of the assignment step in case of an assignment step. | Small, 58.0 | 58.0 |
| `condition​Expression` | [Expression Set Condition Expression Step](./connect_responses_expression_set_condition_expression_step_output.htm.md) | Details of the condition step in case of a condition step. | Small, 58.0 | 58.0 |
| `custom​Element` | [Expression Set Custom Element Step](./connect_responses_expression_set_custom_element_step_output.htm.md) | Details of the custom element step in case of a custom element step. | Small, 58.0 | 58.0 |
| `description` | String | Description of the step in expression set version. | Small, 58.0 | 58.0 |
| `failed​Explainer​Template` | String | Name of the failed explainability message template. | Small, 58.0 | 58.0 |
| `failed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the failed explainability message template. | Optional | 59.0 |
| `lookup​Table` | [Expression Set Lookup Table Step](./connect_responses_expression_set_lookup_table_step_output.htm.md) | Details of the lookup table in case of a decision matrix or decision table step. | Small, 58.0 | 58.0 |
| `name` | String | Unique name of the step in expression set version. | Small, 58.0 | 58.0 |
| `noResult​Explainer​Template` | String | Name of the explainability message template that’s used when the evaluation result of the selected element type is No Result. This field is applicable for a Decision Table only. | Small, 59.0 | 59.0 |
| `noResult​MessageToken​Mappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the no result explainability message template. | Small, 59.0 | 59.0 |
| `parent​Step` | String | Unique name of the parent step of this step in the expression set version. | Small, 58.0 | 58.0 |
| `passed​Explainer​Template` | String | Name of the passed explainability message template. | Small, 58.0 | 58.0 |
| `passed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the passed explainability message template. | Small, 59.0 | 59.0 |
| `result​Included` | Boolean | Indicates whether to include the step output in the expression set result (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `sequence​Number` | Integer | Sequence number of the step in the expression set version. | Small, 58.0 | 58.0 |
| `shouldExpose​Condition​Details` | Boolean | Indicates whether the decision explanation includes the condition details (`true`) or not (`false`) for the condition element type. | Small, 58.0 | 58.0 |
| `should​ExposeExec​PathMsg​Only` | Boolean | Indicates whether the decision explanation includes details of the executed path only (`true`) or not (`false`) for the branch element type. | Small, 58.0 | 58.0 |
| `should​ShowExpl​Externally` | Boolean | Indicates whether the decision explanation is exposed to community users for the step (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `step​Type` | String | Step type of the expression set.Valid values are: `Advanced​Condition` `Branch` `Business​Knowledge​Model` `Condition` `DefaultPath` `SubExpression` | Small, 58.0 | 58.0 |
| `sub​Expression` | [Expression Set SubExpression Step](./connect_responses_expression_set_sub_expression_step_output.htm.md) | Details of the subexpression set in case of a subexpression step. | Small, 58.0 | 58.0 |
