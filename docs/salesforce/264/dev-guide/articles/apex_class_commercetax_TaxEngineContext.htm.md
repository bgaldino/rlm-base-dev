---
page_id: apex_class_commercetax_TaxEngineContext.htm
title: TaxEngineContext Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxEngineContext.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

    

# TaxEngineContext Class

    
    
    
Wrapper class that stores details about the type of a tax
            calculation request.

        

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md)

        

## Example

            

At the beginning of a tax adapter, use `TaxEngineContext` class to pass the value of a request type to an
                instance of `RequestType`.

            

```
global virtual class MockAdapter implements commercetax.TaxEngineAdapter {
 
     global commercetax.TaxEngineResponse processRequest(commercetax.TaxEngineContext taxEngineContext) {
         commercetax.RequestType requestType = taxEngineContext.getRequestType();
         commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest)taxEngineContext.getRequest();
```

            

Build the rest of your adapter based on the type of request that you got from `TaxEngineContext` class.

            

```
if(requestType == commercetax.RequestType.CalculateTax){
             commercetax.calculatetaxtype type = request.taxtype;
             String docCode='';
             if(request.DocumentCode == 'simulateEmptyDocumentCode')
                 docCode = '';
             else if(request.DocumentCode != null)
                 docCode =request.DocumentCode;
             else if(request.ReferenceEntityId != null) docCode = request.ReferenceEntityId;
             else docCode =  String.valueOf(getRandomInteger(0,2147483647));
             commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
             if(request.isCommit == true) {
                 response.setStatus(commercetax.TaxTransactionStatus.Committed);
             } else {
                 response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
             }
}
```

    

- 
**[TaxEngineContext Constructors](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_constructors)**  

Learn more about the available constructors with the `TaxEngineContext` class.

- 
**[TaxEngineContext Methods](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_methods)**  

Learn more about the available methods with the `TaxEngineContext` class.

  

## TaxEngineContext Constructors

  
  
  
Learn more about the available constructors with the `TaxEngineContext` class.

    
      

The `TaxEngineContext` class includes these
        constructors.

    

    
  

- 
**[TaxEngineContext(request, requestType, namedUri)](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_ctor)**  

Initializes the `TaxEngineContext`       object. This constructor is intended for test usage and throws an exception if used outside of       the Apex test context.

  

### TaxEngineContext(request, requestType,
    namedUri)

  
  
  
Initializes the `TaxEngineContext`
      object. This constructor is intended for test usage and throws an exception if used outside of
      the Apex test context.

    

#### Signature

` TaxEngineContext(commercetax.TaxEngineRequest request,
          commercetax.RequestType requestType, String namedUri)`

    

#### Parameters

        
- 
**request**:

Type: TaxEngineRequest Information about

the request.

        
- 
**requestType**:

Type: [RequestType](./apex_enum_commercetax_RequestType.htm.md)

Whether the tax request is to calculate or estimate tax.

        
- 
**namedUri**:

Type: String

URI that was called as part of the tax calculation request.

      

  

  

## TaxEngineContext Methods

  
  
  
Learn more about the available methods with the `TaxEngineContext` class.

    
      

The `TaxEngineContext` class includes these
        methods.

    

    
  

- 
**[getNamedUri()](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_getNamedUri)**  

Retrieves the value of the NamedUri field of the `TaxEngineContext` class.

- 
**[getRequest()](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_getRequest)**  

Gets the value of the `TaxEngineContext`'s Request field.

- 
**[getRequestType()](./apex_class_commercetax_TaxEngineContext.htm.md#apex_commercetax_TaxEngineContext_getRequestType)**  

Gets the value of the RequestType field of the `TaxEngineContext` class.

  

### getNamedUri()

  
  
  
Retrieves the value of the NamedUri field of the `TaxEngineContext` class.

    

#### Signature

`global String
          getNamedUri()`

    

#### Return Value

Type: String

  

  

### getRequest()

  
  
  
Gets the value of the `TaxEngineContext`'s Request field.

    

#### Signature

`global commercetax.TaxEngineRequest getRequest()`

    

#### Return Value

      
      

Type:
        TaxEngineRequest

      

An implemented instance of an external tax engine's interface for processing requests.
        We've provided the `TaxEngineRequest` interface for you to
        test within mock adapters with classes that implement it, such as [CalculateTaxRequest](./apex_class_commercetax_CalculateTaxRequest.htm.md#apex_class_commercetax_CalculateTaxRequest). However,
        don’t use it outside of a testing context.

    

  

  

### getRequestType()

  
  
  
Gets the value of the RequestType field of the `TaxEngineContext` class.

    

#### Signature

`global commercetax.RequestType getRequestType()`

    

#### Return Value

Type: [RequestType](./apex_enum_commercetax_RequestType.htm.md)

Indicates whether the calculation request was for actual or calculated tax.
