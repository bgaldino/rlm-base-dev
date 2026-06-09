---
page_id: actions_obj_write_off_invoices.htm
title: Write Off Invoices Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_write_off_invoices.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Write Off Invoices Action

Write off partially paid or unpaid invoices to manage pending debts
and to maintain accurate financial records. This action calls the Posted Invoice List
Write-Off (POST) API.

This action is available in API version 64.0 and later.

## Special Access Rules

The Write Off Invoices action is available in Enterprise, Developer, and Unlimited
Editions where Billing is enabled. To use this action, you need the Billing
Operations User and Credit Memo Operations User permission sets.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/writeOffInvoices`

Formats
:   JSON, XML

HTTP Methods
:   GET

Authentication
:   `Authorization:
    Bearertoken`

Notes
:   You can also call the associated Connect REST API endpoint or
    InvoiceWriteOff Apex methods. See [Posted Invoice List Write-Off
    (POST)](https://developer.salesforce.com/docs/./connect_resources_write_off_invoices.htm.md) API or [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/./apex_namespace_InvoiceWriteOff.htm.md).

## Inputs

| Input | Details |
| --- | --- |
| writeOffInvoiceInputList | Type  Apex-defined  Description  Required. A collection of Apex input records that contain details about the invoices to be written off. See [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/./apex_namespace_InvoiceWriteOff.htm.md) for the list of input parameters. |

## Outputs

| Output | Details |
| --- | --- |
| writeOffInvoiceResponseList | Type  Apex-defined  Description  A collection of Apex output records that contain details about the invoices that were written off. See [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/./apex_namespace_InvoiceWriteOff.htm.md) for the list of output parameters. |

## Example

GET
:   This sample request is for the Write Off Invoices action.

    ```
    {
      "inputs": [
        {
          "apexClass": "InvoiceWriteOff__WriteOffInvoiceInputList",
          "bytelength": 0,
          "configuration": false,
          "defaultValue": null,
          "description": "A collection of Apex WriteOffInvoiceInputList records that contain details about the invoices to be written-off.",
          "label": "WriteOffInvoiceInputList",
          "maxOccurs": 1,
          "name": "writeOffInvoiceInputList",
          "picklistValues": null,
          "placeholderText": null,
          "required": true,
          "sObjectType": null,
          "setupReferenceType": null,
          "toolingType": null,
          "type": null
        }
      ]
    }
    ```
:   This sample response is for the Write Off Invoices action.

    ```
    {
      "outputs": [
        {
          "additionalAttributes": null,
          "apexClass": "InvoiceWriteOff__WriteOffInvoiceResponseList",
          "description": "A collection Apex WriteOffInvoiceResponseList records that contain details about the invoices that were written off.",
          "label": "WriteOffInvoiceResponseList",
          "maxOccurs": 1,
          "name": "writeOffInvoiceResponseList",
          "picklistValues": null,
          "sobjectType": null,
          "type": null
        }
      ]
    }
    ```
