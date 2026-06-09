---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm
title: WriteOffInvoiceInput Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-06-09
---

# WriteOffInvoiceInput Class

Contains invoice details that are used for the request to write off an
invoice.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md "Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.")

- **[WriteOffInvoiceInput Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_constructors)**  
  Learn more about the constructors available with the WriteOffInvoiceInput class.
- **[WriteOffInvoiceInput Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_properties)**  
  Learn more about the properties available with the WriteOffInvoiceInput class.

## WriteOffInvoiceInput Constructors

Learn more about the constructors available with the WriteOffInvoiceInput
class.

The `WriteOffInvoiceInput` class includes these
constructors.

- **[WriteOffInvoiceInput(invoiceId, reasonCode, reason)](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_ctor)**  
  Initializes the WriteOffInvoiceInput class that stores the invoice details and reason for writing off invoices.
- **[WriteOffInvoiceInput()](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_ctor_2)**  
  Initializes the WriteOffInvoiceInput class.

### WriteOffInvoiceInput(invoiceId, reasonCode, reason)

Initializes the WriteOffInvoiceInput class that stores the invoice details and reason for
writing off invoices.

#### Signature

`public WriteOffInvoiceInput(String invoiceId, String reasonCode, String reason)`

#### Parameters

invoiceId
:   Type: String
:   ID of the invoice record that you want to write off.

reasonCode
:   Type: String
:   Code that categorizes the write-off reason. For example, if the reason for the
    invoice write-off is a disputed amount, the reason code can be Disputed
    Amount (DA).

reason
:   Type: String
:   Reason for writing off invoices.

### WriteOffInvoiceInput()

Initializes the WriteOffInvoiceInput class.

#### Signature

`public WriteOffInvoiceInput()`

## WriteOffInvoiceInput Properties

Learn more about the properties available with the WriteOffInvoiceInput
class.

The `WriteOffInvoiceInput` class includes these
properties.

- **[invoiceId](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_invoiceId)**  
  Sets the ID of the invoice record that must be written off.
- **[reason](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_reason)**  
  Sets the reason for writing off invoices.
- **[reasonCode](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceInput_reasonCode)**  
  Sets the code that categorizes the write-off reason.

### invoiceId

Sets the ID of the invoice record that must be written off.

#### Signature

`public String invoiceId {get; set;}`

#### Property Value

Type: String

### reason

Sets the reason for writing off invoices.

#### Signature

`public String reason {get; set;}`

#### Property Value

Type: String

### reasonCode

Sets the code that categorizes the write-off reason.

#### Signature

`public String reasonCode {get; set;}`

#### Property Value

Type: String
