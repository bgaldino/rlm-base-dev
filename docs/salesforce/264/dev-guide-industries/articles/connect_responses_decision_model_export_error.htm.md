---
page_id: connect_responses_decision_model_export_error.htm
title: Decision Model Export Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_model_export_error.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Model Export Error

Error representation of a failed DMN (Decision Model Notation) export
      request.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Error code corresponding to the failed export request. | Small, 58.0 | 58.0 |
| `errorMessage` | String | Error message corresponding to the failed export request. | Small, 58.0 | 58.0 |
| `recordId` | String | Version ID of the decision matrix for which the data export request failed. | Small, 58.0 | 58.0 |
