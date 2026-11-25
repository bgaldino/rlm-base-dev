---
page_id: connect-responses-data-rounding-output
title: Data Rounding
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-data-rounding-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_data_rounding_output.htm
fetched_at: 2026-11-25
---

# Data Rounding

Output representation of the data rounding response.

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
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 63.0 | 63.0 |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect-responses-unit-of-measure-error-output.md)> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `keyToData​RowOutput` | Map<String, [Data Row](./connect-responses-data-row-output.md)> | Data row key mapped to the associated data row. | Small, 63.0 | 63.0 |
| `status` | [Unit Of Measure Status](./connect-responses-unit-of-measure-status.md)[] | Status of the API request. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-data-rounding-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
