---
page_id: apex_namespace_InvoiceWriteOff.htm
title: InvoiceWriteOff Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_InvoiceWriteOff.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_reference.htm
fetched_at: 2026-06-09
---

# InvoiceWriteOff Namespace

Create credit memos with the total charge amount on the invoice as the write-off amount
and close the invoice.

The `InvoiceWriteOff` namespace includes these classes.

## Usage

You need the Billing Operations User or Credit Memo Operations User permission set to
access this namespace.

- **[WriteOffInvoiceInput Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInput)**  
  Contains invoice details that are used for the request to write off an invoice.
- **[WriteOffInvoiceInputList Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceInputList)**  
  Contains invoice details to write off a list of posted invoices.
- **[WriteOffInvoiceResponse Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponse)**  
  Contains properties to store the response details to the request to write off a posted invoice.
- **[WriteOffInvoiceResponseError Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError)**  
  Contains properties to store the error response that's associated with a request to write off a posted invoice.
- **[WriteOffInvoiceResponseList Class](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList)**  
  Contains properties to store the response details of the list of invoices that are written off.
