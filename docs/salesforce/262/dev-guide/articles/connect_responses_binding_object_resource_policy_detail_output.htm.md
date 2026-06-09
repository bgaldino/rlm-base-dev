---
page_id: connect_responses_binding_object_resource_policy_detail_output.htm
title: Binding Object Resource Policy Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_binding_object_resource_policy_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Binding Object Resource Policy Detail

Output representation of the details of a usage resource policy.

JSON example
:   This example includes the details of a usage resource
    policy.

    ```
    {
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
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `drawdown​Order` | String | Specifies the order or way to process the drawdown. See [Usage Management Essentials](https://help.salesforce.com/s/articleView?id=ind.usage_management_essentials.htm&language=en_US "HTML (New Window)") to know more about a drawdown process. | Big, 65.0 | 65.0 |
| `id` | String | ID of the `Binding Object Usage Resource Policy` record. | Big, 65.0 | 65.0 |
| `ratingFrequency​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | Details of the rating frequency policy. | Big, 65.0 | 65.0 |
| `usageAggregation​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | Details of the usage aggregation policy. | Big, 65.0 | 65.0 |
| `usageCommitment​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | Details of the commitment policy of the usage resource. | Big, 65.0 | 65.0 |
| `usageOverage​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | Details of the overage policy of the usage resource. | Big, 65.0 | 65.0 |
