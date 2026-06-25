---
page_id: connect_responses_explainability_detailed_action_log_detail.htm
title: Explainability Detailed Action Log Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_detailed_action_log_detail.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_responses.htm
fetched_at: 2026-06-25
---

# Explainability Detailed Action Log Detail

Output representation of explainability action log in detail.

JSON example
:   ```
    {
        "actionContextCode": "001xx000003GYiCAAW",
        "actionLog": "{&quot;input&quot;:{&quot;calcInput&quot;:10},&quot;ruledefinition&quot;:{&quot;interfaceSourceType&quot;:null,&quot;calculationProcedureId&quot;:&quot;9QLxx0000004C92GAE&quot;,&quot;variables&quot;:{&quot;details&quot;:[{&quot;apiName&quot;:&quot;calInt&quot;,&quot;isEditable&quot;:true,&quot;defaultValue&quot;:null,&quot;displayName&quot;:null,&quot;dataType&quot;:&quot;Number&quot;,&quot;precision&quot;:2,&quot;calculationMatrixName&quot;:null,&quot;name&quot;:&quot;calInt&quot;,&quot;isUserDefined&quot;:true,&quot;uiDisplayOrder&quot;:null,&quot;id&quot;:null},{&quot;apiName&quot;:&quot;calcInput&quot;,&quot;isEditable&quot;:true,&quot;defaultValue&quot;:null,&quot;displayName&quot;:null,&quot;dataType&quot;:&quot;Number&quot;,&quot;precision&quot;:2,&quot;calculationMatrixName&quot;:null,&quot;name&quot;:&quot;calcInput&quot;,&quot;isUserDefined&quot;:true,&quot;uiDisplayOrder&quot;:null,&quot;id&quot;:null}]},&quot;code&quot;:null,&quot;endDate&quot;:null,&quot;contextDefinition&quot;:null,&quot;description&quot;:null,&quot;message&quot;:null,&quot;enabled&quot;:true,&quot;versionNumber&quot;:1,&quot;aliasGroupList&quot;:{&quot;aliasGroupList&quot;:[]},&quot;versionId&quot;:&quot;0k1xx0000004C92GAE&quot;,&quot;showExplExternally&quot;:false,&quot;root&quot;:{&quot;steps&quot;:[&quot;Calculation&quot;]},&quot;executionScale&quot;:&quot;Low&quot;,&quot;name&quot;:&quot;ExpDes V1&quot;,&quot;rank&quot;:1,&quot;step&quot;:{&quot;details&quot;:{&quot;Calculation&quot;:{&quot;inputVariablesFormatText&quot;:&quot;[{&#92;&quot;dataType&#92;&quot;:&#92;&quot;Number&#92;&quot;,&#92;&quot;name&#92;&quot;:&#92;&quot;calcInput&#92;&quot;,&#92;&quot;alias&#92;&quot;:&#92;&quot;calcInput&#92;&quot;}]&quot;,&quot;exposeExecPathMsgOnly&quot;:true,&quot;stepType&quot;:&quot;Calculation&quot;,&quot;lookupTableName&quot;:null,&quot;outputVariablesFormatText&quot;:&quot;{&#92;&quot;name&#92;&quot;:&#92;&quot;calInt&#92;&quot;}&quot;,&quot;customElementName&quot;:null,&quot;passedExplainerTemplateId&quot;:null,&quot;conditionsUiFormattedText&quot;:&quot;&quot;,&quot;description&quot;:null,&quot;inputVariablesMappingText&quot;:null,&quot;outputVariablesMappingText&quot;:&quot;{&#92;&quot;calInt&#92;&quot;:&#92;&quot;calInt&#92;&quot;}&quot;,&quot;calculationMatrixId&quot;:null,&quot;failedExplainerTemplateId&quot;:null,&quot;exposeConditionDetails&quot;:false,&quot;referenceCalculationProcedureId&quot;:null,&quot;id&quot;:&quot;Calculation&quot;,&quot;returnMessageValueSet&quot;:&quot;{&#92;&quot;true&#92;&quot;:&#92;&quot;&#92;&quot;,&#92;&quot;false&#92;&quot;:&#92;&quot;&#92;&quot;}&quot;,&quot;passedMessageTokenMappings&quot;:[],&quot;failedMessageTokenMappings&quot;:[],&quot;lookupTableError&quot;:null,&quot;noResultMessageTokenMappings&quot;:[],&quot;formulaUiFormattedText&quot;:null,&quot;noResultExplainerTemplateId&quot;:null,&quot;conditionsExpressionText&quot;:null,&quot;isResultIncluded&quot;:true,&quot;formulaExpressionText&quot;:&quot;100 + calcInput&quot;,&quot;showExplExternally&quot;:false,&quot;stage&quot;:&quot;Calculation&quot;,&quot;name&quot;:&quot;Calculation&quot;,&quot;childStepIds&quot;:[]}}},&quot;constants&quot;:{&quot;details&quot;:[]},&quot;allowNullInputsInSimulation&quot;:false,&quot;startDate&quot;:1709616068000,&quot;isSuccess&quot;:true,&quot;usageType&quot;:&quot;Bre&quot;},&quot;simulation&quot;:{&quot;simulationStepResults&quot;:{&quot;Calculation&quot;:{&quot;stepInputs&quot;:[{&quot;datatype&quot;:&quot;Number&quot;,&quot;precision&quot;:2,&quot;name&quot;:&quot;calcInput&quot;,&quot;value&quot;:&quot;10.00&quot;}],&quot;stepResults&quot;:[{&quot;datatype&quot;:&quot;Number&quot;,&quot;precision&quot;:2,&quot;name&quot;:&quot;calInt&quot;,&quot;value&quot;:&quot;110.00&quot;}],&quot;isDefaulted&quot;:false}},&quot;simulationResults&quot;:[{&quot;datatype&quot;:&quot;Number&quot;,&quot;precision&quot;:2,&quot;name&quot;:&quot;calInt&quot;,&quot;value&quot;:&quot;110.00&quot;}]}}",
        "additionalFilter": "undef",
        "applicationLogDate": "Wed Mar 06 05:09:32 GMT 2024",
        "applicationSubtype": "BREDES",
        "applicationType": "0",
        "explainabilitySpecName": "BREDES",
        "name": "BREDES",
        "primaryFilter": "undef",
        "processType": "BREDES",
        "secondaryFilter": "undef",
        "uniqueIdentifier": "f89eff41-94ed-4fe7-9b72-f6df2bb5f4aa"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actionContextCode` | String | Record ID within the context of the associated application action that's used to retrieve the action log. | Small, 62.0 | 62.0 |
