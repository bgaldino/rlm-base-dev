---
page_id: connect_responses_related_object_records_output.htm
title: Related Object Records
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_related_object_records_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Related Object Records

Output representation of the related records for a specified record ID and related object
API name.

JSON example
:   ```
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
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `count` | Integer | Total count of the related records that are returned. | Small, 62.0 | 62.0 |
| `records` | Map<String, Object> | List of related object records. | Small, 62.0 | 62.0 |
| `relatedObject​APIName` | String | API name of the related object to return the records for. | Small, 62.0 | 62.0 |
