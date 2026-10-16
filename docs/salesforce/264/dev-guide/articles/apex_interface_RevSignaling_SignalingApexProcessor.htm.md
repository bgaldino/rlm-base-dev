---
page_id: apex_interface_RevSignaling_SignalingApexProcessor.htm
title: SignalingApexProcessor Interface
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_interface_RevSignaling_SignalingApexProcessor.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: apex_namespace_RevSignaling.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# SignalingApexProcessor Interface

Defines the context-driven orchestration logic based on procedure plan instance and
        contextual instance.

## Namespace

[RevSignaling](./apex_namespace_RevSignaling.htm.md)

## Usage

Here's a sample implementation of the SignalingApexProcessor
                interface.

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

Refer to [Customize Your Pricing
                    Procedures With Apex Hooks](https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm&language=en_US) for additional samples that cover unique
                pricing scenarios by implementing this interface.

- 
**[SignalingApexProcessor Methods](./apex_interface_RevSignaling_SignalingApexProcessor.htm.md#apex_RevSignaling_SignalingApexProcessor_methods)**  

The SignalingApexProcessor method executes the specified transaction request, which     returns the corresponding response.

- 
**[SignalingApexProcessor Example Implementation](./apex_interface_RevSignaling_SignalingApexProcessor.htm.md#apex_interface_RevSignaling_SignalingApexProcessor_Example)**  

Refer to the example implementation of the SignalingApexProcessor interface to define a     context-driven orchestration logic.

  

## SignalingApexProcessor Methods

  
  
  
The SignalingApexProcessor method executes the specified transaction request, which
    returns the corresponding response.

    
      

The `SignalingApexProcessor` class includes these
        methods.

    

    
  

- 
**[execute(var1)](./apex_interface_RevSignaling_SignalingApexProcessor.htm.md#apex_RevSignaling_SignalingApexProcessor_execute)**  

Executes the parameter that's specified in the instance of a transaction     request.

### execute(var1)

Executes the parameter that's specified in the instance of a transaction
    request.

#### Signature

`public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest var1)`

```
RevSignaling.SignalingApexProcessor, execute, [RevSignaling.TransactionRequest], RevSignaling.TransactionResponse
```

#### Parameters

**var1**

: Type: [RevSignaling.TransactionRequest](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_class_RevSignaling_TransactionRequest)

: Instance of the TransactionRequest class containing the execution parameter.

#### Return Value

Type: [RevSignaling.TransactionResponse](./apex_class_RevSignaling_TransactionResponse.htm.md#apex_class_RevSignaling_TransactionResponse)

Response from the orchestration.

## SignalingApexProcessor Example Implementation

  
Refer to the example implementation of the SignalingApexProcessor interface to define a
    context-driven orchestration logic.

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
