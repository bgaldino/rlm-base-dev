---
page_id: connect_requests_usage_based_product_input.htm
title: Usage-Based Product Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_based_product_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Usage-Based Product Input

Understand the sample request structure to specify and manage usage-based products
within a sales transaction.

JSON example to create a quote record with default rates and default grants
:   The example shows a sample request to creates these records with these updates.

    - `Quote`—Creates the main quote record
      with default rates and default grants.
    - `Quote Line Item`—Adds a product to the
      quote.
    - `Rate Card Entry`—Links default pricing
      from rate card. When `NegotiatedRate` property
      value is null, the rate card price is used.
    - `Usage Grant`—Allocates all default
      grants.

    ```
    {
      "pricingPref": "system",
      "configurationPref": {
        "configurationMethod": "skip",
        "configurationOptions": {
          "validateProductCatalog": false,
          "validateAmendRenewCancel": false,
          "executeConfigurationRules": false,
          "addDefaultConfiguration": false
        }
      },
      "graph": {
        "graphId": "graphId",
        "records": [
          {
            "referenceId": "refQuote",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "POST"
              },
              "Name": "Q-2024-001",
              "QuoteAccountId": "001xx000003DHP0AAO",
              "OpportunityId": "006xx000004TmiGAAS",
              "Status": "Draft",
              "Pricebook2Id": "01sxx0000001SGEAA2"
            }
          },
          {
            "referenceId": "refQuoteLineItem",
            "record": {
              "attributes": {
                "type": "QuoteLineItem",
                "method": "POST"
              },
              "QuoteId": "@{refQuote.id}",
              "Product2Id": "01txx0000001SGEAA2",
              "StartDate": "2024-10-29",
              "PeriodBoundary": "Anniversary",
              "EndDate": "2027-03-01",
              "PricebookEntryId": "01uxx0000001SGEAA2",
              "UnitPrice": 100,
              "Quantity": 1
            }
          },
          {
            "referenceId": "refRateCardEntry",
            "record": {
              "attributes": {
                "type": "QuoteLineRateCardEntry",
                "method": "POST"
              },
              "RateCardEntryId": "1CJxx0000004CXEGA2",
              "NegotiatedRate": null,
              "QuoteLineItemId": "@{refQuoteLineItem.id}"
            }
          }
        ]
      }
    }
    ```

JSON example to specify negotiated grants
:   This example shows a sample response to create a QuotLineItmUseRsrcGrant record that
    links a quote line item to a product usage grant for usage-based products. This
    request performs these updates.

    - Associates a usage grant with a quote line item.
    - Allocates a quantity of usage resources.
    - Applies a usage policy that defines how the resources can be consumed.
    - Links to a base product usage grant that defines the grant structure.

    ```
    {
      "pricingPref": "system",
      "configurationPref": {
        "configurationMethod": "skip",
        "configurationOptions": {
          "validateProductCatalog": false,
          "validateAmendRenewCancel": false,
          "executeConfigurationRules": false,
          "addDefaultConfiguration": false
        }
      },
      "graph": {
        "graphId": "graphId",
        "records": [
          {
            "referenceId": "ref1CJxx0000004CXGGA2",
            "record": {
              "attributes": {
                "type": "QuotLineItmUseRsrcGrant",
                "method": "POST"
              },
              "GrantQuantity": 4,
              "ProductUsageResourcePolicyId": "7Suxx0000004C92CAE",
              "QuoteLineItemId": "0QLxx0000004CnMGAU",
              "ProductUsageGrantId": "1BXxx0000004C92GAE"
            }
          }
        ]
      }
    }
    ```
:   This example shows a sample response to update the previously created
    QuotLineItmUseRsrcGrant record with additional units, which is specified by using the
    `GrantQuantity` property. The quote line item now
    has 97 units of usage resource allocation.

    ```
    {
      "pricingPref": "system",
      "configurationPref": {
        "configurationMethod": "skip",
        "configurationOptions": {
          "validateProductCatalog": false,
          "validateAmendRenewCancel": false,
          "executeConfigurationRules": false,
          "addDefaultConfiguration": false
        }
      },
      "graph": {
        "graphId": "graphId",
        "records": [
          {
            "referenceId": "ref1X6xx000000003GCAQ",
            "record": {
              "attributes": {
                "method": "PATCH",
                "type": "QuotLineItmUseRsrcGrant",
                "id": "1X6xx000000003GCAQ"
              },
              "GrantQuantity": 97
            }
          }
        ]
      }
    }
    ```

