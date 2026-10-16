---
page_id: apex_connectapi_output_sequences_assignment_result_output.htm
title: ConnectApi.SequencesAssignmentResultOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_sequences_assignment_result_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.SequencesAssignmentResultOutputRepresentation

Output representation of the details of the assigned sequence values to target
    objects.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<`ConnectApi.SequenceErrorOutputRepresentation`> | Error encountered during the processing of the API request. | 65.0 |
| `isSuccess` | Boolean | Indicates whether the sequence pattern value was assigned (`true`) or not (`false`). | 65.0 |
| `sequencePatternValue` | String | Sequence pattern value assigned to the target object. | 65.0 |
| `sequencePolicyId` | String | ID of the sequence policy assigned to the target object. | 65.0 |
| `targetObjectId` | String | Record to which the sequence pattern value is assigned. | 65.0 |
