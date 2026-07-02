---
page_id: connect_responses_billing_arrangement_line.htm
title: Billing Arrangement Line
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_arrangement_line.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Billing Arrangement Line

Output representation that contains the details of a specific line item within a billing
arrangement, defining how charges are split for an account.

JSON example
:   ```
    {
      "billingArrangementLineId": "1blxx000000006TAAQ",
      "accountId": "accId1",
      "billingAccountId": "bAccId1",
      "isRemainderAdjustmentAccount": false,
      "percentage": 60.00
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account associated with the billing line. | Big, 66.0 | 66.0 |
| `billing​AccountId` | String | ID of the billing account responsible for this portion of the bill. | Big, 66.0 | 66.0 |
| `billingArrangement​LineId` | String | Unique ID of the billing arrangement line. | Big, 66.0 | 66.0 |
| `isRemainder​AdjustmentAccount` | Boolean | Indicates whether the specific line is designated as the adjustment account for any remainder (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `percentage` | Double | Percentage of the charge allocated to this line. | Big, 66.0 | 66.0 |
