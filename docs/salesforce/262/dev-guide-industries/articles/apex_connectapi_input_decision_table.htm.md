---
page_id: apex_connectapi_input_decision_table.htm
title: ConnectApi.DecisionTableInput
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_input_classes.htm
fetched_at: 2026-06-25
---

# ConnectApi.DecisionTableInput

Input representation of the decision table.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | List<[`ConnectApi.​DecisionTableCondition`](./apex_connectapi_input_decision_table_condition_representatio.htm.md "Input representation of the decision table condition.")> | List of decision table conditions on which the decision table executes. | Required | 51.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 51.0 |
