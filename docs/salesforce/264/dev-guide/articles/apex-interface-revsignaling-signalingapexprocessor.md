---
page_id: apex-interface-revsignaling-signalingapexprocessor
title: SignalingApexProcessor Interface
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-interface-revsignaling-signalingapexprocessor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: apex-namespace-revsignaling
legacy_page_id: apex_interface_RevSignaling_SignalingApexProcessor.htm
fetched_at: 2026-11-25
---

# SignalingApexProcessor Interface

Defines the context-driven orchestration logic based on procedure plan instance and contextual instance.

## Namespace

[RevSignaling](./apex-namespace-revsignaling.md)

## Usage

Here’s a sample implementation of the SignalingApexProcessor interface.

```
public class SignalingApexProcessorImpl implements RevSignaling.SignalingApexProcessor {

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing SampleValidClass...');
        System.debug('Procedure Plan: ' + request.procedurePlanInstance);
        System.debug('Context Instance: ' + request.ctxInstanceId);
        
        // Add your logic here
        
        // Return the response
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Apex method was successfully executed!';
        return response;
    }
}
```

Refer to [Customize Your Pricing Procedures With Apex Hooks](https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm) for additional samples that cover unique pricing scenarios by implementing this interface.

- 

**[SignalingApexProcessor Methods](#signalingapexprocessor-methods)**

The SignalingApexProcessor method executes the specified transaction request, which returns the corresponding response.

- 

**[SignalingApexProcessor Example Implementation](#signalingapexprocessor-example-implementation)**

Refer to the example implementation of the SignalingApexProcessor interface to define a context-driven orchestration logic.

## SignalingApexProcessor Methods

The SignalingApexProcessor method executes the specified transaction request, which returns the corresponding response.

The `SignalingApexProcessor` class includes these methods.

- 

**[execute(var1)](#executevar1)**

Executes the parameter that’s specified in the instance of a transaction request.

### execute(var1)

Executes the parameter that’s specified in the instance of a transaction request.

#### Signature

`public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest var1)`

#### Parameters

***var1***

Type: [RevSignaling.TransactionRequest](./apex-class-revsignaling-transactionrequest.md#transactionrequest-class)

Instance of the TransactionRequest class containing the execution parameter.

#### Return Value

Type: [RevSignaling.TransactionResponse](./apex-class-revsignaling-transactionresponse.md#transactionresponse-class)

Response from the orchestration.

## SignalingApexProcessor Example Implementation

Refer to the example implementation of the SignalingApexProcessor interface to define a context-driven orchestration logic.

This is an example implementation of the `RevSignaling.SignalingApexProcessor` interface.

```
public class SignalingApexProcessorImpl implements RevSignaling.SignalingApexProcessor {

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing SampleValidClass...');
        System.debug('Procedure Plan: ' + request.procedurePlanInstance);
        System.debug('Context Instance: ' + request.ctxInstanceId);
        
        // Add your logic here
        
        // Return the response
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Apex method was successfully executed!';
        return response;
    }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-interface-revsignaling-signalingapexprocessor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
