---
page_id: connect_requests_place_order_input.htm
title: Place Order Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_place_order_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Place Order Input

Input representation of the request to create or update an order.

JSON example
:   ```
    {
      "pricingPref": "System",
      "configurationInput": "RunAndAllowErrors",
      "configurationOptions": {
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
      },
      "graph": {
        "graphId": "graphId",
        "records": [
          {
            "referenceId": "refOrder",
            "record": {
              "attributes": {
                "type": "Order",
                "method": "POST",
                "Id": "POST"
              }
            }
          },
          {
             "referenceId":"refOrderItem",
             "record":{
             "attributes":{
                 "type":"OrderItem",
                 "method":"POST"
                },
                "OrderId":"@{refOrder.id}",
                "OrderActionId":"@{refOrderAction.id}",
                "ListPrice":"144.99",
                "Quantity":3,
                "PricebookEntryId":"01uxx0000008yXPAAY",
                "Product2Id":"01txx0000006i2UAAQ",
                "UnitPrice":"199.49"
           }
          }
        ]
      }
    }
    ```
:   This example shows a sample request to define grouping of order
    items.

    ```
    {
        "pricingPref": "system",
        "graph": {
            "graphId": "placeOrder",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "801xx000003GZ9bAAG"
                        }
                    }
                },
                {
                    "referenceId": "refOlg1",
                    "record": {
                        "attributes": {
                            "type": "OrderItemGroup",
                            "method": "POST"
                        },
                        "Name": "New Group",
                        "OrderId": "@{refOrder.id}"
                    }
                }
            ]
        }
    }
    ```
:   This example shows a sample request to ungroup order
    items.

    ```
    {
        "pricingPref": "system",
        "graph": {
            "graphId": "placeOrder",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "refOrder"
                        }
                    }
                },
                {
                    "referenceId": "refOlg1",
                    "record": {
                        "attributes": {
                            "type": "OrderItemGroup",
                            "method": "DELETE",
                            "id": "refOlg1",
                            "action": "Ungroup"
                        }
                    }
                }
            ]
        }
    }
    ```
:   This example shows a sample request to create a new
    group.

    ```
    {
        "pricingPref": "system",
        "graph": {
            "graphId": "placeOrder",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "refOrder"
                        }
                    }
                },
                {
                    "referenceId": "refOlg",
                    "record": {
                        "attributes": {
                            "type": "OrderItemGroup",
                            "method": "POST"
                        },
                        "Name": "New Group",
                        "OrderId": "@{refOrder.id}"
                    }
                }
            ]
        }
    }
    ```
:   This example shows a sample request to delete a
    group.

    ```
    {
        "contextId": "",
        "correlationId": "",
        "records": [
            {
                "referenceId": "refOrder",
                "record": {
                    "attributes": {
                        "type": "Order",
                        "method": "PATCH",
                        "id": "refOrder"
                    }
                }
            },
            {
                "referenceId": "refOlg",
                "record": {
                    "attributes": {
                        "type": "OrderItemGroup",
                        "method": "DELETE",
                        "id": "refOlg",
                        "action": "DeleteGroup"
                    }
                }
            }
        ]
    }
    ```
:   This example shows a sample request to group order items based on
    criteria.

    ```
    {
        "pricingPref": "system",
        "graph": {
            "graphId": "placeOrder",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "refOrder"
                        }
                    }
                },
                {
                    "referenceId": "g0",
                    "record": {
                        "attributes": {
                            "type": "OrderItemGroup",
                            "method": "POST",
                            "action": "GroupBy",
                            "criteria": {
                                "BillingFrequency2": null
                            }
                        },
                        "Name": "Billing Frequency: ",
                        "OrderId": "@{refOrder.id}"
                    }
                },
                {
                    "referenceId": "g1",
                    "record": {
                        "attributes": {
                            "type": "OrderItemGroup",
                            "method": "POST",
                            "action": "GroupBy",
                            "criteria": {
                                "BillingFrequency2": "Monthly"
                            }
                        },
                        "Name": "Billing Frequency: Monthly",
                        "OrderId": "@{refOrder.id}"
                    }
                }
            ]
        }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `catalog​RatesPref` | String | Rate card entries defined in the catalog that must be fetched for order items with usage-based pricing during the order creation process. Valid values are:  - `Fetch`—Retrieves the rate   card entries defined in the catalog for order items during the order   creation process. - `Skip`—Skips the retrieval of   rate card entries for order items during the order creation process.   The default value is `Skip`.  This property is available when the Usage-Based Selling feature is enabled. | Optional | 62.0 |
    | `configuration​Input` | String | Configuration input for the place order process. Valid values are:  - `RunAndAllowErrors`—Specifies   to run the configuration and to proceed order ingestion upon encountering   any configuration errors. - `RunAndBlockErrors`—Specifies   to run configuration and to block order ingestion upon encountering any   configuration errors. - `Skip`—Specifies to skip   configuration.   The default value is `RunAndBlockErrors`. | Optional | 60.0 |
    | `configuration​Options` | [Configuration Options Input​](./connect_requests_configuration_options_input.htm.md "Input representation for the configuration options.")[] | Configuration options during the ingestion process. | Optional | 60.0 |
    | `graph` | [Object Graph Input](./connect_requests_object_graph_input.htm.md "Input representation of an sObject with a graph ID.") | The sObject graph of the order payload to be ingested. You can perform create, update, or delete operations on objects from the Sales Transaction context definition by using this property. Additionally, perform create, update, or delete operations on custom objects and fields in your extended context definition. | Required | 60.0 |
    | `pricing​Pref` | String | Pricing preference during the create order process. Valid values are:  - `Force`—Specifies to force   pricing during the order ingestion process. - `Skip`—Specifies to skip   pricing during the order ingestion process. - `System`—Specifies the system   to determine whether a pricing calculation is required.   The default value is `System`. | Optional | 60.0 |
