---
page_id: meta_expressionsetdefinition.htm
title: ExpressionSetDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_expressionsetdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetDefinition

Represents an expression set definition.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Before deploying an expression set or an expression set version to a target org, review
these [Expression Set Migration Considerations](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US "HTML (New Window)").

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

ExpressionSetDefinition components have the suffix
.expressionSetDefinition and are stored in the
expressionSetDefinition folder.

## Version

ExpressionSetDefinition components are available in API version 55.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
|  |  |
| description | Field Type  string  Description  The description of an expression set definition. |
| executionMode | Field Type  ExpsSetExecutionMode (enumeration of type string)  Description  Specifies the execution mode for the expression set definition. Valid values are:   - `Cloud` - `Local` |
| executionScale | Field Type  ExpsSetExecutionScale (enumeration of type string)  Description  Specifies the scale of the inputs that an expression set processes. The scale determines where the expression set is executed. Valid values are:   - `High` - `Low`  Available in API version 61.0 and later. |
| interfaceSource​Type | Field Type  ExpsSetInterfaceSourceType (enumeration of type string)  Description  The interface source type designed by the consuming cloud that's making a customized expression set builder available to its users.  Valid values are:  - `Bre` - `Constraint` (Available in API version 62.0 and   later). - `DiscoveryProcedure` (Available in API version   61.0 and later). - `EventOrchestration` (Available in API version   61.0 and later). - `GpaCalculationProcedure` (Available in API   version 67.0 and later). - `IntelligentDecisionStudio` (Available in API   version 67.0 and later). - `ItServiceManagement` (Available in API   version 65.0 and later). - `PricingProcedure` - `QualificationProcedure` - `RatingDiscoveryProcedure` (Available in API   version 61.0 and later). - `RatingProcedure` (Available in API version 67.0   and later). - `Sample`  Available in API version 59.0 and later. |
| label | Field Type  string  Description  Required.  The UI label of an expression set definition. |
| processType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  The process type that uses the expression set rule.  Valid values are:  - `AssetRefreshEligibility`—Available in API   version 67.0 and later. - `Bre` - `GpaCalculation` - `InsuranceClaimProcessing`—Available in   API version 65.0 and later. - `ItServiceManagement`—Available in API   version 65.0 and later. - `PlanCostCalculation` - `Program`—Available in API version 67.0   and later. - `RatingDiscovery` - `StockRotation`—Available in API version   67.0 and later. - `StudentInformationSystem`—Available in   API version 65.0 and later. - `StudentSuccess`  When Business Rules Engine is enabled for a Salesforce instance, the default value is `Bre`. Other process types are available to you depending on your industry solution and permission sets. |
| resource​InitializationType | Field Type  ResourceInitializationType (enumeration of type string)  Description  Indicates whether the initial value of expression set variables and context tags is null or a default value.  Valid values are:  - `Default` - `Off`  Available in API version 64.0 and later. |
| template | Field Type  boolean  Description  Defines whether an expression set is a template or not. |
| type | Field Type  ExpsSetType (enumeration of type string)  Description  The type of the expression set definition. Valid values are:   - `Custom` - `Standard` |
| usageSubType | Field Type  ExpsSetUsageSubType (enumeration of type string)  Description  The subtype of the industry that's using the expression set definition. If no value is specified, the field defaults to null. |
| versions | Field Type  [ExpressionSetDefinitionVersion](#ExpSetDefVer)[]  Description  Represents an array of expression set version definitions in an expression set. This array must contain at least one version. |

## ExpressionSetDefinitionVersion​​

Represents a definition of an expression set version.

| Field Name | Description |
| --- | --- |
| decimalScale | Field Type  integer  Description  Number of decimal places to be used in the results of calculation steps that involve context variables. |
| description | Field Type  string  Description  Describes the version of an expression set definition. |
| endDate | Field Type  dateTime  Description  The date until which the expression set definition is available for use. |
| expressionSet​Definition | Field Type  string  Description  The full name of an expression set definition. |
| interface​SourceType | Field Type  ExpsSetInterfaceSourceType (enumeration of type string)  Description  The interface source type designed by the consuming cloud that's making a customized expression set builder available to its users.  Valid values are:  - `Bre` - `Constraint` - `DiscoveryProcedure` - `EventOrchestration` - `GpaCalculationProcedure` - `IntelligentDecisionStudio` - `ItServiceManagement` - `PricingProcedure` - `QualificationProcedure` - `RatingDiscoveryProcedure` - `RatingProcedure` - `Sample`  Available in API version 67.0 and later. |
| label | Field Type  string  Description  Required.  The UI label of an expression set definition. |
| processType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  The process type that uses the expression set rule. Available in API version 67.0 and later. |
| rank | Field Type  int  Description  The rank of the Expression Set Definition Version. When more than one enabled version matches an expression set call, and the start date time to end date time spans overlap, the version with the highest rank is chosen. Available in API version 62.0 and later. |
| shouldShow​ExplExternally | Field Type  boolean  Description  Indicates whether the decision explanation is exposed to external users (`true`) or not (`false`). The default value is `false`. Available in API version 56.0 and later. |
| startDate | Field Type  dateTime  Description  Required.  The date from when the expression set definition is available for use. |
| status | Field Type  ExpsSetStatus (enumeration of type string)  Description  Required.  The status of an expression set definition.  Valid values are:  - `Active` - `Draft` - `Inactive` - `InvalidDraft` - `Obsolete` |
| steps | Field Type  [ExpressionSetStep](#ExpSetStep)[]  Description  Represents an array of steps created in an expression set version. |
| uiTier | Field Type  boolean  Description  Indicates whether the API call originated from the design time builder or a package. Note Note This field is for internal use only. |
| variables | Field Type  [ExpressionSet​​Variable](#ExpSetVar)[]  Description  Represents an array of variables in an expression set version. |
| versionNumber | Field Type  int  Description  Required.  The version number of an expression set definition. |

## ExpressionSet​​Step

Represents a step in an expression set version.

| Field Name | Description |
| --- | --- |
| actionType | Field Type  BusinessKnowledgeModel (enumeration of type string)  Description  Specifies the type of action this step executes. Valid values are:   - `AiAcceleratorSubscriberChurnPrediction` - `ApexAction` - `ApexListAction` (Available in API version   64.0 and later.) - `AssetDiscovery` - `AssignBadgeToMember` - `AssignParameterValues` - `AssignmentElement` - `AssignmentRuleCustomQueue` (Available in   API version 65.0 and later.) - `AssignmentRuleCustomUser` (Available in   API version 65.0 and later.) - `AteprlRecordCreator` (Available in API   version 65.0 and later.) - `AttributeAdjustmentMatrix` - `AttributeDiscount` - `AutomatedClaimsProcessingValidation` - `BaseRate` - `BindingObjectRateAdjustmentResolution`   (Available in API version 64.0 and later.) - `BindingObjectRateCardEntryResolution`   (Available in API version 64.0 and later.) - `BreAggregator` - `BreAggregatorAssignment` - `BreakdownLineMapping` (Available in API   version 64.0 and later.) - `BundleDiscount` - `CalculateQuantity` (Available in API   version 64.0 and later.) - `ChangeMemberTier` - `CheckMemberBadgeAssignment` - `CommercePricing` (Available in API version 62.0   and later.) - `CommitmentAdjustment` (Available in API   version 65.0 and later.) - `ComplianceCheck` - `ComplianceControlLog` (Available in API version   62.0 and later.) - `Constraint`   (Available in API version 64.0 and later.) - `CreditPoints` - `Crud` - `DebitPoints` - `DerivedPricing` - `DiscountDistributionService` - `DiscoverySettings` (Available in API   version 64.0 and later.) - `DynamicRulesExecutor` (Available in API   version 65.0 and later.) - `EvaluateCategoryDisqualification` (Available in   API version 62.0 and later.) - `EvaluateCategoryQualification` (Available in API   version 62.0 and later.) - `EvaluateDisqualification` - `EvaluateQualification` - `FormulaBasedPricing` - `FormulaBasedRating` (Available in API version   62.0 and later.) - `GetCustomerPromotionAttrValue` (Available   in API version 64.0 and later.) - `GetMemberAttributesValues` - `GetMemberPartnerLinkageStatus` - `GetMemberPointBalance` - `GetMemberPromotions` - `GetMemberTier` - `GetOutputsFromDecisionMatrix` - `GetOutputsFromDecisionTable` - `GetUserData` - `GroupingAndAggregatePricing` - `GroupingAndAggregateRating` (Available in API   version 62.0 and later.) - `IncreaseUsageForCumulativePromotion` - `IntegrationOrchestration` - `InterNodeDataCopy` - `IssueExtendedReward` (Available in API   version 64.0 and later.) - `IssueVoucher` - `ListGroup` - `ListGroupCalculation` - `ListPrice` - `ManualDiscount` - `ManualRatingDiscount` (Available in API version   62.0 and later.) - `MapProduct` - `MinimumPrice` (Available in API version 62.0 and   later.) - `MultiRecipientProductQualification`   (Available in API version 64.0 and later.) - `NegotiatedBaseRate` (Available in API   version 64.0 and later.) - `NegotiatedRateCardEntryResolution`   (Available in API version 64.0 and later.) - `NegotiatedTierAdjustment` (Available in   API version 64.0 and later.) - `NegotiatedVolumeAdjustment` (Available in   API version 64.0 and later.) - `PredictiveAI` - `PriceAdjustmentMatrix` - `PriceGuidance` (Available in API version   64.0 and later.) - `PriceRevision` (Available in API version   65.0 and later.) - `PricingPropagation` (Available in API   version 65.0 and later.) - `PricingSettings` - `PromotionExecution` (Available in API   version 65.0 and later.) - `PromotionsDiscount` - `Proration` - `RateAdjustmentByAttributeResolution` (Available   in API version 62.0 and later.) - `RateAdjustmentByTierResolution` (Available in   API version 62.0 and later.) - `RateAdjustmentMatrix` (Available in API version   62.0 and later.) - `RateAssignment` (Available in API version 62.0   and later.) - `RateCardEntryResolution` (Available in API   version 62.0 and later.) - `RateCardResolution` (Available in API version   62.0 and later.) - `RatingAttributeDiscount` - `RatingBreakdownLineMapping` (Available in   API version 65.0 and later.) - `RatingRoundingValues` (Available in API version   62.0 and later.) - `RatingSetting` - `RatingTierDiscount` - `RatingVolumeDiscount` - `RecordAction` - `RecordAlert` - `RedeemVoucher` - `RoundingValues` - `RuleFetch` - `RunFlow` - `RunProgramProcess` - `SampleBusinessElementWithContext` - `SampleCustomElementWithExpressionAndListFilter` - `SampleDynamicCustomElement` - `SampleJavaBasedTaxCalculatorCustomElement` - `SampleTaxCalculatorCustomElement` - `SendMail` - `StopPricing` - `StopRating` (Available in API version 62.0 and   later.) - `SubscriptionPricing` - `TermGpaCalculation` (Available in API   version 64.0 and later.) - `TermGpaReporting` (Available in API   version 64.0 and later.) - `TestCustomElement` - `UpdateCurrentValueForMemberAttribute` - `UpdateCustomerPromotionAttrValue`   (Available in API version 64.0 and later.) - `UpdatePointBalance` - `UpdateUsageForCumulativePromotion` - `UpsertRecord`   (Available in API version 64.0 and later.) - `VolumeDiscount` - `VolumeTierDiscount` |
| advancedCondition | Field Type  [ExpressionSetAdvancedCondition](#ExpSetAdvCon)  Description  Represents an advanced condition step. |
| aggregation | Field Type  [ExpressionSetAggregation](#ExpSetAggregate)  Description  Represents an aggregation step. |
| assignment | Field Type  [ExpressionSetAssignment](#ExpSetAssignment)  Description  Represents an assignment step. |
| conditionExpression | Field Type  [ExpressionSetConditionExpression](#ExpSetConExp)  Description  Represents a condition step. |
| customElement | Field Type  [ExpressionSetCustomElement](#ExpSetCustomElement)  Description  Represents a custom element step that contains the input and output mappings. Available in API version 56.0 and later. |
| decisionTable | Field Type  [ExpressionSetDecisionTable](#ExpSetDecisionTbl)  Description  Represents a decision matrix or decision table step. |
| description | Field Type  string  Description  Describes an expression set definition version step. |
| failed​ExplainerTemplate | Field Type  string  Description  The explainability message template that’s used when the result type of a condition step in an expression set is Failed. |
| failedMessage​TokenMappings | Field Type  ExplainabilityMessageTemplateTokenMapping (enumeration of type string)  Description  List of the token resource mappings of the failed explainability message template. Valid values are:   - `expressionSetMessageToken` - `resourceReference`   Available in API version 59.0 and later. |
| hasNested​Explainability | Field Type  boolean  Description  Indicates whether the step has nested explainability ( ``` true ``` ) or not ( ``` false ``` ). Available in API version 67.0 and later. |
| label | Field Type  string  Description  Required.  The UI label of an expression set definition version step. |
| name | Field Type  string  Description  Required.  The full name of an expression set definition version step. |
| noResult​ExplainerTemplate | Field Type  string  Description  The explainability message template that’s used when the result type of a condition step in an expression set is No Result. Available in API version 59.0 and later. |
| noResultMessage​TokenMappings | Field Type  ExplainabilityMessageTemplateTokenMapping (enumeration of type string)  Description  List of the token resource mappings of the no result explainability message template. Valid values are:   - `expressionSetMessageToken` - `resourceReference`   Available in API version 59.0 and later. |
| parentStep | Field Type  string  Description  The name of the parent step in an expression set definition version that’s associated with a step. |
| passedExplainer​Template | Field Type  string  Description  The explainability message template that’s used when the result type of a condition step in an expression set is Passed. |
| passedMessage​TokenMappings | Field Type  ExplainabilityMessageTemplateTokenMapping (enumeration of type string)  Description  List of the token resource mappings of the passed explainability message template. Valid values are:   - `expressionSetMessageToken` - `resourceReference`   Available in API version 59.0 and later. |
| resultIncluded | Field Type  boolean  Description  Indicates whether the step output must be included in the expression result (true) or not (false). |
| sequenceNumber | Field Type  int  Description  Required.  The sequence number of a step in an expression set definition version. |
| shouldExposExecPathMsgOnly | Field Type  boolean  Description  Indicates whether the message in the explainability message template is exposed for only the branch path that was run. |
| shouldExposeConditionDetails | Field Type  boolean  Description  Indicates whether the details of the condition are shown in the decision explanation. |
| shouldShowExplExternally | Field Type  boolean  Description  Indicates whether the decision explanations are shown to external users. |
| stepType | Field Type  ExpsSetStepType (enumeration of type string)  Description  Required.  Specifies the type of step in an expression set definition version.  Valid values are:  - `AdvancedCondition` - `AdvancedListFilter` (Available in API version   67.0 and later). - `Branch` - `BusinessKnowledgeModel` - `Condition` - `DefaultPath` - `ListFilter` (Available in API version 67.0 and   later). - `ListGroup` (Available in API version 67.0 and   later). - `SubExpression` |
| subExpression | Field Type  [ExpressionSetSubExpression](#ExpSetSubExp)  Description  Represents a sub expression step. |

## ExpressionSetAdvancedCondition

Represents an advanced condition step.

| Field Name | Description |
| --- | --- |
| conditionLogic | Field Type  string  Description  Required.  The condition that’s defined for an advanced condition. |
| criteria | Field Type  [ExpressionSetConditionCriteria](#ExpSetConCriteria) []  Description  Represents an array of criteria defined in the advanced condition. |
| errorMessage | Field Type  string  Description  An error message for a failed advanced condition. |
| resultParameter | Field Type  string  Description  An expression set definition version variable associated with the result of a step. |
| successMessage | Field Type  string  Description  A success message for a successful advanced condition. |

## ExpressionSetConditionCriteria

Represents a criterion defined in an advanced condition.

| Field Name | Description |
| --- | --- |
| operator | Field Type  ExpsSetConditionOperator (enumeration of type string)  Description  Required.  Specifies the operator for evaluating an expression.  Valid values are:  - `Contains` - `DoesNotContain` - `Equals` - `GreaterThan` - `GreaterThanOrEquals` - `IsNull` - `IsNotNull` - `LessThan` - `LessThanOrEquals` - `NoEquals` |
| sequenceNumber | Field Type  int  Description  Required.  The position of the condition in a step that contains multiple conditions. |
| sourceFieldName | Field Type  string  Description  Required.  The expression set definition version variable associated with the result of a condition criterion. |
| value | Field Type  string  Description  Specifies the condition of a criterion. |
| valueType | Field Type  ExpsSetValueType (enumeration of type string)  Description  Specifies the type of value.  Valid values are:  - `Formula` - `Literal` - `Lookup` - `Parameter` - `Picklist` |

## ExpressionSetAggregation

Represents an aggregation step.

| Field Name | Description |
| --- | --- |
| aggregatedParameter | Field Type  string  Description  Required.  The expression set definition version variable associated with the result of a condition criterion. |
| aggregateFunction | Field Type  ExpsSetAggregationFunction (enumeration of type string)  Description  Required.  Specifies the aggregation function used in a step.  Valid values are:  - `Avg` - `Max` - `Min` - `Sum` |
| expression | Field Type  string  Description  Required.  Specifies the expression of an aggregation. |

## ExpressionSetAssignment

Represents an assignment step.

| Field Name | Description |
| --- | --- |
| aggregatedParameter | Field Type  string  Description  Required.  The expression set definition version variable associated with a step detail. |
| expression | Field Type  string  Description  Required.  The expression that’s defined for a step. |

## ExpressionSetConditionExpression

Represents a condition in a condition step.

| Field Name | Description |
| --- | --- |
| errorMessage | Field Type  string  Description  An error message for a failed condition. |
| expression | Field Type  string  Description  Required.  The expression that’s defined for a step. |
| resultParameter | Field Type  string  Description  The expression set definition version variable associated with the result of a step. |
| successMessage | Field Type  string  Description  A success message for a successful condition. |

## ExpressionSetCustomElement

Represents a custom element in an expression set. Available in API version 56.0 and
later.

| Field Name | Description |
| --- | --- |
| parameters | Field Type  [ExpressionSetElementParameter](#ExpressionSetElementParameter)[]  Description  Represents the list of parameters in the custom element. |

## ExpressionSetElementParameter

Represents a parameter within a custom element of an expression set. Available in API
version 56.0 and later.

| Field Name | Description |
| --- | --- |
| input | Field Type  boolean  Description  Required. Indicates whether the custom element parameter is input (`true`) or not (`false`).  The default value is `true`. |
| name | Field Type  string  Description  Required. The name of the custom element parameter. |
| output | Field Type  boolean  Description  Required. Indicates whether the custom element parameter is output (`true`) or not (`false`).  The default value is `true`. |
| type | Field Type  ExpsSetValueType (enumeration of type string)  Description  The type of custom element parameter. Values are:   - `Formula` - `Literal` - `Lookup` - `Parameter` - `PickList`  The default value is `Parameter`. |
| value | Field Type  string  Description  Required. The name of the expression set variable. |

## ExpressionSetDecisionTable

Represents a decision table or decision matrix in a step.

| Field Name | Description |
| --- | --- |
| decisionTableName | Field Type  string  Description  Required.  The decision matrix or decision table name used in a step. |
| mappings | Field Type  [ExpressionSetElementParameter[]](#ExpressionSetElementParameter)  Description  The mapping information between various parameters in an ExpressionSetDecisionTable.  Available in API version 59.0 and later. |
| type | Field Type  string  Description  Required.  The type in a step. It can be a decision table or decision matrix. |

## ExpressionSetSubExpression

Represents a sub expression in a step.

| Field Name | Description |
| --- | --- |
| expressionSet | Field Type  string  Description  Required.  The sub expression name used in a step. |
| mappings | Field Type  [ExpressionSetElementParameter[]](#ExpressionSetElementParameter)  Description  The mapping information between various parameters in an ExpressionSetDecisionTable.  Available in API version 61.0 and later. |

## ExpressionSet​​Variable

Represents a definition of an expression set variable.

| Field Name | Description |
| --- | --- |
| collection | Field Type  boolean  Description  Indicates whether a variable stores a collection of values (`true`) or not (`false`). |
| dataType | Field Type  ExpsSetDataType (enumeration of type string)  Description  Required.  The data type of an expression set variable.  Valid values are:  - `ActionOutput` - `Boolean` - `Currency` - `Date` - `DateTime` - `DecisionMatrix` - `DecisionTable` - `Numeric` - `Percent` - `Sobject` - `SubExpression` - `Text` |
| decimalPlaces | Field Type  int  Description  The decimal digits in the currency, number, or percent data type for an expression set variable. |
| description | Field Type  string  Description  The description of the variable used in an expression set. |
| fields | Field Type  [ExpressionSetVariableField](#ExpSetVarFld) []  Description  Represents an array of fields in an object that's used as a variable in an expression set. |
| input | Field Type  boolean  Description  Indicates whether an expression set variable is used as an input (`true`) in an expression or not (`false`). |
| lookupName | Field Type  string  Description  The API name of a decision matrix, a decision table, or a sub expression. |
| lookupType | Field Type  ExpsSetVariableLookupType (enumeration of type string)  Description  The type of the lookup used in an expression set definition.  Valid values are:  - `DecisionMatrix` - `DecisionTable` - `SubExpression` |
| name | Field Type  string  Description  Required.  The full name of the variable used in an expression set definition. |
| objectName | Field Type  string  Description  The name of the sObject. |
| output | Field Type  boolean  Description  Indicates whether an expression set variable is used as an output in an expression(`true`) or not (`false`). |
| resultStep | Field Type  string  Description  The step that produces the expression set variable. |
| type | Field Type  ExpsSetVariableType (enumeration of type string)  Description  Required.  The type of variable in an expression set definition.  Valid values are:  - `Constant` - `ContextDynamicAttributeTag` (Available in API   version 62.0 and later.) - `ExecutableContextDefinitionTag`   (Available in API version 62.0 and later.) - `Formula` - `Variable` |
| value | Field Type  string  Description  Represents a constant value or a formula.  Note Note It stores the default value of a variable. |

## ExpressionSetVariableField

Represents a definition of a field in an object that's used as a variable in an expression
set.

| Field Name | Description |
| --- | --- |
| dataType | Field Type  ExpsSetDataType (enumeration of type string)  Description  Required.  Specifies the type of data stored in an expression set variable.  Valid values are:  - `ActionOutput` - `Boolean` - `Currency` - `Date` - `DateTime` - `DecisionMatrix` - `DecisionTable` - `Numeric` - `Percent` - `Sobject` - `SubExpression` - `Text` |
| decimalPlaces | Field Type  int  Description  The decimal digits in the currency, number, or percent data type for an expression set variable. |
| fields | Field Type  [ExpressionSetVariableField](#ExpSetVarFld) []  Description  Represents an array of fields in an object that's used as a variable in an expression set. |
| lookupName | Field Type  string  Description  The API name of a decision matrix, a decision table, or a sub expression. |
| lookupType | Field Type  ExpsSetVariableLookupType (enumeration of type string)  Description  Required.  The type of lookup used in an expression set definition.  Valid values are:  - `DecisionMatrix` - `DecisionTable` - `SubExpression` |
| name | Field Type  string  Description  Required.  The full name of the field used in an expression set variable. |
| objectName | Field Type  string  Description  The name of the sObject. |

## Declarative Metadata Sample Definition

The following is an example of an ExpressionSetDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ExpressionSetDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>ExpSetWithAllSteps</label>
    <processType>Bre</processType>
    <template>false</template>
    <description></description>
    <interfaceSourceType>Sample</interfaceSourceType>
    <executionScale>Low</executionScale>
    <versions>
        <fullName>ExpSetWithAllSteps_V1</fullName>
        <expressionSetDefinition>ExpSetWithAllSteps</expressionSetDefinition>
        <label>ExpSetWithAllSteps V1</label>
        <shouldShowExplExternally>false</shouldShowExplExternally>
        <startDate>2022-08-09T22:04:56.000Z</startDate>
        <endDate>2023-08-09T22:04:56.000Z</endDate>
        <status>Draft</status>
        <uiTier>false</uiTier>
        <rank>1</rank>
        <description>ExpSetWithAllSteps_V1</description>
        <steps>
            <description>Aggregate</description>
            <actionType>BreAggregator</actionType>
            <aggregation>
                <aggergatedParameter>result</aggergatedParameter>
                <aggregateFunction>Avg</aggregateFunction>
                <expression>AVG ( result )</expression>
            </aggregation>
            <label>Aggregate</label>
            <name>Aggregate</name>
            <resultIncluded>true</resultIncluded>
            <sequenceNumber>5</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <label>Branch</label>
            <name>Branch</name>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>4</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>Branch</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>b</assignedParameter>
                <expression>SUM ( a , 10 )</expression>
            </assignment>
            <label>Calculation</label>
            <name>Calculation</name>
            <resultIncluded>true</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>result</assignedParameter>
                <expression>b * 100</expression>
            </assignment>
            <label>Calculation</label>
            <name>Calculation10</name>
            <parentStep>DefaultLane</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>result</assignedParameter>
                <expression>b * 1</expression>
            </assignment>
            <label>Calculation</label>
            <name>Calculation3</name>
            <parentStep>Condition</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>result</assignedParameter>
                <expression>SUM ( b , 10 )</expression>
            </assignment>
            <label>Calculation</label>
            <name>Calculation5</name>
            <parentStep>Condition4</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>result</assignedParameter>
                <expression>b * 10</expression>
            </assignment>
            <label>Calculation</label>
            <name>Calculation8</name>
            <parentStep>Condition7</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <steps>
            <conditionExpression>
                <successMessage>success</successMessage>
                <errorMessage>error</errorMessage>
                <expression>IS10 == b</expression>
                <resultParameter>condition_output__1</resultParameter>
            </conditionExpression>
            <label>Condition</label>
            <name>Condition</name>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>2</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>Condition</stepType>
        </steps>
        <steps>
            <advancedCondition>
                <successMessage>success</successMessage>
                <errorMessage>error</errorMessage>
                <conditionLogic>1</conditionLogic>
                <criteria>
                    <operator>Equals</operator>
                    <sequenceNumber>1</sequenceNumber>
                    <sourceFieldName>condition_output__1</sourceFieldName>
                    <value>true</value>
                    <valueType>Literal</valueType>
                </criteria>
                <resultParameter>condition_output__3</resultParameter>
            </advancedCondition>
            <label>Condition</label>
            <name>Condition4</name>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>3</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>AdvancedCondition</stepType>
        </steps>
        <steps>
            <conditionExpression>
                <expression>IS10 == b</expression>
                <resultParameter>condition_output__2</resultParameter>
            </conditionExpression>
            <label>Condition</label>
            <name>Condition7</name>
            <parentStep>Branch</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>Condition</stepType>
        </steps>
        <steps>
            <label>Default Lane</label>
            <name>DefaultLane</name>
            <parentStep>Branch</parentStep>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>2</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>false</shouldShowExplExternally>
            <stepType>DefaultPath</stepType>
        </steps>
        <steps>
            <actionType>AssignParameterValues</actionType>
            <assignment>
                <assignedParameter>a</assignedParameter>
                <expression>3</expression>
            </assignment>
            <failedExplainerTemplate>CalculationFailure</failedExplainerTemplate>
            <failedMessageTokenMappings>
                <expressionSetMessageToken>y2</expressionSetMessageToken>
                <resourceReference>a</resourceReference>
            </failedMessageTokenMappings>
            <label>CalculationStepWithTokensAndMappings</label>
            <name>CalculationStepWithTokensAndMappings</name>
            <passedExplainerTemplate>CalculationSuccess</passedExplainerTemplate>
            <passedMessageTokenMappings>
                <expressionSetMessageToken>y1</expressionSetMessageToken>
                <resourceReference>a</resourceReference>
            </passedMessageTokenMappings>
            <resultIncluded>false</resultIncluded>
            <sequenceNumber>1</sequenceNumber>
            <shouldExposExecPathMsgOnly>true</shouldExposExecPathMsgOnly>
            <shouldExposeConditionDetails>false</shouldExposeConditionDetails>
            <shouldShowExplExternally>true</shouldShowExplExternally>
            <stepType>BusinessKnowledgeModel</stepType>
        </steps>
        <variables>
            <collection>false</collection>
            <dataType>Boolean</dataType>
            <description>condition_output__3</description>
            <input>false</input>
            <name>condition_output__3</name>
            <output>false</output>
            <resultStep>Condition4</resultStep>
            <type>Variable</type>
            <value>False</value>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Numeric</dataType>
            <decimalPlaces>2</decimalPlaces>
            <description>a</description>
            <input>true</input>
            <name>a</name>
            <output>false</output>
            <type>Variable</type>
            <value>10</value>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Boolean</dataType>
            <description>condition_output__1</description>
            <input>false</input>
            <name>condition_output__1</name>
            <output>false</output>
            <resultStep>Condition</resultStep>
            <type>Variable</type>
            <value>False</value>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Boolean</dataType>
            <description>condition_output__2</description>
            <input>false</input>
            <name>condition_output__2</name>
            <output>false</output>
            <resultStep>Condition7</resultStep>
            <type>Variable</type>
            <value>False</value>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Numeric</dataType>
            <decimalPlaces>2</decimalPlaces>
            <description>IS10</description>
            <input>false</input>
            <name>IS10</name>
            <output>false</output>
            <type>Constant</type>
            <value>10</value>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Numeric</dataType>
            <decimalPlaces>2</decimalPlaces>
            <description>b</description>
            <input>false</input>
            <name>b</name>
            <output>true</output>
            <type>Variable</type>
        </variables>
        <variables>
            <collection>false</collection>
            <dataType>Numeric</dataType>
            <decimalPlaces>2</decimalPlaces>
            <description>result</description>
            <input>false</input>
            <name>result</name>
            <output>true</output>
            <type>Variable</type>
        </variables>
        <versionNumber>1</versionNumber>
    </versions>
</ExpressionSetDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>ExpressionSetDefinition</name>
	</types>
	<version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based.htm "HTML (New Window)").
