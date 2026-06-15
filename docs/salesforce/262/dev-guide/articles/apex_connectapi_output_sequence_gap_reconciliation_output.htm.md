---
page_id: apex_connectapi_output_sequence_gap_reconciliation_output.htm
title: ConnectApi.SequenceGapReconciliationOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_sequence_gap_reconciliation_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.SequenceGapReconciliationOutputRepresentation

Output representation of the details of the sequence gap reconciliation.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `error` | [`ConnectApi.SequenceGapReconciliationErrorOutputRepresentation`](./apex_connectapi_output_sequence_gap_reconciliation_error_output.htm.md "List of errors encountered during the processing of the API request.") | List of errors encountered during the processing of the API request. | 65.0 |
| `jobId` | String | Unique identifier assigned to sequence gap reconciliation asynchronous process. | 65.0 |
| `sequencePolicyIds` | List<`String`> | List of IDs of the sequence policies. | 65.0 |
| `status` | `StatusEnum` | The status of sequence reconciliation API request. Valid values are:   - `Submitted` - `NotSubmitted` | 65.0 |
| `submittedAt` | String | Date and time when the reconciliation request was submitted to the async job. | 65.0 |
| `targetObjects` | List<`String`> | List of objects to which the policies are applied. | 65.0 |
