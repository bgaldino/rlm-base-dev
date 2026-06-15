---
page_id: connect_resources_related_records.htm
title: Product Related Records List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_related_records.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Product Related Records List (POST)

Retrieve related ProductRampSegment or ProductUsageGrant records for
Product2 object.

Resource
:   ```
    /connect/pcm/relatedRecords/entityName
    ```
:   The supported entity or object is Product2.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/relatedRecords/product2
    ```

Available version
:   62.0

HTTP methods
:   POST

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

    #### Note

    POST methods typically create an item, but for this resource POST is used to
    retrieve information.

Request body for POST
:   JSON example
    :   ```
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

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 62.0 |
        | `recordIds` | String[] | List of record IDs to return the relatedObjects records for. The maximum number of record IDs supported is 20. | Required | 62.0 |
        | `related​ObjectNodes` | [Related Object Node Input](./connect_requests_related_object_node_input.htm.md "Input representation of the details of a related object node.")[] | List of nodes for the related objects. The maximum number of related object nodes supported is two. | Required | 62.0 |

Response body for POST
:   [Related Records
    List](./connect_responses_related_records_list_output.htm.md "Output representation of the list of related records.")
