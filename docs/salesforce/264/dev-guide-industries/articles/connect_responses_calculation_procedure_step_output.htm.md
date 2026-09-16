---
page_id: connect_responses_calculation_procedure_step_output.htm
title: Calculation Procedure Step Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_step_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedure Step Output

Output representation of the steps of the expression set version
      record.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

#### 

              

              

            

            
              

              

              

#### 

              

              

            

            
              

              

              
- 
- 
- 
- 
- 
- 

              

              

            

          

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `calculation​MatrixId` | String | The ID of the decision matrix record. | Small, 53.0 | 53.0 |
| `childStep​Ids` | String[] | The IDs of the child steps in the parent expression set version record step. | Small, 53.0 | 53.0 |
| `conditions​ExpressionText` | String | User-defined expression text used in a condition step. | Small, 53.0 | 53.0 |
| `conditionsUi​FormattedText` | String | Additional information required to render the condition expression text. For example, when the current step has a subset of `childStepIds` that is marked to bypass. The code `"conditionsUiFormattedText":"{\"bypass\":[\"0mqx000000000f6AAA\"]}"` specified in this field enables navigation outside the branch. | Small, 53.0 | 53.0 |
| `description` | String | The description of the expression set version record step. | Small, 53.0 | 53.0 |
| `failed​Explainer​TemplateId` | String | ID of the failed explainability message template in the Decision Table lookup procedure step. | Small, 56.0 | 56.0 |
| `failed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the failed explainability message template. | Small, 59.0 | 59.0 |
| `formula​Expression​Text` | String | The formula used in a calculation step. | Small, 53.0 | 53.0 |
| `formulaUi​FormattedText` | String | Reserved for future use. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the expression set version record step. | Small, 53.0 | 53.0 |
| `inputVariables​FormatText` | String | The input variables in JSON format required to execute an expression set version record step. | Small, 53.0 | 53.0 |
| `isResult​Included` | Boolean | Indicates whether the result of a step execution is returned to the user. The default is `false`. | Small, 53.0 | 53.0 |
| `name` | String | The name of the expression set version record step. | Small, 53.0 | 53.0 |
| `noResult​Explainer​TemplateId` | String | ID of the no result explainability message template in the Decision Table lookup procedure step. | Small, 59.0 | 59.0 |
| `noResult​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the no result explainability message template. | Small, 59.0 | 59.0 |
| `output​Variables​FormatText` | String | The output variables in JSON format returned by an expression set version record step. | Small, 53.0 | 53.0 |
| `output​Variables​MappingText` | String | The mapping between the output variable of a step and the input variable for a sub-calculation procedure version record or a sub-decision matrix record. | Small, 53.0 | 53.0 |
| `passed​Explainer​TemplateId` | String | ID of the passed explainability message template in the Decision Table lookup procedure step. | Small, 56.0 | 56.0 |
| `passed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect_responses_expression_set_des_token_mapping.htm.md) | List of the token resource mappings of the passed explainability message template. | Small, 59.0 | 59.0 |
| `reference​Calculation​ProcedureId` | String | The ID of the sub-calculation procedure version record. | Small, 53.0 | 53.0 |
| `return​Message​ValueSet` | String | User-configured messages for the result of the current step. Note This field is applicable when the step type is `Condition`. | Small, 53.0 | 53.0 |
| `stage` | String | Indicates whether the expression set version step is a calculation or an aggregation. Note In version 53.0 and later, only calculation is supported. | Small, 53.0 | 53.0 |
| `stepType` | String | Indicates whether the expression set version step type is mathematical or lookup. Possible values are: Condition Calculation MatrixLookup ReferenceProcedure Branch ConditionalGroup | Small, 53.0 | 53.0 |
