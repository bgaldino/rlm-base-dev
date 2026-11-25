---
page_id: connect-responses-usage-detail-output
title: Usage Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_usage_detail_output.htm
fetched_at: 2026-11-25
---

# Usage Details

Output representation of the usage details of a quote, an order, or an asset.

## JSON Example

This sample response shows resources that include grants, if applicable, and resources without rates when you retrieve the usage details of an order item.

```
{
  "records": [
    {
      "bindingInstanceTargetType": null,
      "bindingInstanceType": null,
      "chargeForOverages": "Yes",
      "isOptional": false,
      "fields": {},
      "name": "API Calls",
      "negotiable": ",",
      "negotiatedRate": null,
      "negotiatedRateCardEntryId": ",",
      "quantity": 1000,
      "rate": null,
      "rateAdjustments": [],
      "rateCardEntryId": ",",
      "rateUnitOfMeasureName": "USD",
      "unitOfMeasure": null,
      "usageResourceGrantAndPolicyDetail": {
        "grantDetail": {
          "grantType": "Grant",
          "id": "1BXxx0000004C9lGAE",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedGrantDetail": {
          "grantType": "Grant",
          "id": "1X6xx00000000OECAY",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedResourcePolicyDetail": {
          "id": "1X5xx00000000OECAY",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        },
        "resourcePolicyDetail": {
          "id": "7Suxx0000004C9kCAE",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        }
      },
      "usageResourceId": "1BRxx0000004C9CGAU"
    }
  ]
}
```

This example shows a sample response without negotiated rates when you retrieve the usage details of an order item.

```
{
  "records": [
    {
      "bindingInstanceTargetType": "Product",
      "bindingInstanceType": "Target",
      "chargeForOverages": "Yes",
      "isOptional": false,
      "fields": {},
      "name": "Paddle Board",
      "negotiable": "Negotiable,Non-Negotiable",
      "negotiatedRate": null,
      "negotiatedRateCardEntryId": ",",
      "quantity": 15,
      "rate": 5,
      "rateAdjustments": [
        {
          "fields": {},
          "lowerBound": 0,
          "name": null,
          "negotiatedRateAdjustmentId": null,
          "rateAdjustmentId": "1ENxx0000004C9BGAU",
          "rateAdjustmentType": "Percentage",
          "rateAdjustmentValue": 10,
          "tierUnitOfMeasure": "USD",
          "upperBound": 50
        }
      ],
      "rateCardEntryId": "1CJxx0000004C9IGAU,1CJxx0000004C9JGAU",
      "rateUnitOfMeasureName": "USD",
      "unitOfMeasure": "GB",
      "usageResourceGrantAndPolicyDetail": {
        "grantDetail": {
          "grantType": "Grant",
          "id": "1BXxx0000004C9lGAE",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedGrantDetail": {
          "grantType": "Grant",
          "id": "1X6xx00000000OECAY",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedResourcePolicyDetail": {
          "id": "1X5xx00000000OECAY",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        },
        "resourcePolicyDetail": {
          "id": "7Suxx0000004C9kCAE",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        }
      },
      "usageResourceId": "1BRxx0000004C9CGAU"
    }
  ]
}
```

This sample response shows negotiated rates when you retrieve the usage details of an order item. The negotiated rates are derived from these objects for assets, order items, or quote line items.

- AssetRateCardEntry

- AssetRateAdjustment

- OrderItemRateCardEntry

- OrderItemRateAdjustment

- QuoteLineRateCardEntry

- QuoteLineRateAdjustment

```
{
  "records": [
    {
      "bindingInstanceTargetType": "Product",
      "bindingInstanceType": "Target",
      "chargeForOverages": "Yes",
      "isOptional": false,
      "fields": {},
      "name": "Paddle Board",
      "negotiable": "Negotiable,Non-Negotiable",
      "negotiatedRate": 20,
      "negotiatedRateCardEntryId": "1ELxx0000004C9JGAU,1ELxx0000004C9KGAU",
      "quantity": 15,
      "rate": 5,
      "rateAdjustments": [
        {
          "fields": {},
          "lowerBound": 0,
          "name": "Tier 1",
          "negotiatedRateAdjustmentId": "1ENxx0000004C9BGAU",
          "rateAdjustmentId": "1ENxx0000004C9BGAU",
          "rateAdjustmentType": "Percentage",
          "rateAdjustmentValue": 10,
          "tierUnitOfMeasure": "USD",
          "upperBound": 50
        }
      ],
      "rateCardEntryId": "1CJxx0000004C9IGAU,1CJxx0000004C9JGAU",
      "rateUnitOfMeasureName": "USD",
      "unitOfMeasure": "GB",
      "usageResourceGrantAndPolicyDetail": {
        "grantDetail": {
          "grantType": "Grant",
          "id": "1BXxx0000004C9lGAE",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedGrantDetail": {
          "grantType": "Grant",
          "id": "1X6xx00000000OECAY",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedResourcePolicyDetail": {
          "id": "1X5xx00000000OECAY",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        },
        "resourcePolicyDetail": {
          "id": "7Suxx0000004C9kCAE",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        }
      },
      "usageResourceId": "1BRxx0000004C9CGAU"
    }
  ]
}
```

