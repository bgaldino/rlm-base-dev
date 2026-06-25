---
page_id: meta_explainabilitymsgtemplate.htm
title: ExplainabilityMsgTemplate
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_explainabilitymsgtemplate.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ExplainabilityMsgTemplate

Represents information about the template
that contains the decision explanation message for a specified expression set step
type.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

ExplainabilityMsgTemplate components have the suffix
.explainabilityMsgTemplate and are stored in the
ExplainabilityMsgTemplates folder.

## Version

ExplainabilityMsgTemplate components are available in API version 56.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
|  |  |
| evaluationResult | Field Type  EvaluationResult (enumeration of type string)  Description  Required. The type of result for which the message template can be used. The step type for which the result is evaluated can be a condition, conditional group, or branch. Valid values are:   - `Failed` - `Passed` - `NoResult` |
| expressionSetStepType | Field Type  ExpressionSetStepType (enumeration of type string)  Description  Required. The step type in an expression set that uses the explainability message template. Valid values are:  - `Aggregation` - `Branch` - `BusinessElement` - `Calculation` - `Condition` - `DecisionTableLookup` - `ListEnabledGroup` - `ListFilter` - `MatrixLookup` - `ReferenceProcedure` |
| expsSetProcessType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  Required. The type of industry that’s using the expression set. Valid values are:   - `Bre` - `GpaCalculation` - `InsuranceClaimProcessing`—Available   in API version 65.0 and later. - `ItServiceManagement`—Available in   API version 65.0 and later. - `PlanCostCalculation` - `RatingDiscovery` - `StudentInformationSystem`—Available   in API version 65.0 and later. - `StudentSuccess`  When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other process types are available to you depending on your industry solution and permission sets. |
| isDefault | Field Type  boolean  Description  Indicates whether the decision explainer template for a specified step type is default (true) or not (false). |
| masterLabel | Field Type  string  Description  Required.  Master label the for ExplainabilityMsgTemplate. |
| message | Field Type  string  Description  Required. The message associated with the template for a specific expression set step type. |

## Declarative Metadata Sample Definition

The following is an example of an ExplainabilityMsgTemplate component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ExplainabilityMsgTemplate
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<evaluationResult>Passed</evaluationResult>
	<expressionSetStepType>Condition</expressionSetStepType>
	<expsSetProcessType>ProductQualification</expsSetProcessType>
	<isDefault>false</isDefault>
	<masterLabel>ML EMT testDM</masterLabel>
	<message>EMT Testing</message>
</ExplainabilityMsgTemplate>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>ExplainabilityMsgTemplate</name>
	</types>
	<version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based.htm "HTML (New Window)").
