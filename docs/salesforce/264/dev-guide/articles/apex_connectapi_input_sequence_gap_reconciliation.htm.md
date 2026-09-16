---
page_id: apex_connectapi_input_sequence_gap_reconciliation.htm
title: ConnectApi.SequenceGapReconciliationInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_sequence_gap_reconciliation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.SequenceGapReconciliationInputRepresentation

The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequencePolicyIds` | List<`String`> | List of IDs of the sequence policies. | Required if the `targetObjects` property isn't specified. You must not specify both properties. | 65.0 |
| `targetObjects` | List<`String`> | List of objects to which the policies are applied. | Required if the `sequencePolicyIds` property isn't specified. You must not specify both properties. | 65.0 |
