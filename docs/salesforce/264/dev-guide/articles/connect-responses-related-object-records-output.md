---
page_id: connect-responses-related-object-records-output
title: Related Object Records
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-related-object-records-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_related_object_records_output.htm
fetched_at: 2026-11-25
---

# Related Object Records

Output representation of the related records for a specified record ID and related object API name.

## JSON Example

```
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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `count` | Integer | Total count of the related records that are returned. | Small, 62.0 | 62.0 |
| `records` | Map<String, Object> | List of related object records. | Small, 62.0 | 62.0 |
| `relatedObject​APIName` | String | API name of the related object to return the records for. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-related-object-records-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
