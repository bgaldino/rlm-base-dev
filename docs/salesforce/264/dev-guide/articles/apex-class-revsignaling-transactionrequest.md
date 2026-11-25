---
page_id: apex-class-revsignaling-transactionrequest
title: TransactionRequest Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsignaling-transactionrequest.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: apex-namespace-revsignaling
legacy_page_id: apex_class_RevSignaling_TransactionRequest.htm
fetched_at: 2026-11-25
---

# TransactionRequest Class

Represents the transaction request to the signaling Apex processor.

## Namespace

[RevSignaling](./apex-namespace-revsignaling.md)

- 

**[TransactionRequest Constructors](#transactionrequest-constructors)**

Learn more about the available constructors with the TransactionRequest class.

- 

**[TransactionRequest Properties](#transactionrequest-properties)**

Learn more about the properties that are available with the TransactionRequest class.

## TransactionRequest Constructors

Learn more about the available constructors with the TransactionRequest class.

The `TransactionRequest` class includes these constructors.

- 

**[TransactionRequest(procedurePlanInstance, ctxInstanceId)](#transactionrequestprocedureplaninstance-ctxinstanceid)**

Creates an instance of the TransactionRequest class to specify the procedure plan and context instance ID.

### TransactionRequest(procedurePlanInstance, ctxInstanceId)

Creates an instance of the TransactionRequest class to specify the procedure plan and context instance ID.

#### Signature

`public TransactionRequest(RevSignaling.ProcedurePlan procedurePlan, String ctxInstanceId)`

#### Parameters

***procedurePlan***

Type: [RevSignaling.ProcedurePlan](./apex-class-revsignaling-procedureplan.md#procedureplan-class)

Instance of the procedure plan.

***ctxInstanceId***

Type: String

ID of the context.

## TransactionRequest Properties

Learn more about the properties that are available with the TransactionRequest class.

The `TransactionRequest` class includes these properties.

- 

**[ctxInstanceId](#ctxinstanceid)**

Set the context ID.

- 

**[procedurePlanInstance](#procedureplaninstance)**

Set the instance of the procedure plan.

### ctxInstanceId

Set the context ID.

#### Signature

`public String ctxInstanceId {get; set;}`

#### Property Value

Type: String

### procedurePlanInstance

Set the instance of the procedure plan.

#### Signature

`public RevSignaling.ProcedurePlan procedurePlanInstance {get; set;}`

#### Property Value

Type: [RevSignaling.ProcedurePlan](./apex-class-revsignaling-procedureplan.md#procedureplan-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsignaling-transactionrequest.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
