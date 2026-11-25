---
page_id: connect-requests-expression-set-version-step
title: Expression Set Version Step Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-version-step.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_version_step.htm
fetched_at: 2026-11-25
---

# Expression Set Version Step Input

Input representation of a step in an expression set version.

## Root XML tag

`<ExpressionSetVersionStepInput>`

## JSON Example

```
"steps": [
            {
              "actionType": null,
              "advancedCondition": null,
              "aggregation": null,
              "assignment": null,
              "conditionExpression": {
                "expression": "productName == 'iPhone' && City == 'Los Angeles'",
                "resultParameter": "condition_output__1"
              },
              "customElement": null,
              "lookupTable": null,
              "description": "Condition step for conditions w.r.t product",
              "failedExplainerTemplate": "FailureTemplate",
              "failedMessageTokenMappings": [
              {
              "expressionSetMessageToken": "model",
              "resourceReference": "Model"
              }],
              "name": "Condition1",
              "noResultExplainerTemplate": "NoResultTemplate",
              "noResultMessageTokenMappings": [
              {
              "expressionSetMessageToken": "year",
              "resourceReference": "Year"
              }],
              "parentStep": null,
              "passedExplainerTemplate": "SuccessTemplate",
              "passedMessageTokenMappings": [
              {
              "expressionSetMessageToken": "price",
              "resourceReference": "DM1__Price"
              }],
              "resultIncluded": true,
              "sequenceNumber": 1,
              "shouldExposeExecPathMsgOnly": false,
              "shouldExposeConditionDetails": false,
              "shouldShowExplExternally": false,
              "stepType": "Condition",
              "subExpression": null
            }
          ]
```

## Properties

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
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action​Type` | String | Business Knowledge Model of the expression set. Valid values are: `AiAccelerator​SubscriberChurn​Prediction``AssignBadge​ToMember``AssignParameter​Values``Automated​Claims​Processing​Validation``BreAggregator``BreAggregator​Assignment``ChangeMember​Tier``CheckMember​BadgeAssignment``CreditPoints``Crud``DebitPoints``Evaluate​Qualification``Evaluate​Disqualification``GetMember​Attributes​Values``GetMember​PointBalance``GetMember​Promotions``GetMemberTier``GetOutputs​FromDecision​Matrix``GetOutputs​FromDecision​Table``GetUser​Data``IncreaseUsage​ForCumulative​Promotion``IssueVoucher``List​Group​Calculation``PriceAdjustmentMatrix``PriceList``RecordAlert``Redeem​Voucher``RunFlow``RunProgram​Process``SampleBusiness​ElementWith​Context``SampleDynamic​Custom​Element``SendMail``TestCustom​Element``UpdateCurrent​ValueFor​MemberAttribute``UpdatePoint​Balance``UpdateUsage​ForCumulative​Promotion``VolumeDiscount` | Optional | 58.0 |
| `advanced​Condition` | [Expression Set Advanced Condition Step Input](./connect-requests-expression-set-advanced-condition-step.md) | Details of the advanced condition if the step is an advanced condition step. | Optional | 58.0 |
| `aggregation` | [Expression Set Aggregation Step Input](./connect-requests-expression-set-aggregation-step.md) | Aggregation details if the step is an aggregation step. | Optional | 58.0 |
| `assignment` | [Expression Set Assignment Step Input](./connect-requests-expression-set-assignment-step.md) | Assignment details if the step is an assignment step. | Optional | 58.0 |
| `condition​Expression` | [Expression Set Condition Expression Step Input](./connect-requests-expression-set-condition-expression-step.md) | Details of the condition if the step is a condition step. | Optional | 58.0 |
| `custom​Element` | [Expression Set Custom Element Step Input](./connect-requests-expression-set-custom-element-step.md) | Details of the custom element if the step is a custom element step. | Optional | 58.0 |
| `description` | String | Description of the step. | Optional | 58.0 |
| `failed​Explainer​Template` | String | Name of the failed explainability message template. | Optional | 58.0 |
| `failed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect-requests-expression-set-des-token-mapping.md) | List of the token resource mappings of the failed explainability message template. | Optional | 59.0 |
| `lookup​Table` | [Expression Set Lookup Table Step Input](./connect-requests-expression-set-lookup-table-step.md) | Details of the lookup table for a decision matrix or decision table step. | Optional | 58.0 |
| `name` | String | Unique name of the step in the expression set version. | Required | 58.0 |
| `noResult​Explainer​Template` | String | Name of the explainability message template that’s used when the evaluation result of the selected element type is No Result. This field is applicable for a Decision Table only. | Optional | 59.0 |
| `noResult​MessageToken​Mappings` | [Expression Set DES Token Mapping](./connect-requests-expression-set-des-token-mapping.md) | List of the token resource mappings of the no result explainability message template. | Optional | 59.0 |
| `parent​Step` | String | Unique name of the parent step in the expression set version. | Optional | 58.0 |
| `passed​Explainer​Template` | String | Name of the passed explainability message template. | Optional | 58.0 |
| `passed​Message​TokenMappings` | [Expression Set DES Token Mapping](./connect-requests-expression-set-des-token-mapping.md) | List of the token resource mappings of the passed explainability message template. | Optional | 59.0 |
| `result​Included` | Boolean | Indicates whether to include the step output in the expression set result (`true`) or not (`false`). | Optional | 58.0 |
| `sequence​Number` | Integer | Sequence number of the step in the expression set version. | Required | 58.0 |
| `shouldExpose​ExecPathMsg​Only` | Boolean | Indicates whether the decision explanation includes information about the executed path only (`true`) or not (`false`) for the Branch element type. | Optional | 58.0 |
| `should​ExposeCondition​Details` | Boolean | Indicates whether the decision explanation includes the condition details (`true`) or not (`false`) for the Condition element type. | Optional | 58.0 |
| `shouldShow​Expl​Externally` | Boolean | Indicates whether the decision explanation is exposed to community users for the step (`true`) or not (`false`). | Optional | 58.0 |
| `step​Type` | String | Step type of the expression set. Valid values are: `Advanced​Condition``Advanced​ListFilter`—Available in version 59.0 and later.`Branch``Business​Knowledge​Model``Condition``DefaultPath``ListFilter`—Available in version 59.0 and later.`ListGroup`—Available in version 59.0 and later.`SubExpression` | Required | 58.0 |
| `sub​Expression` | [Expression Set Sub Expression Step Input](./connect-requests-expression-set-sub-expression-step.md) | Details of the subexpression if the step is a subexpression step. | Optional | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-version-step.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
