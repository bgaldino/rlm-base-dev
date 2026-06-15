---
page_id: connect_responses_data_row_output.htm
title: Data Row
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_data_row_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Data Row

Output representation of the details of a data row.

JSON example
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md "Output representation of the details of errors encountered during the processing of the Unit of Measure API request.")> | Map of error codes to their details. | Small, 63.0 | 63.0 |
| `fieldApi​NameToField​DataOutput` | Map<String, [Field Data](./connect_responses_field_data_output.htm.md "Output representation of the field data.")> | Map of field API name to associated field data. | Small, 63.0 | 63.0 |
| `key` | String | Unique key of the data row. | Small, 63.0 | 63.0 |
