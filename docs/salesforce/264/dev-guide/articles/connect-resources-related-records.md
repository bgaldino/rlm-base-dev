---
page_id: connect-resources-related-records
title: Product Related Records List (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-related-records.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_related_records.htm
fetched_at: 2026-11-25
---

# Product Related Records List (POST)

Retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object.

**Resource**

```
/connect/pcm/relatedRecords/{entityName}
```

The supported entity or object is Product2.

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/relatedRecords/{product2}
```

**Available Version:** 62.0

**HTTP Methods:** POST

**Note:** POST methods typically create an item, but for this resource POST is used to retrieve information.

**Request Body for POST**

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

**Response Body for POST:** [Related Records List](./connect-responses-related-records-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-related-records.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
