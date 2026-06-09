---
page_id: sforce_api_objects_fulfillmentstep.htm
title: FulfillmentStep
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstep.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentStep

Represents a task that's required to perform a certain action as part
of order fulfillment. This task can be manual or automated. This object is available
in API version 61.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| ActualCompletionDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the fulfillment step state changed to `Completed` or `Skipped`. |
| ActualStartDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the fulfillment step state changed to `Ready`. |
| AssignedToId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The user or queue associated with the fulfillment step.  This field is a polymorphic relationship field.  Relationship Name  AssignedTo  Relationship Type  Lookup  Refers To  Queue, User |
| CustomConfigParameter | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Represents the custom configuration context set by the designer in the Fulfillment Step Definition record. This context is passed to fulfillment steps during execution to enable flow reusability. |
| CompensatedStepId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The alternative step that's executed when a particular step in the fulfillment plan is amended or canceled.  This field is a relationship field. This field is available in API version 62.0 and later.  Relationship Name  CompensatedStep  Refers To  FulfillmentStep |
| DelayOf | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value of the delay. This field is available in API version 63.0 and later. |
| DelayUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit for the delay of the fulfillment step. This field is available in API version 63.0 and later.  Valid values are:  - `Days` - `Hours` - `Minutes` |
| ExecuteOn | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies when to execute the fulfillment step. This field is available in API version 63.0 and later.  Valid values are:  - `PreviousStepExecutionDate` - `SourceLineStartDate` |
| ExecuteOnRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the expression set. The fulfillment step is executed only when its corresponding expression set returns the value `true`.  This field is a polymorphic relationship field.  Relationship Name  ExecuteOnRule  Relationship Type  Lookup  Refers To  ExpressionSet |
| ExecutionMessage | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only. |
| FalloutQueueId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fallout queue that's associated with the fallout task. This field is available in API version 62.0 and later.  This field is a relationship field.  Relationship Name  FalloutQueue  Refers To  Group |
| FlowDefinitionName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the flow definition that's associated with the `AutoTask` type of fulfillment step. This field is available in API version 62.0 and later. |
| FlowInterviewId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The flow interview associated with the fulfillment step.  This field is a relationship field.  Relationship Name  FlowInterview  Relationship Type  Lookup  Refers To  FlowInterview |
| ForcePlanFreezeDuringExecution | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to freeze the plan while the step is in progress. If enabled, specifies how to complete the step before resuming the plan. This field is available in API version 63.0 and later.  Valid values are:  - `Never` - `YesButWaitForStepCompletion`  The default value is `Never`. |
| FulfillmentPlanId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The fulfillment plan associated with the fulfillment step.  This field is a relationship field.  Relationship Name  FulfillmentPlan  Relationship Type  Lookup  Refers To  FulfillmentPlan |
| FulfillmentStepDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The fulfillment step definition associated with the fulfillment step.  This field is a relationship field.  Relationship Name  FulfillmentStepDefinition  Relationship Type  Lookup  Refers To  FulfillmentStepDefinition |
| IntegrationDefinitionNameId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  IntegrationDefinitionName  Relationship Type  Lookup  Refers To  IntegrationProviderDef |
| IsSkipBranch | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the remaining steps in the fulfillment step group are skipped from execution when the Execute On Rule condition is set (`true`) or not (`false`). This field is available in API version 62.0 and later.  The default value is `false`. |
| JeopardyStatus | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The jeopardy status of the fulfillment step.  This field is a calculated field. |
| JeopardyThreshold | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The number of days, hours, minutes, or seconds, counting back from the expected duration, before a fulfillment step is in jeopardy. |
| JeopardyThresholdUnit | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The time unit of the jeopardy threshold.  Valid values are:  - `Days` - `Hours` - `Minutes` - `Seconds`  The default value is `Minutes`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the fulfillment step. |
| NextEarliestRunTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The next available time for the process execution. This field is available in API version 62.0 and later. |
| OmniscriptName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For inyternal use only. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| PlannedCompletionDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time Dynamic Revenue Orchestrator estimates that the fulfillment step will complete. |
| PlannedStartDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the Dynamic Revenue Orchestrator calculates the fulfillment step state change to `Ready`. |
| PointOfNoReturn | Type  multipicklist  Properties  Create, Filter, Nillable  Description  The type of source change applied to the line item. This field is available in API version 62.0 and later.  Valid value is:  - `Changes Denied` |
| RequestedCompletionDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The planned completion date and time of the fulfillment step. |
| RequestedStartDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The planned start date and time of the fulfillment step. |
| ResumeOnRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The rule set or expression set for the fulfillment step. The step is completed only when the corresponding expression set returns the `isExecuteStep` output as `true`.  This field is a polymorphic relationship field.  Relationship Name  ResumeOnRule  Relationship Type  Lookup  Refers To  ExpressionSet |
| RetryAttempts | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The number of attempts allowed for retry as set up in the Fallout Qualification Rule table. |
| RunAsUserId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Overrides user context for an automated step. The default user context is AutomatedProc user.  This field is a relationship field.  Relationship Name  RunAsUser  Relationship Type  Lookup  Refers To  User |
| State | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The state of the fulfillment step. For example, `In Progress` or `Completed`.  Valid values are:  - `Completed` - `Failed` - `FatallyFailed` - `InProgress` - `Pending` - `Ready` - `Scheduled` - `Skipped` |
| StepType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The fulfillment step type associated with the fulfillment step.  Valid values are:  - `AutoTask` - `Callout` - `ManualTask` - `Milestone` - `Pause` - `StagedAssetize`—Available in API version 63.0   and later. |
| TaskAllocationType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The method of assigning the manual step. This field is available in API version 63.0 and later.  Valid values are:  - `ContextBased` - `LeastLoaded` - `RoundRobin` |
| TaskId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the task assigned to a user or queue. This field is available in API version 63.0 and later.  This field is a relationship field.  Relationship Name  Task  Refers To  Task |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The details about the business that uses Fulfillment Orchestration. Some examples of UsageBy include Financial Services Cloud and CPQ.  Valid values are:  - `Fulfillment` - `InsuranceRuleAction` - `IntegrationOrchestrator` - `OrderFulfillment` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[FulfillmentStepChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.")
:   Change events are available for the object.

[FulfillmentStepHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[FulfillmentStepShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
