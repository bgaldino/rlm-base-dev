---
page_id: connect_responses_message_templates_list_output.htm
title: Message Templates List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_message_templates_list_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Message Templates List

Output representation of the list of explainability message
      templates.

      
        
          

**JSON example**

          
: 
            

```
{
  "messageTemplates" : [ {
    "expressionSetStepType" : "Branch",
    "id" : "8U8x00000000027CAA",
    "isDefault" : true,
    "message" : "This is Branch Passing Message",
    "name" : "BranchMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "Calculation",
    "id" : "8U8x00000000022CAA",
    "isDefault" : true,
    "message" : "CalcMessageTemplate PASS",
    "name" : "CalcMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "Condition",
    "id" : "8U8x0000000002CCAQ",
    "isDefault" : false,
    "message" : "This is Condition Passing Message",
    "name" : "ConditionMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "MatrixLookup",
    "id" : "8U8x0000000002HCAQ",
    "isDefault" : true,
    "message" : "This is DM passing message",
    "name" : "DMMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "ReferenceProcedure",
    "id" : "8U8x0000000002MCAQ",
    "isDefault" : true,
    "message" : "This is SubExpression Passing Message",
    "name" : "SubExpressionMessageTemplate",
    "resultType" : "Passed"
  } ]
}

```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The API response code when there’s a failure in retrieving the list of explainability message templates. | Small, 56.0 | 56.0 |
| `isSuccess` | Boolean | Identifies whether the request is successful (`true`) or not (`false`). | Small, 56.0 | 56.0 |
| `message` | String | The error message when there’s a failure in retrieving the list of explainability message templates. | Small, 56.0 | 56.0 |
| `message​Templates` | [Message Template Detail](./connect_responses_message_template_detail_output.htm.md) [] | The list of explainability message templates. | Small, 56.0 | 56.0 |
