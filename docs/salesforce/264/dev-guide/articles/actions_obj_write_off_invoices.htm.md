---
page_id: actions_obj_write_off_invoices.htm
title: Write Off Invoices Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_write_off_invoices.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-11-23
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

**Authentication:** `Authorization: Bearer token`

**Notes:** You can also call the associated Connect REST API endpoint or InvoiceWriteOff Apex methods. See [Posted Invoice List Write-Off (POST)](./connect_resources_write_off_invoices.htm.md) API or [InvoiceWriteOff Namespace](./apex_namespace_InvoiceWriteOff.htm.md).

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| writeOffInvoiceInputList | Apex-defined | Required. A collection of Apex input records that contain details about the invoices to be written off. See [InvoiceWriteOff Namespace](./apex_namespace_InvoiceWriteOff.htm.md) for the list of input parameters. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| writeOffInvoiceResponseList | Apex-defined | A collection of Apex output records that contain details about the invoices that were written off. See [InvoiceWriteOff Namespace](./apex_namespace_InvoiceWriteOff.htm.md) for the list of output parameters. |

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_write_off_invoices.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
