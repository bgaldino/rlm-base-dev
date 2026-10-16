---
page_id: apex_connectapi_output_decision_table_outcome.htm
title: ConnectApi.DecisionTableOutcome
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_output_decision_table_outcome.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.DecisionTableOutcome

Output representation of the decision table
    execution.

#### 

- 
- 
- 

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errorCode` | Integer | The error code if transaction fails for any reason. | 51.0 |
| `errorMessage` | String | The error message if transaction fails for any reason. | 51.0 |
| `outcomeList` | List<[`ConnectApi.​DecisionTableOutcomeItem`](./apex_connectapi_output_decision_table_outcome_item.htm.md)> | The outcome list that stores two or more outcomes provided by the decision table. Note A decision table that is invoked by the Decision Table custom invocable action can provide up to 50 outcomes. | 51.0 |
| `outcomeType` | String | The outcome type after the request is successful. Valid values are: `MultipleMatch`—Outcome returns multiple matches. `NoMatch`—Outcome returns no match. `SingleMatch`—Outcome returns single match. | 51.0 |
| `successStatus` | Boolean | Indicates the status of the decision table execution. | 51.0 |
