---
page_id: apex_connectapi_output_sequences_assignment_output.htm
title: ConnectApi.SequencesAssignmentOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_sequences_assignment_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.SequencesAssignmentOutputRepresentation

Output representation showing the status of the assigned sequence pattern values.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[`ConnectApi.SequenceErrorOutputRepresentation`](./apex_connectapi_output_sequence_error_output.htm.md "Output representation of the error response that's associated with a request to create or update a sequence policy, or assign sequences.")> | Error encountered during the processing of the API request. | 65.0 |
| `sequencesAssignment` | List<[`ConnectApi.SequencesAssignmentResultOutputRepresentation`](./apex_connectapi_output_sequences_assignment_result_output.htm.md "Output representation of the details of the assigned sequence values to target objects.")> | Details of the sequence pattern values assignment. | 65.0 |
| `status` | `SequenceResponseStatusEnum` | Status of the sequence policy assignment. Valid values are:   - `PartialSuccess` - `Success` - `Failed` | 65.0 |
