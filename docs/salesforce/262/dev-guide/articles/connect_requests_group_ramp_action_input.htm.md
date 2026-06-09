---
page_id: connect_requests_group_ramp_action_input.htm
title: Group Ramp Action Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_group_ramp_action_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: connect_requests_place_sales_transaction_input.htm
fetched_at: 2026-06-09
---

# Group Ramp Action Input

Understand the sample request to specify group ramp actions during initial
sale.

Keep these considerations in mind when you specify ramp actions.

- Use the [Clone Sales Transaction API](./connect_resources_clone_sales_transaction.htm.md "HTML (New Window)") to clone a
  ramp segment, and specify the clone option.
- Use the [Place Sales Transaction API](./connect_resources_place_sales_transaction.htm.md "HTML (New Window)") to specify a
  group ramp action by using the `groupRampAction`
  property. You can refer to the sections in this topic for examples.

JSON example to edit a group
:   This is a sample request that creates the first ramp segment. This request accepts
    IDs of a quote and quote line group. Additionally, the request accepts attributes of
    quote line group such as `IsRamped`, `SegmentType`, `StartDate`, and `EndDate`. A ramp
    segment is created with a ramp identifier and segment identifier added to all the
    quote line items available in the ramp segment.

    This process converts a group
    into a segment, which becomes the first segment in the ramp schedule. A quote can
    contain a single ramp schedule only. To create another segment in the ramp schedule,
    use the [Clone Sales Transaction API](./connect_resources_clone_sales_transaction.htm.md "HTML (New Window)").
:   ```
    {
      "groupRampAction": "EditGroup",
      "pricingPref": "System",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0xx0000004CYqCAM",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CYqCAM"
              }
            }
          },
          {
            "referenceId": "1C9xx0000004CVcCAM",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CVcCAM"
              },
              "StartDate": "2025-05-01",
              "EndDate": "2025-06-30",
              "SortOrder": 1,
              "IsRamped": true,
              "SegmentType": "Custom"
            }
          }
        ]
      }
    }
    ```

JSON example to edit a ramp segment
:   This is a sample request to edit multiple ramp segments simultaneously, maintaining
    date continuity among ramp
    segments.

    ```
    {
      "groupRampAction": "EditRampSchedule",
      "pricingPref": "System",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0xx0000004CYqCAM",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CYqCAM"
              }
            }
          },
          {
            "referenceId": "1C9xx0000004CVcCAM",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CVcCAM"
              },
              "StartDate": "2025-05-01",
              "EndDate": "2025-06-30"
            }
          },
          {
            "referenceId": "1C9xx0000004CVcAAM",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CVcAAM"
              },
              "StartDate": "2025-07-01",
              "EndDate": "2025-08-30"
            }
          },
          {
            "referenceId": "1C9xx0000004CVcBAM",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CVcBAM"
              },
              "StartDate": "2025-09-01",
              "EndDate": "2025-10-30"
            }
          }
        ]
      }
    }
    ```

JSON example to add a product
:   This is a sample request to add a product to the current and subsequent segments. A
    ramp identifier and segment identifier are added to the quote line
    items.

    ```
    {
      "groupRampAction": "AddProducts",
      "pricingPref": "System",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0xx0000004CKKCA2",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CKKCA2"
              }
            }
          },
          {
            "referenceId": "1C9xx0000004CCGCA2",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CCGCA2"
              }
            }
          },
          {
            "referenceId": "ref_01txx0000006iCXAAY_0",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST",
                "id": "ref_01txx0000006iCXAAY_0"
              },
              "QuoteId": "@{0Q0xx0000004CKKCA2.id}",
              "Id": "ref_01txx0000006iCXAAY_0",
              "UnitPrice": 2000,
              "Product2Id": "01txx0000006iCXAAY",
              "PricebookEntryId": "01uxx0000008yciAAA",
              "Quantity": 1,
              "StartDate": "2025-05-28T00:00:00.000Z",
              "BillingFrequency": null,
              "PeriodBoundary": null,
              "QuoteLineGroupId": "1C9xx0000004CCGCA2"
            }
          },
          {
            "referenceId": "1C9xx0000004CCGCAB",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004CCGCAB"
              }
            }
          },
          {
            "referenceId": "ref_01txx0000006iCXABY_0",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST",
                "id": "ref_01txx0000006iCXABY_0"
              },
              "QuoteId": "@{0Q0xx0000004CKKCA2.id}",
              "Id": "ref_01txx0000006iCXAAY_0",
              "UnitPrice": 2000,
              "Product2Id": "01txx0000006iCXAAY",
              "PricebookEntryId": "01uxx0000008yciAAA",
              "Quantity": 1,
              "StartDate": "2025-05-28T00:00:00.000Z",
              "BillingFrequency": null,
              "PeriodBoundary": null,
              "QuoteLineGroupId": "1C9xx0000004CCGCAB"
            }
          }
        ]
      }
    }
    ```

JSON example to delete a product
:   This is a sample request to delete a product from the current and subsequent ramp
    segments.

    ```
    {
      "pricingPref": "System",
      "groupRampAction": "DeleteProducts",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0SG000000L5r70AC",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0SG000000L5r70AC"
              }
            }
          },
          {
            "referenceId": "0QLSG000000WuTh4AK",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "DELETE",
                "id": "0QLSG000000WuTh4AK"
              }
            }
          },
          {
            "referenceId": "0QLSG000000WuTh4BK",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "DELETE",
                "id": "0QLSG000000WuTh4AK"
              }
            }
          }
        ]
      }
    }
    ```

JSON example to delete a segment
:   This is a sample request to delete the first and last segment in a ramp schedule. The
    API throws an error if the specified segment isn't the first and last segment, ensuring
    there are no gaps between quote line items in different ramp
    segments.

    ```
    {
      "pricingPref": "System",
      "groupRampAction": "DeleteSegment",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0xx0000004CfICAU",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CfICAU"
              }
            }
          },
          {
            "referenceId": "1C9xx0000004FjcCAE",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "DELETE",
                "id": "1C9xx0000004FjcCAE",
                "action": "DeleteGroup"
              }
            }
          }
        ]
      }
    }
    ```

JSON example to remove a segment from a ramp schedule
:   This is a sample request to remove the first or last ramp segment in a ramp schedule.
    This request removes the ramp-specific fields from a quote line group such as `IsRamped` and `SegmentType`. Additionally, this request removes the `RampIdentifier` and `SegmentIdentifier` fields from a quote line
    item.

    ```
    {
      "pricingPref": "System",
      "groupRampAction": "ConvertToNonRampedGroup",
      "graph": {
        "graphId": "updateQuote",
        "records": [
          {
            "referenceId": "0Q0xx0000004CfICAU",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CfICAU"
              }
            }
          },
          {
            "referenceId": "1C9xx0000004FjcCAE",
            "record": {
              "attributes": {
                "type": "QuoteLineGroup",
                "method": "PATCH",
                "id": "1C9xx0000004FjcCAE"
              }
            }
          }
        ]
      }
    }
    ```
