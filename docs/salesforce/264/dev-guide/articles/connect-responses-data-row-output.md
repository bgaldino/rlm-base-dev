---
page_id: connect-responses-data-row-output
title: Data Row
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-data-row-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_data_row_output.htm
fetched_at: 2026-11-25
---

# Data Row

Output representation of the details of a data row.

## JSON Example

```
{
  "keyToUomDataRowOutput": {
    "PRC1": {
      "key": "PRC1",
      "fieldApiNameToFieldDataOutput": {
        "MaxQuantity": {
          "fieldApiName": "MaxQuantity",
          "originalValue": 1234.5678,
          "isRoundingApplicable": true,
          "roundedValue": 1234.56,
          "unitOfMeasureId": "uomId1",
          "errorCodeToErrorMap" : []
        },
        "MinQuantity": {
          "fieldApiName": "MinQuantity",
          "originalValue": 643.1,
          "isRoundingApplicable": true,
          "roundedValue": 643.1,
          "unitOfMeasureId": "uomId1"
        }
      },
      "errorCodeToErrorMap" : []
    },
    "PRC2": {
      "key": "PRC2",
      "fieldApiNameToFieldDataOutput": {
        "MaxQuantity": {
          "fieldApiName": "MaxQuantity",
          "originalValue": 1234.5678,
          "isRoundingApplicable": true,
          "roundedValue": 1234.56,
          "unitOfMeasureId": "uomId1"
        },
        "MinQuantity": {
          "fieldApiName": "MinQuantity",
          "originalValue": 987.4628,
          "isRoundingApplicable": true,
          "errorCodeToErrorMap": {
            "message": "arithrmetic operation"
          },
          "unitOfMeasureId": "uomId1"
        }
      },
      "errorCodeToErrorMap": []
    },
    "PRC3": {
      "key": "PRC3",
      "fieldApiNameToFieldDataOutput": {
        "MaxQuantity": {
          "fieldApiName": "MaxQuantity",
          "originalValue": 1234.5678,
          "isRoundingApplicable": false,
          "unitOfMeasureId": "uomId2"
        },
        "MinQuantity": {
          "fieldApiName": "MinQuantity",
          "originalValue": 987.4628,
          "isRoundingApplicable": false,
          "unitOfMeasureId": "uomId2"
        }
      },
      "errorCodeToErrorMap": []
    }
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect-responses-unit-of-measure-error-output.md)> | Map of error codes to their details. | Small, 63.0 | 63.0 |
| `fieldApi​NameToField​DataOutput` | Map<String, [Field Data](./connect-responses-field-data-output.md)> | Map of field API name to associated field data. | Small, 63.0 | 63.0 |
| `key` | String | Unique key of the data row. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-data-row-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
