---
page_id: connect_requests_get_instant_pricing_input.htm
title: Instant Pricing Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_get_instant_pricing_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Instant Pricing Input

Input representation to fetch the instant pricing details.

JSON example
:   ```
    {
      "correlationId": "7847127122596",
      "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
      "records": [
        {
          "referenceId": "0Q0xx0000004DOSCA2",
          "record": {
            "attributes": {
              "type": "Quote",
              "method": "POST"
            },
            "Name": "Test Quote Proration Pricing",
            "OpportunityId": "006xx000001a4ISAAY",
            "Pricebook2Id": "01sxx0000005ptpAAA"
          }
        },
        {
          "referenceId": "refQuoteLine",
          "record": {
            "attributes": {
              "type": "QuoteLineItem",
              "method": "POST"
            },
            "QuoteId": "0Q0xx0000004DOSCA2",
            "PricebookEntryId": "01uxx0000008zHmAAI",
            "Product2Id": "01txx0000006jmWAAQ",
            "Quantity": 2,
            "UnitPrice": 25,
            "StartDate": "2022-09-28",
            "EndDate": "2028-09-27",
            "PeriodBoundary": "ANNIVERSARY",
            "BillingFrequency": "ANNUAL"
          }
        }
      ]
    }
    ```
:   This example shows a sample request to specify grouping of lines based on
    criteria.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004DOSCA2",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
            {
                "referenceId": "0QLxx0000004F3gGAE",
                "record": {
                    "attributes": {
                        "type": "QuoteLineItem",
                        "method": "PUT"
                    },
                    "Quantity": 5
                }
            }, {
                "referenceId": "0QLxx0000004F3hGAE",
                "record": {
                    "attributes": {
                        "type": "QuoteLineItem",
                        "method": "PUT"
                    },
                    "Quantity": 2
                }
            },
            {
                "referenceId": "GroupId1",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "POST",
                        "action": "GroupBy",
                        "criteria": {
                            "Quantity": 5
                        }
                    },
                    "Name": "record"
                }
            }, {
                "referenceId": "GroupId2",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "POST",
                        "action": "GroupBy",
                        "criteria": {
                            "Quantity": 2
                        }
                    },
                    "Name": "record1",
                }
            }
        ]
    }
    ```
:   This example shows a sample request for the initial grouping of the quote with the
    quote lines assigned to the first
    group.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004CAgCAM",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
            {
                "referenceId": "GroupId1",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "POST",
                        "action": "GroupAll" 
                    },
                    "Name": "sample"
                }
            }
        ]
    }
    ```
:   This example shows a sample request to ungroup a quote but retain the quote
    lines.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004CAgCAM",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
             {
                "referenceId": "0QLxx0000004CBYGA2",
                "record": {
                    "attributes": {
                        "type": "QuoteLineItem",
                        "method": "PUT"
                    },
                    "Quantity": 2,
                    "QuoteLineGroupId": null
                }
            },
            {
                "referenceId": "GroupId1",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "DELETE",
                        "action": "Ungroup"
                    }
                }
            }
        ]
    }
    ```
:   This example shows a sample request to create a new
    group.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004CAgCAM",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
            {
                "referenceId": "GroupId1",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "POST"
                    },
                    "Name": "sample"
                }
            }
        ]
    }
    ```
:   This example shows a sample request to delete a
    group.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004CAgCAM",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
            {
                "referenceId": "GroupId1",
                "record": {
                    "attributes": {
                        "type": "QuoteLineGroup",
                        "method": "DELETE",
                        "action": "DeleteGroup"
                    },
                    "Name": "sample"
                }
            }
        ]
    }
    ```
:   This example shows a sample request to move a
    group.

    ```
    {
        "contextId": "0000000b28op21g00281751271041790cc1e5686282849a387dd3c59b310418b",
        "correlationId": "7847127122596",
        "records": [
            {
                "referenceId": "0Q0xx0000004CAgCAM",
                "record": {
                    "attributes": {
                        "type": "Quote",
                        "method": "PUT"
                    }
                }
            },
            {
                "referenceId": "0QLxx0000004CBYGA2",
                "record": {
                    "attributes": {
                        "type": "QuoteLineItem",
                        "method": "PUT"
                    },
                    "Quantity": 2
                    "QuoteLineGroupId": "{@GroupId2}"
                }
            },
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextId` | String | ID generated by the context service. If you don’t specify a context ID, a new context is created. | Optional | 59.0 |
    | `correlationId` | String | Client-generated ID for tracking multiple related API requests. | Optional | 59.0 |
    | `records` | [Object with Reference Input](./connect_requests_object_with_reference_input.htm.md "Input representation of a list of records to be inserted or updated. To update a record, specify the record ID.")[] | List of pricing data to be fetched. | Required | 59.0 |
