---
page_id: apex_connectapi_output_sequences_assignment_result_output.htm
title: ConnectApi.SequencesAssignmentResultOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_sequences_assignment_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

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