JSON example to specify tiered pricing and usage grants
:   This example shows a sample request to update an existing quote with tiered pricing
    and usage grants. This request sets up a multi-tier rate structure and updates a usage
    grant quantity along with these additional updates.

    - Creates a base rate card entry with a negotiated rate of 10. Sets the base price
      for the quote line item.
    - Creates a second rate card entry for tiered pricing without any negotiated rate.
      The default rate card is used. This rate card entry is the base for tier
      adjustments.
    - Creates a tier adjustment for quantities 0 through 50 and adds $5 adjustment to
      the base rate.
    - Creates a tier adjustment for quantities 50 through 100 and adds an adjustment of
      $10.
    - Updates an existing usage resource grant record to set grant quantity to 150
      units.

    For example, if an order is placed for 75 units, the base rate is $10. As tier 2
    is applicable for this order, an adjustment of $10 is applicable. The final price per
    unit is $20 with a total of $1500 for 75
    units.

    ```
    {
      "pricingPref": "system",
      "configurationPref": {
        "configurationMethod": "skip",
        "configurationOptions": {
          "validateProductCatalog": false,
          "validateAmendRenewCancel": false,
          "executeConfigurationRules": false,
          "addDefaultConfiguration": false
        }
      },
      "graph": {
        "graphId": "graphId",
        "records": [
          {
            "referenceId": "refLineItemParent",
            "record": {
              "attributes": {
                "type": "Quote",
                "method": "PATCH",
                "id": "0Q0xx0000004CXEGA2"
              }
            }
          },
          {
            "referenceId": "ref1",
            "record": {
              "attributes": {
                "type": "QuoteLineRateCardEntry",
                "method": "POST"
              },
              "RateCardEntryId": "1CJxx0000004CXEGA2",
              "NegotiatedRate": 10,
              "QuoteLineItemId": "0QLxx0000004Eh6GAE"
            }
          },
          {
            "referenceId": "refTierRateCardEntry0",
            "record": {
              "attributes": {
                "type": "QuoteLineRateCardEntry",
                "method": "POST"
              },
              "RateCardEntryId": "1CJxx0000004CXFGA2",
              "QuoteLineItemId": "0QLxx0000004Eh6GAE"
            }
          },
          {
            "referenceId": "refTier0",
            "record": {
              "attributes": {
                "type": "QuoteLineRateAdjustment",
                "method": "POST"
              },
              "Name": "Tier 1",
              "AdjustmentType": "Amount",
              "AdjustmentValue": 5,
              "LowerBound": 0,
              "UpperBound": 50,
              "QuoteLineRateCardEntryId": "@{refTierRateCardEntry0.id}"
            }
          },
          {
            "referenceId": "refTier1",
            "record": {
              "attributes": {
                "type": "QuoteLineRateAdjustment",
                "method": "POST"
              },
              "Name": "Tier 2",
              "AdjustmentType": "Amount",
              "AdjustmentValue": 10,
              "LowerBound": 50,
              "UpperBound": 100,
              "QuoteLineRateCardEntryId": "@{refTierRateCardEntry0.id}"
            }
          },
          {
            "referenceId": "refTier2",
            "record": {
              "attributes": {
                "type": "QuoteLineRateAdjustment",
                "method": "POST"
              },
              "Name": "Tier 3",
              "AdjustmentType": "Amount",
              "AdjustmentValue": 15,
              "LowerBound": 100,
              "UpperBound": 150,
              "QuoteLineRateCardEntryId": "@{refTierRateCardEntry0.id}"
            }
          },
          {
            "referenceId": "refGt2xzdUP",
            "record": {
              "attributes": {
                "type": "QuotLineItmUseRsrcGrant",
                "method": "PATCH",
                "id": "1X6xx000000003GCAQ"
              },
              "GrantQuantity": 150
            }
          }
        ]
      }
    }
    ```