| `actionLog` | String | Contents of the explainability action log as a JSON string. | Small, 62.0 | 62.0 |
| `additionalFilter` | String | Additional filter that's used to retrieve the results. | Small, 62.0 | 62.0 |
| `applicationLogDate` | String | Date and time at which the explainability action log was generated by the application's action. | Small, 62.0 | 62.0 |
| `applicationSubtype` | String | Subtype of the associated application for which the explainability log is generated. It matches one of the valid values for Explainability Action Specification table's ApplicationSubtype field. | Small, 62.0 | 62.0 |
| `applicationType` | String | Name of the application for which the explainability service is run. It must match one of the valid values in the applicationType field of the Explainability Action Specification table. | Small, 62.0 | 62.0 |
| `explainabilitySpecName` | String | Name of the explainability specification associated with the action log. | Small, 62.0 | 62.0 |
| `name` | String | Name to identify the explainability action log record to be created. | Small, 62.0 | 62.0 |
| `primaryFilter` | String | Primary filter that's used to retrieve the results. | Small, 62.0 | 62.0 |
| `processType` | String | Type of business process associated with the application for which the explainability action log is generated. It must match with one of the valid values in the processType field of the Explainability Action Specification table. | Small, 62.0 | 62.0 |
| `secondaryFilter` | String | Secondary filter that's used to retrieve the results. | Small, 62.0 | 62.0 |
| `uniqueIdentifier` | String | Unique ID associated with the specific Explainability action log. | Small, 62.0 | 62.0 |
