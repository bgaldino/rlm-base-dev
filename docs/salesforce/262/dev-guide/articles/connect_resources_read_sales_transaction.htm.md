---
page_id: connect_resources_read_sales_transaction.htm
title: Read Sales Transaction (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_read_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Read Sales Transaction (POST)

Retrieve sales transaction data efficiently from an initialized or a
hydrated context.

Resource
:   ```
    /connect/revenue/transaction-management/sales-transactions/actions/read
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/revenue/transaction-management/sales-transactions/actions/read
    ```

Available version
:   65.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
          "queryTags": [
            "Quote",
            "QuoteLineItem",
            "Product"
          ],
          "sobjectFieldMap": {
            "Quote": [],
            "QuoteLineItem": [
              "Quantity",
              "Product2Id"
            ]
          },
          "filters": [
            {
              "sObjectName": "Quote",
              "fieldName": "Status",
              "operator": "Equals",
              "operands": [
                {
                  "value": "Draft",
                  "type": "STRING"
                }
              ]
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextId` | String | ID of the context to retrieve the data records. | Required | 65.0 |
        | `queryTags` | List<String> | List of objects that must be retrieved from the context. | Optional | 65.0 |
        | `sobjectFieldMap` | Map<String, List<String>> | Mapping of an sObject name to a list. The list includes the sObject field names on the object or can be an empty list. An empty list specifies that all fields on the object must be queried. | Optional | 67.0 |
        | `filters` | List<[Sales Transaction Filter Condition](./connect_requests_sales_transaction_filter_condition_input.htm.md)> | Filter conditions to query the context data. | Optional | 67.0 |

Response body for POST
:   [Read Sales Transaction](./connect_responses_read_sales_transaction_output.htm.md "Output representation of the request to read a sales transaction.")
