---
page_id: connect_requests_place_sales_transaction_input.htm
title: Sales Transaction Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_place_sales_transaction_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Sales Transaction Input

Input representation of the details of the request to place a sales transaction, such as
a quote or an order.

JSON example
:   This is a sample request to create a sales transaction for a quote. This example also
    skips tax calculation by specifying a value for the optional `taxPref` property.
:   ```
    {
      "pricingPref": "System",
      "catalogRatesPref": "Skip",
      "configurationPref": {
        "configurationMethod": "Skip",
        "configurationOptions": {
          "validateProductCatalog": true,
          "validateAmendRenewCancel": true,
          "executeConfigurationRules": true,
          "addDefaultConfiguration": true
        }
      },
      "taxPref": "Skip",
      "contextDetails": {
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
      },
      "graph": {
        "graphId": "createQuote",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "method": "POST",
                "type": "Quote"
              },
              "Name": "Quote_Acme",
              "Pricebook2Id": "01sDU000000JvhbYAC"
            }
          },
          {
            "referenceId": "refQuoteLine0",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST"
              },
              "QuoteId": "@{refQuote.id}",
              "Product2Id": "01tDU000000F7b8YAC",
              "PricebookEntryId": "01uDU000000fxt2YAA",
              "UnitPrice": 100,
              "Quantity": "1",
              "StartDate": "2024-10-29",
              "EndDate": "2025-03-01",
              "PeriodBoundary": "Anniversary"
            }
          },
          {
            "referenceId": "refQuoteLine1",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST"
              },
              "QuoteId": "@{refQuote.id}",
              "Product2Id": "01tLT00000AA2M9YAL",
              "PricebookEntryId": "01uLT000007PTafYAG",
              "Quantity": "1"
            }
          },
          {
            "referenceId": "refQuoteLineItemAttribute1",
            "record": {
              "attributes": {
                "type": "QuoteLineItemAttribute",
                "method": "POST"
              },
              "QuoteLineItemId": "@{refQuoteLine0.id}",
              "AttributeDefinitionId": "0tjRT0000000XbtYAE",
              "AttributeValue": "True"
            }
          },
          {
            "referenceId": "refQuoteLineRelationship1",
            "record": {
              "attributes": {
                "type": "QuoteLineRelationship",
                "method": "POST"
              },
              "ProductRelationshipTypeId": "0yoLT000000wHq6YAE",
              "ProductRelatedComponentId": "0dSLT00000076IP2AY",
              "MainQuoteLineId": "@{refQuoteLine0.id}",
              "AssociatedQuoteLineId": "@{refQuoteLine1.id}",
              "AssociatedQuoteLinePricing": "NotIncludedInBundlePrice"
            }
          }
        ]
      }
    }
    ```
:   This sample request assigns a TransactionProcessingType record to a quote without any
    additional preferences. In this example, the TransactionType value for a record is set
    to a TransactionProcessingType record. See [TransactionProcessingType](./tooling_api_objects_transactionprocessingtype.htm.md "Represents the settings to configure the processing constraints for a request.. This object is available in API version 63.0 and later.") tooling
    object for more details.

    ```
    {
      "pricingPref": "Force",
      "contextDetails": {
        "contextId": "f1c9e3e1c335f7959a88de09d3a867cc2b95e08709b99de8e2edeb8f5039e8ed",
        "scope": "Session"
      },
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "POST"
              },
              "OpportunityId": "006xx000001a2oWAAQ",
              "PriceBook2Id": "01sxx0000005ptpAAA",
              "TransactionType": "SkipPricingAndRunTax",
              "Name": "Quote_No_Tax_System"
            }
          },
          {
            "referenceId": "refQLI1",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST"
              },
              "QuoteId": "@{refQuote.id}",
              "UnitPrice": 49.99,
              "Product2Id": "01txx0000006i2aAAA",
              "PricebookEntryId": "01uxx0000008yX0AAI",
              "Quantity": 10
            }
          }
        ]
      }
    }
    ```
