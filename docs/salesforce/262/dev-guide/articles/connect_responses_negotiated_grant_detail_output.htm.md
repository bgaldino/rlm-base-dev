---
page_id: connect_responses_negotiated_grant_detail_output.htm
title: Grant Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_negotiated_grant_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Grant Detail

Output representation of the details of a grant from the ProductUsageGrant,
LineItemUsageResourceGrant, or TransactionUsageEntitlement objects.

JSON Example
:   ```
    {
      "negotiatedGrantDetail": {
        "grantType": "Grant",
        "id": "1X6xx00000000OECAY",
        "quantity": 100,
        "usageGrantNegotiable": "Negotiable",
        "usageRefreshPolicy": {
          "displayName": null,
          "id": "1BYxx0000004C92GAE",
          "negotiable": "Non-Negotiable"
        },
        "usageRolloverPolicy": {
          "displayName": null,
          "id": "1BVxx0000004C92GAE",
          "negotiable": "Non-Negotiable"
        },
        "validityPeriodTerm": 12,
        "validityPeriodUnit": "Month"
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `grantType` | String | Details about the grant type. | Big, 65.0 | 65.0 |
| `id` | String | ID of the usage resource grant. | Big, 65.0 | 65.0 |
| `quantity` | Double | Quantity of the negotiated usage resource grant. | Big, 65.0 | 65.0 |
| `usageGrant​Negotiable` | String | Specifies whether the grant is negotiable or not. | Big, 65.0 | 65.0 |
| `usageRefresh​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | ID of the usage grant refresh policy. | Big, 65.0 | 65.0 |
| `usageRollover​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md "Output representation of the details of a policy.") | ID of the usage grant rollover policy. | Big, 65.0 | 65.0 |
| `validity​PeriodTerm` | Double | Validity period term of the grant. | Big, 65.0 | 65.0 |
| `validity​PeriodUnit` | String | Validity period unit of the grant. | Big, 65.0 | 65.0 |
