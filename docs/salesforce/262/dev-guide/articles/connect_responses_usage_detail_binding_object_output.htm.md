---
page_id: connect_responses_usage_detail_binding_object_output.htm
title: Binding Object Usage Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_detail_binding_object_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Binding Object Usage Detail

Output representation of the usage details of a binding object.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "records": [
        {
          "bindingObjectRate": {
            "id": "1QNSB0000001JyH4AU,1QNSB0000001JyI4AU",
            "negotiatedRate": null,
            "negotiatedRateAdjustments": [
              {
                "lowerBound": 101,
                "name": null,
                "rateAdjustmentId": "1DMSB000001N3C74AK",
                "rateAdjustmentType": "Amount",
                "rateAdjustmentValue": 10,
                "tierUnitOfMeasure": "USD",
                "upperBound": null
              },
              {
                "lowerBound": 1,
                "name": null,
                "rateAdjustmentId": "1DMSB000001N3C64AK",
                "rateAdjustmentType": "Percentage",
                "rateAdjustmentValue": 30,
                "tierUnitOfMeasure": "USD",
                "upperBound": 100
              }
            ],
            "rate": 100,
            "rateCardEntryId": "1CJSB000000207R4AQ,1CJSB000000207S4AQ",
            "rateUnitOfMeasureName": "USD"
          },
          "bindingObjectResourceGrantAndPolicyDetail": {
            "bindingObjectGrantDetail": [
              {
                "effectiveEndDate": "Sat Oct 04 23:59:59 GMT 2025",
                "effectiveStartDate": "Fri Sep 05 00:00:00 GMT 2025",
                "grantType": "Grant",
                "id": "1B0SB0000000Eiv0AE",
                "product": {
                  "id": "01tSB000006XMtqYAG"
                },
                "quantity": 100,
                "record": {
                  "id": "02iSB000000IoETYA0"
                },
                "unitOfMeasure": {
                  "id": "0hESB0000003yfp2AA"
                },
                "usageRefreshPolicy": {
                  "id": "1BYSB0000001lOH4AY",
                  "negotiable": null
                },
                "usageRolloverPolicy": {
                  "id": "1BVSB000000A1xJ4AS",
                  "negotiable": null
                },
                "validityPeriodTerm": 1,
                "validityPeriodUnit": "Month"
              }
            ],
            "bindingObjectResourcePolicyDetail": {
              "drawdownOrder": "ExpiringFirst",
              "id": "1X2SB00000002WT0AY",
              "ratingFrequencyPolicy": {
                "id": "1HJSB0000000G3B4AU",
                "negotiable": null
              },
              "usageAggregationPolicy": {
                "id": "1cfSB0000001xHPYAY",
                "negotiable": null
              },
              "usageCommitmentPolicy": {
                "id": null,
                "negotiable": null
              },
              "usageOveragePolicy": {
                "id": "7UkSB00000002OP0AY",
                "negotiable": null
              }
            }
          },
          "usageResource": {
            "id": "1BRSB0000001x4h4AA"
          }
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Usage Detail Error Response](./connect_responses_usage_detail_error_response.htm.md "Output representation of the details of an error related to usage details.")[] | List of errors encountered during the processing of the API request. | Small, 65.0 | 65.0 |
| `records` | [Binding Object Detail](./connect_responses_binding_object_detail_output.htm.md "Output representation of the list of records with the binding target details.")[] | List of records that contains the binding target details. | Small, 65.0 | 65.0 |
