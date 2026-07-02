---
page_id: apex_class_RevSignaling_TransactionRequest.htm
title: TransactionRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSignaling_TransactionRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: apex_namespace_RevSignaling.htm
fetched_at: 2026-06-09
---

# TransactionRequest Class

Represents the transaction request to the signaling Apex processor.

## Namespace

[RevSignaling](./apex_namespace_RevSignaling.htm.md "The RevSignaling Namespace includes properties and methods to extend the standard procedure plan implementation through custom logic. Using this extension support, you can tailor implementations to your unique requirements.")

- **[TransactionRequest Constructors](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_RevSignaling_TransactionRequest_constructors)**  
  Learn more about the available constructors with the TransactionRequest class.
- **[TransactionRequest Properties](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_RevSignaling_TransactionRequest_properties)**  
  Learn more about the properties that are available with the TransactionRequest class.

## TransactionRequest Constructors

Learn more about the available constructors with the TransactionRequest
class.

The `TransactionRequest` class includes these
constructors.

- **[TransactionRequest(procedurePlanInstance, ctxInstanceId)](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_RevSignaling_TransactionRequest_ctor)**  
  Creates an instance of the TransactionRequest class to specify the procedure plan and context instance ID.

### TransactionRequest(procedurePlanInstance, ctxInstanceId)

Creates an instance of the TransactionRequest class to specify the procedure plan and
context instance ID.

#### Signature

`public TransactionRequest(RevSignaling.ProcedurePlan procedurePlan, String ctxInstanceId)`

```
RevSignaling.TransactionRequest, newinstance, [RevSignaling.ProcedurePlan, String], RevSignaling.TransactionRequest
```

#### Parameters

procedurePlan
:   Type: [RevSignaling.ProcedurePlan](./apex_class_RevSignaling_ProcedurePlan.htm.md#apex_class_RevSignaling_ProcedurePlan "Represents the instance of the current pricing procedure plan that you're working on.")
:   Instance of the procedure plan.

ctxInstanceId
:   Type: String
:   ID of the context.

## TransactionRequest Properties

Learn more about the properties that are available with the TransactionRequest
class.

The `TransactionRequest` class includes these
properties.

- **[ctxInstanceId](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_RevSignaling_TransactionRequest_ctxInstanceId)**  
  Set the context ID.
- **[procedurePlanInstance](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_RevSignaling_TransactionRequest_procedurePlanInstance)**  
  Set the instance of the procedure plan.

### ctxInstanceId

Set the context ID.

#### Signature

`public String ctxInstanceId {get; set;}`

```
RevSignaling.TransactionRequest, ctxInstanceId
```

#### Property Value

Type: String

### procedurePlanInstance

Set the instance of the procedure plan.

#### Signature

`public RevSignaling.ProcedurePlan procedurePlanInstance {get; set;}`

```
RevSignaling.TransactionRequest, procedurePlanInstance
```

#### Property Value

Type: [RevSignaling.ProcedurePlan](./apex_class_RevSignaling_ProcedurePlan.htm.md#apex_class_RevSignaling_ProcedurePlan "Represents the instance of the current pricing procedure plan that you're working on.")
