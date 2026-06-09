---
page_id: connect_requests_related_object_node_input.htm
title: Related Object Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_related_object_node_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Related Object Node Input

Input representation of the details of a related object node.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `filter` | [Criteria](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.")[] | Criteria to filter records. The supported properties are:   - `StartDate` - `EndDate` - `Status`   The supported operators are:   - `eq` - `gte` - `lte`   The supported related object is ProductUsageGrant.  If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 62.0 |
    | `offSet` | Integer | Number of records to skip. The default value is 0. | Optional | 62.0 |
    | `pageSize` | Integer | Number of records per page. Valid values are from 1 through 100. If unspecified, the default value is 100. | Optional | 62.0 |
    | `relatedObject​APIName` | String | API name of the related object to return the records for. The supported related objects are ProductRampSegment and ProductUsageGrant. | Required | 62.0 |
