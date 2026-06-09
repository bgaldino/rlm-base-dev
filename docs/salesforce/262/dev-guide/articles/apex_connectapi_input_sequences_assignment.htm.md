---
page_id: apex_connectapi_input_sequences_assignment.htm
title: ConnectApi.SequencesAssignmentInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_sequences_assignment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.SequencesAssignmentInputRepresentation

The details of the target objects to which the sequence pattern values are assigned.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequencePolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
| `shouldPublishPlatformEvent` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
| `targetObjectIds` | List<`String`> | List of records to which the sequence pattern values are assigned. | Required | 65.0 |
