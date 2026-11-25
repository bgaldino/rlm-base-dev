---
page_id: connect-requests-related-object-node-input
title: Related Object Node Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-object-node-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_related_object_node_input.htm
fetched_at: 2026-11-25
---

# Related Object Node Input

Input representation of the details of a related object node.

**JSON Example**

```
 "relatedObjectNodes": [
    {
      "relatedObjectAPIName": "ProductRampSegment",
      "pageSize": 20,
      "offSet": 0
    },
    {
      "relatedObjectAPIName": "ProductUsageGrant",
      "pageSize": 10,
      "offSet": 0,
      "filter": {
        "criteria": [
          {
            "property": "status",
            "operator": "eq",
            "value": "active"
          },
          {
            "property": "effectivestartdate",
            "operator": "lte",
            "value": "2024-06-25"
          },
          {
            "criteriaType": "CustomWhereCondition",
            "value": "(effectiveenddate = null OR effectiveenddate >= 2024-06-25)"
          }
        ]
      }
    }
  ]
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filter` | [Criteria](./connect-requests-criteria.md)[] | Criteria to filter records. The supported properties are `StartDate`, `EndDate`, or `Status`. The supported operators are `eq`, `gte`, or `lte`. The supported related object is ProductUsageGrant. If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 62.0 |
| `offSet` | Integer | Number of records to skip. The default value is 0. | Optional | 62.0 |
| `pageSize` | Integer | Number of records per page. Valid values are from 1 through 100. If unspecified, the default value is 100. | Optional | 62.0 |
| `relatedObject​APIName` | String | API name of the related object to return the records for. The supported related objects are ProductRampSegment and ProductUsageGrant. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-object-node-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
