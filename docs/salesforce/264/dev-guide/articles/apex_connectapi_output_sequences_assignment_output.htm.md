---
page_id: apex_connectapi_output_sequences_assignment_output.htm
title: ConnectApi.SequencesAssignmentOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_sequences_assignment_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.SequencesAssignmentOutputRepresentation

Output representation showing the status of the assigned sequence pattern values.

- 
- 
- 

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[`ConnectApi.SequenceErrorOutputRepresentation`](./apex_connectapi_output_sequence_error_output.htm.md)> | Error encountered during the processing of the API request. | 65.0 |
| `sequencesAssignment` | List<[`ConnectApi.SequencesAssignmentResultOutputRepresentation`](./apex_connectapi_output_sequences_assignment_result_output.htm.md)> | Details of the sequence pattern values assignment. | 65.0 |
| `status` | `SequenceResponseStatusEnum` | Status of the sequence policy assignment. Valid values are: `PartialSuccess` `Success` `Failed` | 65.0 |
