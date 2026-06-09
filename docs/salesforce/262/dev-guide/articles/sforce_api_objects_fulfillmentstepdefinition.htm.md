---
page_id: sforce_api_objects_fulfillmentstepdefinition.htm
title: FulfillmentStepDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstepdefinition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentStepDefinition

Represents a definition of a step that must be executed during
fulfillment orchestration. This object is available in API version 61.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AmendGroupId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fulfillment step group that's added to the fulfillment plan when the step is amended. This field is available in API version 62.0 and later.  This field is a relationship field.  Relationship Name  AmendGroup  Refers To  FulfillmentStepDefinitionGroup |
| AssignedToId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The user or queue associated with the fulfillment step definition.  This field is a polymorphic relationship field.  Relationship Name  AssignedTo  Relationship Type  Lookup  Refers To  Queue, User |
| CancelledGroupId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fulfillment step group that's added to the fulfillment plan when the step is canceled. This field is available in API version 62.0 and later.  This field is a relationship field.  Relationship Name  CancelledGroup  Refers To  FulfillmentStepDefinitionGroup |
| CustomBaseExecutionDate | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The context tag containing a custom date that's used to calculate the execution time for a future-dated step. This field is available in API version 65.0 and later. |
| CustomConfigParameter | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Represents the custom configuration context given by the designer. This context is passed to fulfillment steps during execution to support flow reusability. |
| CustomFulfillmentScope | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The custom scope to use during order fulfillment. This field is available in API version 65.0 and later. |
| DelayOf | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value of the delay. This field is available in API version 63.0 and later. |
| DelayUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit for the delay of the fulfillment step. This field is available in API version 63.0 and later.  Valid values are:  - `Days` - `Hours` - `Minutes` |
| ExecuteOn | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies when to execute the fulfillment step. This field is available in API version 63.0 and later.  Valid values are:  - `PreviousStepsStartDate` - `SourceLineStartDate` |
| ExecuteOnConditionData | Type  textarea  Properties  Create, Nillable, Update  Description  The condition for executing the fulfillment step. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later. |
| ExecuteOnRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The expression set for the fulfillment step. The step is executed only when the corresponding expression set is `true`.  This field is a polymorphic relationship field.  Relationship Name  ExecuteOnRule  Relationship Type  Lookup  Refers To  ExpressionSet |
| FlowDefinitionName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the associated flow. |
| ForcePlanFreezeDuringExecution | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to freeze the plan while the step is in progress. If enabled, specifies how to complete the step before resuming the plan. This field is available in API version 63.0 and later.  Valid values are:  - `Never` - `YesButForcefullyCompleteStep`  The default value is `Never`. |
| IntegrationDefinitionNameId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the integration definition that’s used to set up communication with an external endpoint.  This field is a relationship field.  Relationship Name  IntegrationDefinitionName  Relationship Type  Lookup  Refers To  IntegrationProviderDef |
| IsSkipBranch | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the remaining steps in the fulfillment step group are skipped from execution when the Execute On Rule condition is set. This field is available in API version 62.0 and later.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the fulfillment step definition. |
| OmniscriptName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only. |
| PointOfNoReturn | Type  multipicklist  Properties  Create, Filter, Nillable, Update  Description  The type of source change applied to the line item. This field is available in API version 62.0 and later.  Valid value is:  - `Changes Denied` |
| ResumeOnConditionData | Type  textarea  Properties  Create, Nillable, Update  Description  The condition for resuming the paused fulfillment step. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later. |
| ResumeOnRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The expression set for the fulfillment step definition. The step is completed when the expression set is `true`.  This field is a polymorphic relationship field.  Relationship Name  ResumeOnRule  Relationship Type  Lookup  Refers To  ExpressionSet |
| RunAsUserId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The user context to run a fulfillment step when the fulfillment operator wants to override the default autoproc user.  This field is a relationship field.  Relationship Name  RunAsUser  Relationship Type  Lookup  Refers To  User |
| Scope | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The scope of the fulfillment step definition. For example, `Bundle` or `Order`.  Valid values are:  - `Bundle` - `CrossPlan` - `LineItem` - `Plan`  The default value is `Plan`. |
| StepDefinitionGroupId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  StepDefinitionGroup  Relationship Type  Master-detail  Refers To  FulfillmentStepDefinitionGroup (the master object) |
| StepType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  For internal use only.  Valid values are:  - `AutoTask` - `Callout` - `ManualTask` - `Milestone` - `Pause` - `StagedAssetize` |
| TaskAllocationType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The method of assigning the manual step. This field is available in API version 62.0 and later.  Valid value is:  - `RoundRobin` - `LeastLoaded` - `ContextBased` |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The business vertical that uses fulfillment orchestration. For example, Financial Services Cloud.  Valid values are:  - `IntegrationOrchestrator` - `OrderFulfillment` |
