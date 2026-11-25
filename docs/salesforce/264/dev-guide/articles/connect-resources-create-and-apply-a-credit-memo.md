---
page_id: connect-resources-create-and-apply-a-credit-memo
title: Create and Apply Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-and-apply-a-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_create_and_apply_a_credit_memo.htm
fetched_at: 2026-11-25
---

# Create and Apply Credit Memo (POST)

Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.

Use this API to adjust an outstanding invoice balance or rectify errors in an invoice. In the API request, pass a list of invoice lines to credit. Keep these considerations in mind when you use this API.

- The request must contain at least one invoice line. Each invoice line must have the invoice line’s ID, the amount to credit, and any optional tax details. The invoice lines must be a part of the invoice passed in the resource.

- The amount to credit must not exceed the charge or adjustment amount of an individual invoice line.

- The request body’s credit amount inclusive of taxes must not exceed the target invoice line’s amount inclusive of taxes, except for taxes calculated through an external tax service.

- The request body’s total credit amount inclusive of taxes calculated through an external tax service must not exceed the outstanding invoice balance, which is also inclusive of taxes.

This API creates and posts a credit memo. The credit memo has one credit memo line for each invoice line passed in the API request. The invoice balance reduces by a value equal to the credit memo’s balance. This API modifies the balance of a posted invoice or invoice line based on the specified credit application level for your org. See [Apply Credits to Posted Invoices or Invoice Lines](https://help.salesforce.com/s/articleView?id=sf.billing_setup_credit_application_level.htm).

## Special Access Rules

You need the Credit Memo Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/invoices/{invoiceId}/actions/credit
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/{3ttR000000008NEIAY}/actions/credit
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoice​Id` | String | ID of the invoice to be credited partially or fully. The status of the invoice must be `Posted`. | Required | 62.0 |

## Request Body for POST

**JSON Example**

This example shows a sample request with the `Calculate` tax strategy.

```
{
  "type": "POSTED",
  "taxStrategy": "Calculate",
  "taxEffectiveDate": "2024-07-20",
  "effectiveDate": "2024-07-20",
  "description": "Credit Invoice",
  "invoiceLines": [
    {
      "invoiceLineId": "5TVR00000004SiqOBE",
      "amountToCredit": 5
    }
  ]
}
```

This example shows a sample request with the `CopyFromInvoiceLine` tax strategy.

```
{
  "type": "POSTED",
  "taxStrategy": "CopyFromInvoiceLine",
  "effectiveDate": "2020-05-22",
  "description": "Credit Invoice",
  "invoiceLines": [
    {
      "invoiceLineId": "5TVR00000004SiqOBE",
      "amountToCredit": "5",
      "taxStrategy": "CopyFromInvoiceLine"
    }
  ]
}
```

This example shows a sample request with the `ManualOverride` and `CopyFromInvoiceLine` tax strategies.

```
{
  "type": "POSTED",
  "taxStrategy": "ManualOverride",
  "taxEffectiveDate": "2021-08-01",
  "effectiveDate": "2021-08-01",
  "description": "Credit issued because product was malfunctioning.",
  "invoiceLines": [
    {
      "invoiceLineId": "5TVR00000004SiqOBE",
      "amountToCredit": 100,
      "taxStrategy": "ManualOverride",
      "taxEffectiveDate": "2021-08-01T21:22:41.000Z",
      "taxes": [
        {
          "taxAmount": 15,
          "taxName": "abc",
          "taxCode": "taxCode",
          "taxRate": 7
        }
      ],
      "addresses": {
        "billingAddress": {
          "street": "1 Market St #300",
          "city": "San Francisco",
          "state": "CA",
          "country": "US",
          "postalCode": "94105",
          "latitude": "37.789901",
          "longitude": "-122.396923"
        },
        "shippingAddress": {
          "street": "415 Mission St",
          "city": "San Francisco",
          "state": "CA",
          "country": "US",
          "postalCode": "94105",
          "latitude": "37.789901",
          "longitude": "-122.396923"
        }
      }
    },
    {
      "invoiceLineId": "5TVR00000004SiqOAE",
      "amountToCredit": 200,
      "taxStrategy": "CopyFromInvoiceLine"
    }
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description for the credit memo to be created. | Optional | 62.0 |
| `effective​Date` | String | Date when the credit memo takes effect. | Optional | 62.0 |
| `invoice​Lines` | [Credit Invoice Line Input](./connect-requests-credit-invoice-line-input.md)[] | List of the invoice lines to be credited. The invoice line IDs must be related to the invoice ID specified in the API request. If invoice lines aren’t specified, the API request results in an error. | Required | 62.0 |
| `taxEffective​Date` | String | Date when the tax takes effect to recalculate the taxes. | Optional | 62.0 |
| `tax​Strategy` | String |  | Required | 62.0 |
| `type` | String |  | Optional | 62.0 |

Supported values:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `ManualOverride`—Specifies that the provided tax values must be considered for taxes.

- `CopyFromInvoiceLine`—Specifies that tax values must be copied from the invoice line.

- `Calculate`—Specifies that tax must be calculated by using the API.

## Response Body for POST

[Revenue Async Line Level](./connect-responses-revenue-async-line-level.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-and-apply-a-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
