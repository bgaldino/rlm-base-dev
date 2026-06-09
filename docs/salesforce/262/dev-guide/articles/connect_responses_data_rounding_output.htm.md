---
page_id: connect_responses_data_rounding_output.htm
title: Data Rounding
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_data_rounding_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Data Rounding

Output representation of the data rounding response.

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
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 63.0 | 63.0 |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md "Output representation of the details of errors encountered during the processing of the Unit of Measure API request.")> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `keyToData​RowOutput` | Map<String, [Data Row](./connect_responses_data_row_output.htm.md "Output representation of the details of a data row.")> | Data row key mapped to the associated data row. | Small, 63.0 | 63.0 |
| `status` | [Unit Of Measure Status](./connect_responses_unit_of_measure_status.htm.md "Output representation of the status of the Unit of Measure API request.")[] | Status of the API request. | Small, 63.0 | 63.0 |
