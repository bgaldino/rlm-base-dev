---
page_id: connect-requests-related-records-input
title: Related Records Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-records-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_related_records_input.htm
fetched_at: 2026-11-25
---

# Related Records Input

Input representation of the request to retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object.

**JSON Example**

```
{
  "recordIds": [
    "01txx0000006i44AAA",
    "01txx0000006i5gAAA"
  ],
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
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 62.0 |
| `recordIds` | String[] | List of record IDs to return the relatedObjects records for. The maximum number of record IDs supported is 20. | Required | 62.0 |
| `related​ObjectNodes` | [Related Object Node Input](./connect-requests-related-object-node-input.md)[] | List of nodes for the related objects. The maximum number of related object nodes supported is two. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-records-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
