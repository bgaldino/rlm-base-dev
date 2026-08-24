---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm
title: WriteOffInvoiceInputList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# WriteOffInvoiceInputList Class

Contains invoice details to write off a list of posted invoices.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md)

- 
**[WriteOffInvoiceInputList Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_constructors)**  

Learn more about the constructors available with the WriteOffInvoiceInputList     class.

- 
**[WriteOffInvoiceInputList Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_properties)**  

Learn more about the properties available with the WriteOffInvoiceInputList     class.

  

## WriteOffInvoiceInputList Constructors

  
  
  
Learn more about the constructors available with the WriteOffInvoiceInputList
    class.

    
      

The `WriteOffInvoiceInputList` class includes these
        constructors.

    

- 
**[WriteOffInvoiceInputList(writeOffInvoiceInputList)](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_ctor)**  

Initializes the WriteOffInvoiceInputList class that stores the details of invoices that     you want to write off.

- 
**[WriteOffInvoiceInputList()](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_ctor_2)**  

Initializes the WriteOffInvoiceInputList class.

### WriteOffInvoiceInputList(writeOffInvoiceInputList)

Initializes the WriteOffInvoiceInputList class that stores the details of invoices that
    you want to write off.

#### Signature

`public WriteOffInvoiceInputList(List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList)`

#### Parameters

**writeOffInvoiceInputList**

: Type: List<I[nvoiceWriteOff.WriteOffInvoiceInput](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput)>

: Input representation of the request to write off a list of posted invoices.

### WriteOffInvoiceInputList()

Initializes the WriteOffInvoiceInputList class.

#### Signature

`public WriteOffInvoiceInputList()`

  

## WriteOffInvoiceInputList Properties

  
  
  
Learn more about the properties available with the WriteOffInvoiceInputList
    class.

    
      

The `WriteOffInvoiceInputList` class includes these
        properties.

    

- 
**[writeOffInvoiceInputList](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_writeOffInvoiceInputList)**  

Input representation of the request to write off a list of posted invoices.

### writeOffInvoiceInputList

Input representation of the request to write off a list of posted invoices.

#### Signature

`public List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList {get; set;}`

#### Property Value

Type: List<[nvoiceWriteOff.WriteOffInvoiceInput](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput)>
