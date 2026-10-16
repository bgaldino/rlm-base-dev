---
page_id: apex_namespace_InvoiceWriteOff.htm
title: InvoiceWriteOff Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_InvoiceWriteOff.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_reference.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# InvoiceWriteOff Namespace

Create credit memos with the total charge amount on the invoice as the write-off amount
    and close the invoice.

The `InvoiceWriteOff` namespace includes these classes.

    

## Usage

      
      

You need the Billing Operations User or Credit Memo Operations User permission set to
        access this namespace.

    

- 
**[WriteOffInvoiceInput Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput)**  

Contains invoice details that are used for the request to write off an     invoice.

- 
**[WriteOffInvoiceInputList Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInputList)**  

Contains invoice details to write off a list of posted invoices.

- 
**[WriteOffInvoiceResponse Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponse)**  

Contains properties to store the response details to the request to write off a posted     invoice.

- 
**[WriteOffInvoiceResponseError Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError)**  

Contains properties to store the error response that's associated with a request to write     off a posted invoice.

- 
**[WriteOffInvoiceResponseList Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList)**  

Contains properties to store the response details of the list of invoices that are     written off.