:   This is a sample request to insert, update, or delete a quote line
    item.

    ```
    {
      {
      "pricingPref": "System",
      "catalogRatesPref": "Skip",
      "configurationPref": {
        "configurationMethod": "Skip",
        "configurationOptions": {
          "validateProductCatalog": true,
          "validateAmendRenewCancel": true,
          "executeConfigurationRules": true,
          "addDefaultConfiguration": true
        }
      },
      "contextDetails": {
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
      },
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "method": "PATCH",
                "type": "Quote",
                "id": "801xx000003GZ9bAAG"
              }
            }
          },
          {
            "referenceId": "refQuoteLine0",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "PATCH",
                "id": "402xx000003KY5vJGH"
              },
              "Quantity": "5"
            }
          }
        ]
      }
    }
    ```
:   This is a sample request to define grouping of quote line
    items.

    ```
    {
      "pricingPref": "Force",
      "catalogRatesPref": "Skip",
      "configurationPref": {
        "configurationMethod": "Skip",
        "configurationOptions": {
          "validateProductCatalog": true,
          "validateAmendRenewCancel": true,
          "executeConfigurationRules": true,
          "addDefaultConfiguration": true
        }
      },
      "contextDetails": {
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
      },
      "graph": {
        "graphId": "groupQuoteLines",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "method": "PATCH",
                "type": "Quote",
                "id": "801xx000003GZ9bAAG"
              }
            }
          },
          {
            "referenceId": "refQuoteLine0",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "PATCH",
                "id": "402xx000003KY5vJGH"
              },
              "QuoteLineGroupId": "@{refQuote.id}"
            }
          }
        ]
      }
    }
    ```
:   This is s a sample request for the initial grouping of the quote with all the quote
    lines assigned to the first
    group.

    ```
    {
      "pricingPref": "Force",
      "catalogRatesPref": "Skip",
      "graph": {
        "graphId": "groupQuote",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CAmCAM"
              }
            }
          },
          {
            "referenceId": "refQlg1",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "POST",
                "action": "GroupAll"
              },
              "Name": "From PST API Group",
              "QuoteId": "@{refQuote.id}"
            }
          }
        ]
      }
    }
    ```
:   This is a sample request to ungroup a quote but retain the quote
    lines.

    ```
    {
       "catalogRatesPref": "Skip",
       "pricingPref": "Force",
       "graph": {
          "graphId": "ungroupQuote",
          "records": [
             {
                "referenceId": "refQuote", 
                "record": {
                   "attributes": {
                      "type": "Quote",
                      "method": "PATCH",
                      "id":"0Q0xx0000004C99CAE"
                   },
                   "Name": "Grouped Quote with PST API"
                }
             },
             {
                "referenceId": "refQlg1",
                "record": {
                   "attributes": {
                      "type": "QuoteLineGroup",
                      "method": "DELETE",
                      "id": "402xx000003KY5vJGH",
                      "action": "Ungroup"
                   }
                }
             }
          ]
       }
    }
    ```
:   This is a sample request to create a new
    group.

    ```
    {
       "catalogRatesPref": "Skip",
       "pricingPref": "Force",
       "graph": {
          "graphId": "createGroup",
          "records": [
             {
                "referenceId": "refQuote",
                "record": {
                   "attributes": {
                      "type": "Quote",
                      "method": "PATCH",
                      "id":"0Q0xx0000004C99CAE"
                   },
                   "Name": "Grouped Quote with PST API"
                }
             },
             {
                "referenceId": "refQlg1",
                "record": {
                   "attributes": {
                      "type": "QuoteLineGroup",
                      "method": "POST"
                   },
                   "Name": "From PQ API Group",
                   "QuoteId": "@{refQuote.id}"
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
       "catalogRatesPref": "Skip",
       "pricingPref": "Force",
       "graph": {
          "graphId": "deleteGroup",
          "records": [
             {
                "referenceId": "refQuote",
                "record": {
                   "attributes": {
                      "type": "Quote",
                      "method": "PATCH",
                      "id":"0Q0xx0000004C99CAE"
                   },
                   "Name": "Grouped Quote with PST API"
                }
             },
             {
                "referenceId": "refQlg1",
                "record": {
                   "attributes": {
                      "type": "QuoteLineGroup",
                      "method": "DELETE",
                      "id": "402xx000003KY5vJGH",
                      "action": "DeleteGroup"
                   }
                }
             }
          ]
       }
    }
    ```
