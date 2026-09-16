---
page_id: apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm
title: RecordWithReferenceRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# RecordWithReferenceRequest Class

Contains constructors and properties to associate a record object with a reference
    identifier.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md)

    

## Example

      
      

```
RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
```

    

- 
**[RecordWithReferenceRequest Constructors](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_RevSalesTrxn_RecordWithReferenceRequest_constructors)**  

Learn more about the available constructors with the RecordWithReferenceRequest     class.

- 
**[RecordWithReferenceRequest Properties](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_RevSalesTrxn_RecordWithReferenceRequest_properties)**  

Learn more about the available properties with the RecordWithReferenceRequest     class.

  

## RecordWithReferenceRequest Constructors

  
  
  
Learn more about the available constructors with the RecordWithReferenceRequest
    class.

    
      

The `RecordWithReferenceRequest` class includes these
        constructors.

    

    
  

- 
**[RecordWithReferenceRequest(referenceId, record)](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_RevSalesTrxn_RecordWithReferenceRequest_ctor)**  

Creates an instance of the RecordWithReferenceRequest class to associate a record object     with a reference identifier by using the referenceId and record object properties.

### RecordWithReferenceRequest(referenceId, record)

Creates an instance of the RecordWithReferenceRequest class to associate a record object
    with a reference identifier by using the referenceId and record object properties.

#### Signature

`public RecordWithReferenceRequest(String referenceId, RevSalesTrxn.RecordResource record)`

#### Parameters

**referenceId**

: Type: String

: Reference ID that maps to the subrequest response and can be used to reference the response in
            subsequent subrequests. You can reference the referenceId in either the body or URL of a
            subrequest. Use this syntax to include a reference: @{referenceId.FieldName}. See [referenceId property of a
              composite subrequest](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_rest.meta/api_rest/resources_composite_graph_composite_subrequest.htm).

**record**

: Type: [RevSalesTrxn.RecordResource](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_class_RevSalesTrxn_RecordResource)

: Record object that’s defined using the `RecordResource`
            class.

  

## RecordWithReferenceRequest Properties

  
  
  
Learn more about the available properties with the RecordWithReferenceRequest
    class.

    
      

The `RecordWithReferenceRequest` class has these
        properties.

    

    
  

- 
**[record](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_RevSalesTrxn_RecordWithReferenceRequest_record)**  

Set the record property to specify the record object that’s defined by using the     RecordResource class.

- 
**[referenceId](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_RevSalesTrxn_RecordWithReferenceRequest_referenceId)**  

Set the referenceId property to specify the reference ID that maps to the subrequest     response. This reference ID can be used to reference the response in subsequent     subrequests.

### record

Set the record property to specify the record object that’s defined by using the
    RecordResource class.

#### Signature

`public RevSalesTrxn.RecordResource record {get; set;}`

#### Property Value

Type: [RevSalesTrxn.RecordResource](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_class_RevSalesTrxn_RecordResource)

### referenceId

Set the referenceId property to specify the reference ID that maps to the subrequest
    response. This reference ID can be used to reference the response in subsequent
    subrequests.

#### Signature

`public String referenceId {get; set;}`

#### Property Value

Type: String
