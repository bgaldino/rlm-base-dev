---
page_id: apex_connectapi_input_decision_table.htm
title: ConnectApi.DecisionTableInput
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.DecisionTableInput

Input representation of the decision table.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | List<[`ConnectApi.​DecisionTableCondition`](./apex_connectapi_input_decision_table_condition_representatio.htm.md)> | List of decision table conditions on which the decision table executes. | Required | 51.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 51.0 |