:   This is a sample request to group order items based on
    criteria.

    ```
    {
        "catalogRatesPref": "Skip",
        "pricingPref": "Force",
        "graph": {
            "graphId": "groupOrderItems",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "0Q0xx0000004C99CAE"
                        }
                    }
                },
                {
                    "referenceId": "refOlg1",
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
:   This is a sample request to save changes to a ramp deal by using context ID. The
    context ID is returned by the Ramp Deal APIs. See [Create Ramp Deal
    (POST)](./connect_resources_create_ramp_deal.htm.md "HTML (New Window)").

    ```
    {
      "pricingPref": "Force",
      "contextDetails": {
        "contextId": "f1c9e3e1c335f7959a88de09d3a867cc2b95e08709b99de8e2edeb8f5039e8ed",
        "scope": "Session"
      },
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004DQ4CAM"
              }
            }
          }
        ]
      }
    }
    ```
:   To see examples that specify actions to create ramp deals for groups, see [Group Ramp Action Input](./connect_requests_group_ramp_action_input.htm.md "Understand the sample request to specify group ramp actions during initial sale.").
:   To see examples that apply to usage-based products, see [Usage-Based Product Input](./connect_requests_usage_based_product_input.htm.md "Understand the sample request structure to specify and manage usage-based products within a sales transaction.").

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `catalogRates​Pref` | String | Rate card entries defined in the catalog that must be fetched for sales items with usage-based pricing during the creation of the sales transaction. Valid values are:  - `Fetch`—Retrieves the rate   card entries defined in the catalog for sales items during the creation of   the sales transaction. - `Skip`—Skips the retrieval of   rate card entries for sales items during the creation of the sales   transaction. The default value is `Skip`.  This property is available when the Usage-Based Selling feature is enabled. | Optional | 63.0 |
    | `configuration​Pref` | [Configurator Preference Input](./connect_requests_configurator_preference_input.htm.md "Input representation of the configuration preference for the place sales transaction request.") | Configuration preference during the quote process. These preferences ensure that quotes are defined as per the requirement. | Optional | 63.0 |
    | `contextDetails` | [Context Input](./connect_requests_context_info_input.htm.md "Input representation of the context that's associated with a sales transaction for a quote or an order.") | Context details that are created for a sales transaction. | Required if the `graph` property isn’t specified. | 63.0 |
    | `graph` | [Object Graph Input](./connect_requests_object_graph_input.htm.md "Input representation of an sObject with a graph ID.") | The sObject graph of the sales transaction to be ingested. You can perform create, update, or delete operations on objects from the Sales Transaction context definition by using this property. Additionally, perform create, update, or delete operations on custom objects and fields in your extended context definition.  To create custom objects that are at the grandchildren level from a line item, you must create the hierarchy of objects until the grandchild object in the same request. | Required if the `contextDetails` property isn’t specified. | 63.0 |
    | `groupRampAction` | String | Specifies the action ‌that you want to perform on group ramp segments. You can also convert a non-ramped group into a ramped group. Valid values are:   - `AddProducts`—Adds rampable   products to group ramp segments. - `DeleteProducts`—Deletes   ramped products. - `EditGroup`—Converts a   non-ramped group into a group ramp segment, or edit group ramp segment   attributes such as name and description, except the start and end   dates. - `EditRampSchedule`—Edits   details of the group ramp segments, including start and end dates. - `DeleteSegment`—Deletes the   first or last segment in a group ramp schedule. - `ConvertToNonRampedGroup`—Converts the first or last group   ramp segment into a non-ramped group.  To add or delete ramped line items from multiple group ramp segments, specify the applicable values in the `graph` property. See [Group Ramp Action Input](./connect_requests_group_ramp_action_input.htm.md "Understand the sample request to specify group ramp actions during initial sale.") to refer to examples. | Optional | 65.0 |
    | `pricingPref` | String | Pricing preference during the creation of a sales transaction. Valid values are:  - `Force`—Enforces pricing   during the creation of sales transactions. - `Skip`—Skips pricing during   the creation of sales transactions. - `System`—Determines whether a   pricing calculation is required.   The default value is `System`. | Optional | 63.0 |
    | `taxPref` | String | Specifies whether to execute or skip the tax calculation step for each sales transaction record. Valid value is `Skip`. If you don't specify this value, then tax calculation request is performed by default. | Optional | 65.0 |

- **[Group Ramp Action Input](./connect_requests_group_ramp_action_input.htm.md)**  
  Understand the sample request to specify group ramp actions during initial sale.
