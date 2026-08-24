---
page_id: connect_responses_decision_table_outcome_item.htm
title: Decision Table Outcome Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_outcome_item.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Outcome Item

Output representation of the decision table outcome
    item.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `values` | Map<String, Object> | The list of outcomes provided by the decision table. If the decision table is configured to sort outcomes based on an input field or the output field, then the outcomes are provided based on the selected sort order. | Small, 55.0 | 55.0 |
