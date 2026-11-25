---
page_id: connect-responses-configurator-unit-of-measure-output
title: Configurator Unit Of Measure
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configurator-unit-of-measure-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_configurator_unit_of_measure_output.htm
fetched_at: 2026-11-25
---

# Configurator Unit Of Measure

Output representation of the details of the unit of measure record.

## JSON Example

```
{
  "unitOfMeasure": {
    "id": "0hEXR00000000BJ2AY",
    "name": "Litres",
    "roundingMethod": "Down",
    "scale": 2,
    "unitCode": "Ltrs"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the unit of measure record. | Small, 63.0 | 63.0 |
| `name` | String | Name of the unit of measure record. | Small, 63.0 | 63.0 |
| `rounding​Method` | String | Rounding method associated with the unit of measure record. | Small, 63.0 | 63.0 |
| `scale` | Integer | Scale associated with the unit of measure record. | Small, 63.0 | 63.0 |
| `unitCode` | String | Unit code associated with the unit of measure record. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configurator-unit-of-measure-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
