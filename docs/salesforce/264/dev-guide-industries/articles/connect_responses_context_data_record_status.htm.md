---
page_id: connect_responses_context_data_record_status.htm
title: Context Data Record Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_data_record_status.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Data Record Status

Output representation of context data record status.

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextErrors` | [Context Error](./connect_responses_context_error.htm.md)[] | List of context errors. | Small, 59.0 | 59.0 |
| `dataPath` | String[] | Path of the data. | Small, 59.0 | 59.0 |
| `processingStatus` | String | Processing status of the context data record. | Small, 59.0 | 59.0 |
