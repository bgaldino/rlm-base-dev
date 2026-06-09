---
page_id: connect_requests_sales_transaction_filter_condition_input.htm
title: Sales Transaction Filter Condition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sales_transaction_filter_condition_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Sales Transaction Filter Condition Input

Input representation of filter conditions used to query sales transaction context
data.

JSON example
:   ```
    {
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
    | `sObjectName` | String | Name of the sObject that contains the field to filter on. | Required if the `fieldName` property value isn’t specified. Or, specify the `nodeName` and `attributeName` property values. | 67.0 |
    | `fieldName` | String | Name of the field on the specified sObject to filter on. | Required if the `sObjectName` property value isn’t specified. Or, specify the `nodeName` and `attributeName` property values. | 67.0 |
    | `operator` | String | Operator to use to filter the results. Valid values are:  - `Equals` - `NotEquals` - `Gt`—Greater Than - `GtEq`—Greater Than or   Equals - `Lt`—Less Than - `LtEq`—Less Than or   Equals - `In` | Required | 67.0 |
    | `nodeName` | String | Name of the context node to apply filtering on. | Optional | 67.0 |
    | `attributeName` | String | Name of the node attribute to apply filtering on. | Optional | 67.0 |
    | `operands` | [Sales Transaction Operand](./connect_requests_sales_transaction_operand_input.htm.md#SalesTransactionOperandInputRepresentation)[] | Operand values with explicit value and type metadata. | Required | 67.0 |
    | `underlyingFilters` | [Sales Transaction Filter Condition](#SalesTransactionFilterConditionInputRepresentation)[] | Nested filter conditions used to compose a composite filter. | Optional | 67.0 |
    | `operatorLogic` | String | Logical expression that defines how underlying filters are combined. Valid values are:   - `AND` - `OR` | Optional | 67.0 |
