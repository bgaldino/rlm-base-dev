---
page_id: connect_resources_unit_of_measure_rounded_data.htm
title: Unit of Measure Rounded Data (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_unit_of_measure_rounded_data.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Unit of Measure Rounded Data (POST)

Round off and scale decimal data for a specific set of
fields.

Resource
:   ```
    /connect/pcm/unit-of-measure/rounded-data
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/unit-of-measure/rounded-data
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "dataRowInputs": [
            {
              "key": "PRC1",
              "fieldDataInputs": [
                {
                  "fieldApiName": "MaxQuantity",
                  "originalValue": 1234.5678,
                  "unitOfMeasureId": "0hExx0000000001EAA"
                },
                {
                  "fieldApiName": "MinQuantity",
                  "originalValue": "987462848934739347.32232590183756545",
                  "unitOfMeasureId": "0hExx000000001dEAA"
                }
              ]
            },
            {
              "key": "PRC2",
              "fieldDataInputs": [
                {
                  "fieldApiName": "MaxQuantity",
                  "originalValue": 1234.5678,
                  "unitOfMeasureId": "uomId1"
                },
                {
                  "fieldApiName": "MinQuantity",
                  "originalValue": 987.4628,
                  "unitOfMeasureId": "Kgs Id"
                }
              ]
            },
            {
              "key": "PRC3",
              "fieldDataInputs": [
                {
                  "fieldApiName": "MaxQuantity",
                  "originalValue": 0.437584,
                  "unitOfMeasureId": "uomId2"
                },
                {
                  "fieldApiName": "MinQuantity",
                  "originalValue": 7364.58923,
                  "unitOfMeasureId": "uomId2"
                }
              ]
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 63.0 |
        | `dataRow​Inputs` | [Data Row Input](./connect_requests_data_row_input.htm.md "Input representation of the details of the input for a data rounding request.")[] | List of row inputs for rounding the data. | Required | 63.0 |

Response body for POST
:   [Data
    Rounding](./connect_responses_data_rounding_output.htm.md "Output representation of the data rounding response.")
