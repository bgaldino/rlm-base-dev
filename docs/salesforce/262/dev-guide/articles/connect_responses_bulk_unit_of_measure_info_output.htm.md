---
page_id: connect_responses_bulk_unit_of_measure_info_output.htm
title: Bulk Unit Of Measure Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_bulk_unit_of_measure_info_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Bulk Unit Of Measure Info

Output representation of the details of the unit of measure records along with error
details.

JSON example
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 63.0 | 63.0 |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md "Output representation of the details of errors encountered during the processing of the Unit of Measure API request.")> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `status` | [Unit Of Measure Status](./connect_responses_unit_of_measure_status.htm.md "Output representation of the status of the Unit of Measure API request.")[] | Status of the API request. | Small, 63.0 | 63.0 |
| `uomIdToUnit​OfMeasure​Info` | Map<String, [Unit Of Measure Info](./connect_responses_unit_of_measure_info_output.htm.md "Output representation of the details of a unit of measure record.")> | Unit of measure record IDs mapped to their details. | Small, 63.0 | 63.0 |
