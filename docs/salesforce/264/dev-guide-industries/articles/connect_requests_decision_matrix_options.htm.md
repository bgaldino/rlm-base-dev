---
page_id: connect_requests_decision_matrix_options.htm
title: Decision Matrix Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_options.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Options Input

Input representation of the options used to look up a decision
      matrix.

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | String | The date from when a decision matrix version comes into effect. The date format is yyyy-mm-dd’T’hh:mm:ss’Z. | Optional | 55.0 |
| `useDatesOnly` | String | Specifies that only the date portion (yyyy-mm-dd) of the value of the effectiveDate field be used at the time of execution. | Optional | 55.0 |
