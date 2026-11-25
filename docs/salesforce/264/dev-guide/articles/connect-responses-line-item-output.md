---
page_id: connect-responses-line-item-output
title: Line Item
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-line-item-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_line_item_output.htm
fetched_at: 2026-11-25
---

# Line Item

Output representation of the details of the line item.

## JSON Example

```
{
  "lineItems": [
    {
      "addresses": {
        "shipFrom": {
          "locationCode": "67890"
        },
        "shipTo": {
          "locationCode": "12345"
        },
        "soldTo": {
          "locationCode": "12345"
        }
      },
      "amountDetails": {
        "exemptAmount": 0,
        "taxAmount": 12.5,
        "totalAmount": 100,
        "totalAmountWithTax": 112.5
      },
      "effectiveDate": "2022-03-09T10:55:38.416Z",
      "lineNumber": "001xx000003HYEiAAO",
      "productCode": "Y0001",
      "quantity": 1,
      "taxCode": "TX0001",
      "taxes": [
        {
          "exemptAmount": 0,
          "exemptReason": "NoExemption",
          "imposition": {
            "type": "General"
          },
          "jurisdiction": {
            "country": "US",
            "id": "63000",
            "level": "CIT",
            "name": "SEATTLE",
            "region": "WA",
            "stateAssignedNo": "1726"
          },
          "rate": 12.5,
          "tax": 12.5,
          "taxId": "11000378132466",
          "taxableAmount": 100
        }
      ]
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Addresses](./connect-responses-addresses-output.md) | Different types of addresses that are used for the transaction of the line item. | Big, 62.0 | 62.0 |
| `amountDetails` | [Tax Amount Details](./connect-responses-tax-amount-details-output.md) | Details of the transaction amount and the taxes applicable for the line item. | Big, 62.0 | 62.0 |
| `effectiveDate` | String | Date when the tax rules are applied on the line item. | Big, 62.0 | 62.0 |
| `lineNumber` | String | Unique identifier of the line item. | Big, 62.0 | 62.0 |
| `productCode` | String | Product code of the line item as defined by the tax engine. | Big, 62.0 | 62.0 |
| `quantity` | Double | Quantity of the line item. | Big, 62.0 | 62.0 |
| `taxCode` | String | Tax code of the line item according to the tax engine. | Big, 62.0 | 62.0 |
| `taxes` | [Tax Details](./connect-responses-tax-details-output.md) [] | Tax details of the line item. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-line-item-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
