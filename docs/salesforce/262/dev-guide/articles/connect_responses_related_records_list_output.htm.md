---
page_id: connect_responses_related_records_list_output.htm
title: Related Records List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_related_records_list_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Related Records List

Output representation of the list of related records.

JSON example
:   ```
    {
      "correlationId": "f4d6b42a-d9b7-49c9-8fa8-1c7bb6fe99aa",
      "relatedRecords": [
        {
          "recordId": "01txx0000006i44AAA",
          "relatedObjectRecords": [
            {
              "count": 2,
              "records": [
                {
                  "SegmentType": "Yearly",
                  "DurationType": "Months",
                  "TrialDuration": null,
                  "ProductSellingModelId": "0jPxx000000001dEAA",
                  "ProductId": "01txx0000006i44AAA",
                  "Id": "1FTxx0000004CDtGAM",
                  "Name": "PPRS-000000005"
                },
                {
                  "SegmentType": "FreeTrial",
                  "DurationType": "Days",
                  "TrialDuration": null,
                  "ProductSellingModelId": "0jPxx000000001dEAA",
                  "ProductId": "01txx0000006i44AAA",
                  "Id": "1FTxx0000004CFUGA2",
                  "Name": "PPRS-000000006"
                }
              ],
              "relatedObjectAPIName": "ProductRampSegment"
            },
            {
              "count": 2,
              "records": [
                {
                  "UsageMetricId": "1BRxx0000004CAeGAM",
                  "UsageMetricName": "Test Usage Metric 2",
                  "UsageDefinitionProductId": null,
                  "Label": "PUG-103",
                  "Quantity": 100,
                  "Id": "1BXxx0000004CCGGA2"
                },
                {
                  "UsageMetricId": "1BRxx0000004CCGGA2",
                  "UsageMetricName": "Test Usage Metric 3",
                  "UsageDefinitionProductId": "01txx0000006i2eAAA",
                  "Label": "PUG-105",
                  "Quantity": 500,
                  "Id": "1BXxx0000004CFUGA2"
                }
              ],
              "relatedObjectAPIName": "ProductUsageGrant"
            }
          ]
        },
        {
          "recordId": "01txx0000006i5gAAA",
          "relatedObjectRecords": [
            {
              "count": 4,
              "records": [
                {
                  "SegmentType": "Yearly",
                  "DurationType": "Months",
                  "TrialDuration": null,
                  "ProductSellingModelId": "0jPxx0000000001EAA",
                  "ProductId": "01txx0000006i5gAAA",
                  "Id": "1FTxx0000004C92GAE",
                  "Name": "PPRS-000000001"
                },
                {
                  "SegmentType": "Custom",
                  "DurationType": "Days",
                  "TrialDuration": null,
                  "ProductSellingModelId": "0jPxx0000000001EAA",
                  "ProductId": "01txx0000006i5gAAA",
                  "Id": "1FTxx0000004CAeGAM",
                  "Name": "PPRS-000000002"
                },
                {
                  "SegmentType": "FreeTrial",
                  "DurationType": "Months",
                  "TrialDuration": 6,
                  "ProductSellingModelId": "0jPxx0000000001EAA",
                  "ProductId": "01txx0000006i5gAAA",
                  "Id": "1FTxx0000004CCGGA2",
                  "Name": "PPRS-000000003"
                },
                {
                  "SegmentType": "Custom",
                  "DurationType": null,
                  "TrialDuration": null,
                  "ProductSellingModelId": "0jPxx0000000001EAA",
                  "ProductId": "01txx0000006i5gAAA",
                  "Id": "1FTxx0000004CDsGAM",
                  "Name": "PPRS-000000004"
                }
              ],
              "relatedObjectAPIName": "ProductRampSegment"
            },
            {
              "count": 0,
              "records": [],
              "relatedObjectAPIName": "ProductUsageGrant"
            }
          ]
        }
      ],
      "status": {
        "code": "200",
        "errors": [
        ],
        "message": ""
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 62.0 | 62.0 |
| `related​Records` | [Related Records](./connect_responses_related_records_output.htm.md "Output representation of the list of relatedObject records for a specified record ID.")[] | List of related records. | Small, 62.0 | 62.0 |
| `status` | [Status](./connect_responses_status.htm.md "Output representation of the status of the request.")[] | Status of the API request. | Small, 62.0 | 62.0 |
