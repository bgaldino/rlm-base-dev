---
page_id: apex_class_RulesAppln_RulesApplicationErrorResponse.htm
title: RulesApplicationErrorResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RulesAppln_RulesApplicationErrorResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_RulesAppln.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# RulesApplicationErrorResponse Class

Contains properties to store error details that occurred during the rules application.

## Namespace

[RulesAppln](./apex_namespace_RulesAppln.htm.md)

- 
**[RulesApplicationErrorResponse Constructors](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_constructors)**  

Learn more about the constructors available with the RulesApplicationErrorResponse     class.

- 
**[RulesApplicationErrorResponse Properties](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_properties)**  

Learn more about the properties available with the RulesApplicationErrorResponse     class.

  

## RulesApplicationErrorResponse Constructors

  
  
  
Learn more about the constructors available with the RulesApplicationErrorResponse
    class.

    
      

The `RulesApplicationErrorResponse` class includes these
        constructors.

    

    
  

- 
**[RulesApplicationErrorResponse(errorCode, message)](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_ctor)**  

Initializes the RulesApplicationErrorResponse class that stores error details that occurred during the rules application.

- 
**[RulesApplicationErrorResponse()](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_ctor_2)**  

Initializes an empty instance of the RulesApplicationErrorResponse class.

### RulesApplicationErrorResponse(errorCode, message)

Initializes the RulesApplicationErrorResponse class that stores error details that occurred during the rules application.

#### Signature

`public RulesApplicationErrorResponse(String errorCode, String message)`

```
RulesAppln.RulesApplicationErrorResponse, newinstance, [String, String], RulesAppln.RulesApplicationErrorResponse
```

#### Parameters

**errorCode**

: Type: String

: 

Error code that identifies the type of error that occurred during the rules application.

**message**

: Type: String

: 

Error message that describes the error that occurred during the rules application.

### RulesApplicationErrorResponse()

Initializes an empty instance of the RulesApplicationErrorResponse class.

#### Signature

`public RulesApplicationErrorResponse()`

```
RulesAppln.RulesApplicationErrorResponse, newinstance, [], RulesAppln.RulesApplicationErrorResponse
```

  

## RulesApplicationErrorResponse Properties

  
  
  
Learn more about the properties available with the RulesApplicationErrorResponse
    class.

    
      

The `RulesApplicationErrorResponse` class includes these
        properties.

    

    
  

- 
**[errorCode](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_errorCode)**  

Get the error code that identifies the type of error that occurred during the rules     application.

- 
**[message](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_RulesAppln_RulesApplicationErrorResponse_message)**  

Get the error message that describes the error that occurred during the rules     application.

### errorCode

Get the error code that identifies the type of error that occurred during the rules
    application.

#### Signature

`public String errorCode {get; set;}`

```
RulesAppln.RulesApplicationErrorResponse, errorCode
```

#### Property Value

Type: String

### message

Get the error message that describes the error that occurred during the rules
    application.

#### Signature

`public String message {get; set;}`

```
RulesAppln.RulesApplicationErrorResponse, message
```

#### Property Value

Type: String
