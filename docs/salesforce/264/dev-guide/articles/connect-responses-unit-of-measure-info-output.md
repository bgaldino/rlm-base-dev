---
page_id: connect-responses-unit-of-measure-info-output
title: Unit of Measure Info
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-unit-of-measure-info-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_unit_of_measure_info_output.htm
fetched_at: 2026-11-25
---

# Unit of Measure Info

Output representation of the details of a unit of measure record.

## JSON Example

```
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
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the unit of measure record. | Small, 63.0 | 63.0 |
| `name` | String | Name of the unit of measure record. | Small, 63.0 | 63.0 |
| `roundingMethod` | String | Data rounding method of the unit of measure record. | Small, 63.0 | 63.0 |
| `scale` | Integer | Scale of the unit of measure record. | Small, 63.0 | 63.0 |
| `unitCode` | String | Code of the unit of measure record. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-unit-of-measure-info-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
