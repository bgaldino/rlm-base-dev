---
page_id: apex-connectapi-sequencingwithoutaura-static-methods
title: SequencingWithoutAura Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-sequencingwithoutaura-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_SequencingWithoutAura_static_methods.htm
fetched_at: 2026-11-25
---

# SequencingWithoutAura Class

Manage invoice sequencing processes by using the SequencingWithoutAura class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## SequencingWithoutAura Methods

These methods are for `SequencingWithoutAura`. All methods are static.

- 

**[reconcileSequences(sequenceGapReconciliationInputRepresentation)](#reconcilesequencessequencegapreconciliationinputrepresentation)**

Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.

- 

**[sequenceAssignment(sequencesAssignmentInputRepresentation)](#sequenceassignmentsequencesassignmentinputrepresentation)**

Assign sequence pattern values to objects based on the configured sequence policy.

### reconcileSequences(sequenceGapReconciliationInputRepresentation)

Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.

#### API Version

65.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.sequenceGapReconciliationOutputRepresentation reconcileSequences(ConnectApi.sequenceGapReconciliationInputRepresentation sequenceGapReconciliationInputRepresentation)`

#### Parameters

***sequenceGapReconciliationInputRepresentation***

Type: [`ConnectApi.SequenceGapReconciliationInputRepresentation`](./apex-connectapi-input-sequence-gap-reconciliation.md)

The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

#### Return Value

Type: [`ConnectApi.SequenceGapReconciliationOutputRepresentation`](./apex-connectapi-output-sequence-gap-reconciliation-output.md)

#### Usage

You need the Billing Admin permission set to use this method.

### sequenceAssignment(sequencesAssignmentInputRepresentation)

Assign sequence pattern values to objects based on the configured sequence policy.

#### API Version

65.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.SequencesAssignmentOutputRepresentation sequenceAssignment(ConnectApi.SequencesAssignmentInputRepresentation sequencesAssignmentInputRepresentation)`

#### Parameters

***sequencesAssignmentInputRepresentation***

Type: [`ConnectApi.SequencesAssignmentInputRepresentation`](./apex-connectapi-input-sequences-assignment.md)

The details of the target objects to which the sequence pattern values are assigned.

#### Return Value

Type: [`ConnectApi.SequencesAssignmentOutputRepresentation`](./apex-connectapi-output-sequences-assignment-output.md)

#### Usage

You need the Billing Admin permission set to use this method.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-sequencingwithoutaura-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
