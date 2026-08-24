---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm
title: WriteOffInvoiceResponseList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# WriteOffInvoiceResponseList Class

Contains properties to store the response details of the list of invoices that are
    written off.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md)

- 
**[WriteOffInvoiceResponseList Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseList_constructors)**  

Learn more about the constructors available with the WriteOffInvoiceResponseList     class.

- 
**[WriteOffInvoiceResponseList Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseList_properties)**  

Learn more about the properties available with the WriteOffInvoiceResponseList     class.

  

## WriteOffInvoiceResponseList Constructors

  
  
  
Learn more about the constructors available with the WriteOffInvoiceResponseList
    class.

    
      

The `WriteOffInvoiceResponseList` class includes these
        constructors.

    

- 
**[WriteOffInvoiceResponseList(writeOffInvoiceResponseList)](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseList_ctor)**  

Initializes the WriteOffInvoiceResponseList class that stores the response details of the     list of invoices that are written off.

- 
**[WriteOffInvoiceResponseList()](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseList_ctor_2)**  

Initializes the WriteOffInvoiceResponseList class.

### WriteOffInvoiceResponseList(writeOffInvoiceResponseList)

Initializes the WriteOffInvoiceResponseList class that stores the response details of the
    list of invoices that are written off.

#### Signature

`public WriteOffInvoiceResponseList(List<InvoiceWriteOff.WriteOffInvoiceResponse> writeOffInvoiceResponseList)`

#### Parameters

**writeOffInvoiceResponseList**

: Type: List<[InvoiceWriteOff.WriteOffInvoiceResponse](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponse)>

: 

Details of the invoices for which the write-off process is initiated.

### WriteOffInvoiceResponseList()

Initializes the WriteOffInvoiceResponseList class.

#### Signature

`public WriteOffInvoiceResponseList()`

  

## WriteOffInvoiceResponseList Properties

  
  
  
Learn more about the properties available with the WriteOffInvoiceResponseList
    class.

    
      

The `WriteOffInvoiceResponseList` class includes these
        properties.

    

- 
**[writeOffInvoiceResponseList](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseList_writeOffInvoiceResponseList)**  

Get the details of the invoices for which the write-off posted invoice process is     initiated.

### writeOffInvoiceResponseList

Get the details of the invoices for which the write-off posted invoice process is
    initiated.

#### Signature

`public List<InvoiceWriteOff.WriteOffInvoiceResponse> writeOffInvoiceResponseList {get; set;}`

#### Property Value

Type: List<[InvoiceWriteOff.WriteOffInvoiceResponse](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponse)>
