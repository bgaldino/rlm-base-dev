---
page_id: connect_responses_rate_card_entry_output.htm
title: Rate Card Entry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rate_card_entry_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Rate Card Entry

Output representation of the details of a rate card entry.

JSON Example
:   ```
    {
      "records": [
        {
          "bindingInstanceTargetType": "Product",
          "bindingInstanceType": "Target",
          "chargeForOverages": "Yes",
          "fields": {},
          "isOptional": false,
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

If the `negotiable` property value is blank, then the
data is derived from Product Catalog Management. If it isn’t blank, then the data is derived
from Rate Management.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `binding​Instance​TargetType` | String | Type of the target object that's associated with this transaction. | Big, 63.0 | 63.0 |
| `bindingInstance​Type` | String | Type of the binding instance. Valid values are:   - `Self` - `Target` | Big, 63.0 | 63.0 |
| `chargeFor​Overages` | String | Specifies whether overage is permitted. Valid values are:   - `Yes` - `No` - `NA` | Big, 63.0 | 63.0 |
| `fields` | Map<String, [Fields Response](./connect_responses_fields_output.htm.md "Output representation of the details of the optional fields on the usage-based selling-related objects.")> | List of optional fields and their values that's associated with the rate card entry object. | Big, 63.0 | 63.0 |
| `isOptional` | Boolean | Indicates whether the product usage resource is optional when the associated product is one of the commitment usage model types (`true`) or not (`false`). | Big, 65.0 | 65.0 |
| `name` | String | Name of the resource. | Big, 63.0 | 63.0 |
| `negotiable` | String | Type of the base rate and the tier rate, if applicable. Valid values are:   - `Negotiable` - `Non-Negotiable` | Big, 63.0 | 63.0 |
| `negotiated​Rate` | Double | User-overridden overage rate. | Big, 63.0 | 63.0 |
| `negotiated​RateCard​EntryId` | String | ID of the negotiated rate card entry and the tier rate card entry, if applicable. | Big, 63.0 | 63.0 |
| `quantity` | Double | Amount granted for the resource. | Big, 63.0 | 63.0 |
| `rate` | Double | Base overage rate. | Big, 63.0 | 63.0 |
| `rate​Adjustments` | [Rate Adjustments](./connect_responses_rate_adjustments_output.htm.md "Output representation of the details of a rate adjustment.")[] | List of tiers associated with the rate card entry, if applicable. | Big, 63.0 | 63.0 |
| `rateCard​EntryId` | String | ID of the base rate card entry and the tier rate card entry, if applicable. | Big, 63.0 | 63.0 |
| `rateUnit​OfMeasure​Name` | String | Unit of measure for rates in the rate card entry. | Big, 64.0 | 64.0 |
| `unitOf​Measure` | String | Unit of measure of the grant. For example, `Unit`. | Big, 63.0 | 63.0 |
| `usageResource​Id` | String | ID of the usage resource. | Big, 65.0 | 65.0 |
| `usageResource​GrantAndPolicy​Detail` | [Usage Resource Grant And Policy Detail](./connect_responses_usage_resource_grant_and_policy_detail_output.htm.md "Output representation of the details of a usage resource grant and policy.") | Details of a usage resource grant and policy. | Big, 65.0 | 65.0 |
