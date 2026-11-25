---
page_id: connect-responses-bulk-unit-of-measure-info-output
title: Bulk Unit Of Measure Info
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-bulk-unit-of-measure-info-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_bulk_unit_of_measure_info_output.htm
fetched_at: 2026-11-25
---

# Bulk Unit Of Measure Info

Output representation of the details of the unit of measure records along with error details.

## JSON Example

```
{
  "correlationId": "928ea35f-8a2f-4932-9f7e-ec6cdbcabdbe",
  "errorCodeToErrorMap": {
    "UNIT_OF_MEASURE_INFO_INVALID_UOM_IDS": {
      "errorCode": "UOM_INFO_API_003",
      "messageDetail": "Invalid uomId is passed. Please specify a valid uomId.",
      "messageTitle": "Invalid uomId is passed.",
      "recordIds": [
        "sample"
      ],
      "source": "Unit_Of_Measure_Info_Api"
    }
  },
  "status": {
    "errors": [],
    "httpStatusCode": "200",
    "message": " Successfully fetched UnitOfMeasure Info. "
  },
  "uomIdToUnitOfMeasureInfo": {
    "0hEU200000003M5MAI": {
      "id": "0hEU200000003M5MAI",
      "name": "Pounds",
      "roundingMethod": "Nearest",
      "scale": 1,
      "unitCode": "Pounds"
    },
    "0hEU200000003KTMAY": {
      "id": "0hEU200000003KTMAY",
      "name": "Grams",
      "roundingMethod": "Down",
      "scale": 5,
      "unitCode": "Grams"
    }
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 63.0 | 63.0 |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect-responses-unit-of-measure-error-output.md)> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `status` | [Unit Of Measure Status](./connect-responses-unit-of-measure-status.md)[] | Status of the API request. | Small, 63.0 | 63.0 |
| `uomIdToUnit​OfMeasure​Info` | Map<String, [Unit Of Measure Info](./connect-responses-unit-of-measure-info-output.md)> | Unit of measure record IDs mapped to their details. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-bulk-unit-of-measure-info-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