This sample response shows details of the custom fields when you retrieve the usage details of an order item.

```
{
  "records": [
    {
      "fields": {
        "MyCustomDate__c": {
          "displayValue": "2024-09-24",
          "value": "2024-09-24T17:46:30.662Z"
        },
        "MyCustomNumber__c": {
          "displayValue": "20.0",
          "value": 20
        }
      },
      "isOptional": false,
      "bindingInstanceTargetType": "Product",
      "bindingInstanceType": "Target",
      "chargeForOverages": "Yes",
      "name": "Therapy",
      "negotiable": "Negotiable,Non-Negotiable",
      "negotiatedRate": 20,
      "negotiatedRateCardEntryId": "1ELxx0000004C9JGAU,1ELxx0000004C9KGAU",
      "quantity": 15,
      "rate": 5,
      "rateAdjustments": [
        {
          "fields": {
            "MyCustomString__c": {
              "displayValue": "My Custom String",
              "value": "MyCustomString"
            }
          },
          "lowerBound": 0,
          "name": "Tier 1",
          "negotiatedRateAdjustmentId": "1ENxx0000004C9BGAU",
          "rateAdjustmentId": "1ENxx0000004C9BGAU",
          "rateAdjustmentType": "Percentage",
          "rateAdjustmentValue": 10,
          "tierUnitOfMeasure": "USD",
          "upperBound": 50
        }
      ],
      "rateCardEntryId": "1CJxx0000004C9IGAU,1CJxx0000004C9JGAU",
      "rateUnitOfMeasureName": "USD",
      "unitOfMeasure": "GB",
      "usageResourceGrantAndPolicyDetail": {
        "grantDetail": {
          "grantType": "Grant",
          "id": "1BXxx0000004C9lGAE",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedGrantDetail": {
          "grantType": "Grant",
          "id": "1X6xx00000000OECAY",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedResourcePolicyDetail": {
          "id": "1X5xx00000000OECAY",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        },
        "resourcePolicyDetail": {
          "id": "7Suxx0000004C9kCAE",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        }
      },
      "usageResourceId": "1BRxx0000004C9CGAU"
    }
  ]
}
```

This sample response shows values for the type and target type of a binding instance if the `BindingInstanceTargetId` value is available in the QuoteLineItem, OrderItem, and AssetStatePeriod objects. Additionally, the rate, negotiated rates, and rate card entry values show the associated details of the binding object.

```
{
  "records": [
    {
      "bindingInstanceTargetType": "Account",
      "bindingInstanceType": "Target",
      "chargeForOverages": "Yes",
      "fields": {},
      "isOptional": false,
      "name": "Data Transfers",
      "negotiable": "Non-Negotiable,Non-Negotiable",
      "negotiatedRate": null,
      "negotiatedRateCardEntryId": "1QNxx0000004CQmGAM,1QNxx0000004CLwGAM",
      "quantity": 250,
      "rate": 0.098765,
      "rateAdjustments": [
        {
          "fields": {},
          "lowerBound": 0,
          "name": null,
          "negotiatedRateAdjustmentId": null,
          "rateAdjustmentId": "1Soxx0000004CAeCAM",
          "rateAdjustmentType": "Percentage",
          "rateAdjustmentValue": 0,
          "tierUnitOfMeasure": "USD",
          "upperBound": 121
        }
      ],
      "rateCardEntryId": "1CJxx0000004C9CGAU,1CJxx0000004C9GGAU",
      "rateUnitOfMeasureName": "USD",
      "unitOfMeasure": "GB",
      "usageResourceGrantAndPolicyDetail": {
        "grantDetail": {
          "grantType": "Grant",
          "id": "1BXxx0000004C9lGAE",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedGrantDetail": {
          "grantType": "Grant",
          "id": "1X6xx00000000OECAY",
          "quantity": 100,
          "usageGrantNegotiable": "Negotiable",
          "usageRefreshPolicy": {
            "id": "1BYxx0000004C92GAE",
            "negotiable": "Non-Negotiable"
          },
          "usageRolloverPolicy": {
            "id": "1BVxx0000004C93GAE",
            "negotiable": "Non-Negotiable"
          },
          "validityPeriodTerm": 1,
          "validityPeriodUnit": "Month"
        },
        "negotiatedResourcePolicyDetail": {
          "id": "1X5xx00000000OECAY",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        },
        "resourcePolicyDetail": {
          "id": "7Suxx0000004C9kCAE",
          "ratingFrequencyPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageAggregationPolicy": {
            "id": null,
            "negotiable": null
          },
          "usageCommitmentPolicy": {
            "id": "7Pexx0000004C92CAE",
            "negotiable": "Non-Negotiable"
          },
          "usageOveragePolicy": {
            "id": null,
            "negotiable": null
          }
        }
      },
      "usageResourceId": "1BRxx0000004C9CGAU"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Usage Detail Error Response](./connect-responses-usage-detail-error-response.md)[] | List of errors encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `records` | [Rate Card Entry](./connect-responses-rate-card-entry-output.md)[] | List of rate card entry records. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
