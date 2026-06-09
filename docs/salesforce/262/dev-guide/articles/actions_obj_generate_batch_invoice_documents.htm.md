---
page_id: actions_obj_generate_batch_invoice_documents.htm
title: Generate Invoice Documents Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_generate_batch_invoice_documents.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Generate Invoice Documents Action

Asynchronously generate PDF documents for the invoices associated with
an invoice batch run record that are in the `Draft`
or `Posted` status.

This action uses the ID of the invoice batch run record to find the draft or posted invoices
from the batch and to generate the PDF documents for its invoices that are in the
`Draft` or `Posted` status. This action creates a DocGenerationBatchProcess record
that contains the Document Generation Process and Invoice Document records for each
of the invoices. This action is available in API version 63.0 and later with Revenue
Cloud Billing.

## Special Access Rules

The Generate Invoice Documents action is available in Enterprise, Unlimited, and Developer
Editions where Revenue Cloud Billing is enabled. The org must have Billing Docgen
enabled and an active Invoice Document Template to generate PDF documents. To use
this action, you need either the Billing Operations User or the Billing Admin
permission set, along with the Docgen Designer and Docgen Designer Standard User
permission sets.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/generateInvoiceDocuments`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| invoiceBatchRunId | Type  string  Description  Required.  ID of the invoice batch run record that created the draft or posted invoices. |

## Outputs

| Output | Details |
| --- | --- |
| requestId | Type  string  Description  An alphanumeric string to track the status of the document generation request. |
| requestStatus | Type  boolean  Description  Indicates whether the operation is successful (`true`) or not (`false`). |

## Example

POST
:   This example shows a sample request for the Generate Invoice Documents
    action.

    ```
    {
      "inputs": [
        {
          "invoiceBatchRunId": "5IRSG000001Az014AC"
        }
      ]
    }
    ```

    This example shows a sample response for the Generate Invoice Documents
    action.

    ```
    {
      "actionName": "generateInvoiceDocuments",
      "errors": null,
      "isSuccess": true,
      "outputValues": {
        "requestId": "4sFDU00000000652AA",
        "requestStatus": true
      }
    }
    ```
