---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm
title: WriteOffInvoiceInputList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-06-09
---

# WriteOffInvoiceInputList Class

Contains invoice details to write off a list of posted invoices.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md "Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.")

- **[WriteOffInvoiceInputList Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_constructors)**  
  Learn more about the constructors available with the WriteOffInvoiceInputList class.
- **[WriteOffInvoiceInputList Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_properties)**  
  Learn more about the properties available with the WriteOffInvoiceInputList class.

## WriteOffInvoiceInputList Constructors

Learn more about the constructors available with the WriteOffInvoiceInputList
class.

The `WriteOffInvoiceInputList` class includes these
constructors.

- **[WriteOffInvoiceInputList(writeOffInvoiceInputList)](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_ctor)**  
  Initializes the WriteOffInvoiceInputList class that stores the details of invoices that you want to write off.
- **[WriteOffInvoiceInputList()](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_ctor_2)**  
  Initializes the WriteOffInvoiceInputList class.

### WriteOffInvoiceInputList(writeOffInvoiceInputList)

Initializes the WriteOffInvoiceInputList class that stores the details of invoices that
you want to write off.

#### Signature

`public WriteOffInvoiceInputList(List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList)`

#### Parameters

writeOffInvoiceInputList
:   Type: List<I[nvoiceWriteOff.WriteOffInvoiceInput](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput "Contains invoice details that are used for the request to write off an invoice.")>
:   Input representation of the request to write off a list of posted invoices.

### WriteOffInvoiceInputList()

Initializes the WriteOffInvoiceInputList class.

#### Signature

`public WriteOffInvoiceInputList()`

## WriteOffInvoiceInputList Properties

Learn more about the properties available with the WriteOffInvoiceInputList
class.

The `WriteOffInvoiceInputList` class includes these
properties.

- **[writeOffInvoiceInputList](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInputList_writeOffInvoiceInputList)**  
  Input representation of the request to write off a list of posted invoices.

### writeOffInvoiceInputList

Input representation of the request to write off a list of posted invoices.

#### Signature

`public List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList {get; set;}`

#### Property Value

Type: List<[nvoiceWriteOff.WriteOffInvoiceInput](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput "Contains invoice details that are used for the request to write off an invoice.")>
