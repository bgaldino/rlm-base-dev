---
page_id: apex_ConnectAPI_SequencingWithoutAura_static_methods.htm
title: SequencingWithoutAura Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_SequencingWithoutAura_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# SequencingWithoutAura Class

Manage invoice sequencing processes by using the SequencingWithoutAura
class.

## Namespace

ConnectApi

## SequencingWithoutAura Methods

These methods are for `SequencingWithoutAura`. All
methods are static.

- **[reconcileSequences(sequenceGapReconciliationInputRepresentation)](./apex_ConnectAPI_SequencingWithoutAura_static_methods.htm.md#apex_ConnectAPI_SequencingWithoutAura_reconcileSequences_1)**  
  Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.
- **[sequenceAssignment(sequencesAssignmentInputRepresentation)](./apex_ConnectAPI_SequencingWithoutAura_static_methods.htm.md#apex_ConnectAPI_SequencingWithoutAura_sequenceAssignment_1)**  
  Assign sequence pattern values to objects based on the configured sequence policy.

### reconcileSequences(sequenceGapReconciliationInputRepresentation)

Restore a missing sequence value identified by using this API in gapless-enabled
sequences. This sequence value can be used later in the subsequent sequence policy numbering,
ensuring there are no gaps.

#### API Version

65.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.sequenceGapReconciliationOutputRepresentation reconcileSequences(ConnectApi.sequenceGapReconciliationInputRepresentation sequenceGapReconciliationInputRepresentation)`

#### Parameters

sequenceGapReconciliationInputRepresentation
:   Type: [`ConnectApi.SequenceGapReconciliationInputRepresentation`](./apex_connectapi_input_sequence_gap_reconciliation.htm.md "The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.")
:   The details of the input used to identify and reconcile gaps in sequence values based on the
    sequence policy or target object.

#### Return Value

Type: [`ConnectApi.SequenceGapReconciliationOutputRepresentation`](./apex_connectapi_output_sequence_gap_reconciliation_output.htm.md "Output representation of the details of the sequence gap reconciliation.")

#### Usage

You need the Billing Admin permission set to use this method.

### sequenceAssignment(sequencesAssignmentInputRepresentation)

Assign sequence pattern values to objects based on the configured sequence
policy.

#### API Version

65.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.SequencesAssignmentOutputRepresentation sequenceAssignment(ConnectApi.SequencesAssignmentInputRepresentation sequencesAssignmentInputRepresentation)`

#### Parameters

sequencesAssignmentInputRepresentation
:   Type: [`ConnectApi.SequencesAssignmentInputRepresentation`](./apex_connectapi_input_sequences_assignment.htm.md "The details of the target objects to which the sequence pattern values are assigned.")
:   The details of the target objects to which the sequence pattern values are assigned.

#### Return Value

Type: [`ConnectApi.SequencesAssignmentOutputRepresentation`](./apex_connectapi_output_sequences_assignment_output.htm.md "Output representation showing the status of the assigned sequence pattern values.")

#### Usage

You need the Billing Admin permission set to use this method.
