---
page_id: apex-namespace-revsignaling
title: RevSignaling Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-revsignaling.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-apex-reference
legacy_page_id: apex_namespace_RevSignaling.htm
fetched_at: 2026-11-25
---

# RevSignaling Namespace

The RevSignaling Namespace includes properties and methods to extend the standard procedure plan implementation through custom logic. Using this extension support, you can tailor implementations to your unique requirements.

## Usage

To use this namespace, enable the **Procedure Plan Orchestration for Pricing** toggle from the Revenue Settings page from Setup.

The `RevSignaling` namespace includes these classes.

- 

**[ProcedurePlan Class](./apex-class-revsignaling-procedureplan.md#procedureplan-class)**

Represents the instance of the current pricing procedure plan that you’re working on.

- 

**[SignalingApexProcessor Interface](./apex-interface-revsignaling-signalingapexprocessor.md#signalingapexprocessor-interface)**

Defines the context-driven orchestration logic based on procedure plan instance and contextual instance.

- 

**[TransactionRequest Class](./apex-class-revsignaling-transactionrequest.md#transactionrequest-class)**

Represents the transaction request to the signaling Apex processor.

- 

**[TransactionResponse Class](./apex-class-revsignaling-transactionresponse.md#transactionresponse-class)**

Represents the transaction response from the signaling Apex processor.

- 

**[TransactionStatus Enum](./apex-enum-revsignaling-transactionstatus.md)**

Specifies the status of the transaction request.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-revsignaling.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
