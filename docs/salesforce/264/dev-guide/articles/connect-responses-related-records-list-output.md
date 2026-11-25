---
page_id: connect-responses-related-records-list-output
title: Related Records List
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-related-records-list-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_related_records_list_output.htm
fetched_at: 2026-11-25
---

# Related Records List

Output representation of the list of related records.

## JSON Example

```
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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 62.0 | 62.0 |
| `related​Records` | [Related Records](./connect-responses-related-records-output.md)[] | List of related records. | Small, 62.0 | 62.0 |
| `status` | [Status](./connect-responses-status.md)[] | Status of the API request. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-related-records-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
