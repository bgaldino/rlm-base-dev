---
page_id: connect_responses_policy_detail_output.htm
title: Policy Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_policy_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Policy Details

Output representation of the details of a policy.

JSON example
:   This example includes the details for different policy
    types.

    ```
    {
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
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the policy. | Big, 65.0 | 65.0 |
| `negotiable` | String | Indicates whether the policy is negotiable. Valid values are:   - `Negotiable` - `Non-Negotiable` | Big, 65.0 | 65.0 |
