---
page_id: actions-obj-write-off-invoices
title: Write Off Invoices Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-write-off-invoices.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_write_off_invoices.htm
fetched_at: 2026-11-25
---

# Write Off Invoices Action

Write off partially paid or unpaid invoices to manage pending debts and to maintain accurate financial records. This action calls the Posted Invoice List Write-Off (POST) API.

This action is available in API version 64.0 and later.

## Special Access Rules

The Write Off Invoices action is available in Enterprise, Developer, and Unlimited Editions where Billing is enabled. To use this action, you need the Billing Operations User and Credit Memo Operations User permission sets.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/writeOffInvoices`

**Formats:** JSON, XML

**HTTP Methods:** GET

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

**Notes:** You can also call the associated Connect REST API endpoint or InvoiceWriteOff Apex methods. See [Posted Invoice List Write-Off (POST)](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_write_off_invoices.htm) API or [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_InvoiceWriteOff.htm).

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `writeOffInvoiceInputList` | Apex-defined | Required. A collection of Apex input records that contain details about the invoices to be written off. See [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_InvoiceWriteOff.htm) for the list of input parameters. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `writeOffInvoiceResponseList` | Apex-defined | A collection of Apex output records that contain details about the invoices that were written off. See [InvoiceWriteOff Namespace](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_InvoiceWriteOff.htm) for the list of output parameters. |

## Example

**GET**

This sample request is for the Write Off Invoices action.

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

This sample response is for the Write Off Invoices action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-write-off-invoices.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
