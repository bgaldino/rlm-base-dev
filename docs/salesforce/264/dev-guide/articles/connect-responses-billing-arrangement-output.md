---
page_id: connect-responses-billing-arrangement-output
title: Billing Arrangement
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-arrangement-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_billing_arrangement_output.htm
fetched_at: 2026-11-25
---

# Billing Arrangement

Output representation that contains the details of a billing arrangement, including its status, configuration settings, and associated lines.

## JSON Example

```
{
  "billingArrangementId": "1bdxx000000004rAAA",
  "name": "Acme Shared Billing Definition",
  "isAdjustmentToOwnAccount": true,
  "remainderPercentage": 15,
  "versionNumber": 1,
  "numOfAssociatedBSGs": 5,
  "status": "Active",
  "billingArrangementLines": [
    {
      "billingArrangementLineId": "1blxx000000006TAAQ",
      "accountId": "accId1",
      "billingAccountId": "bAccId1",
      "isRemainderAdjustmentAccount": false,
      "percentage": 60
    },
    {
      "billingArrangementLineId": "1blxx000000001dAAA",
      "accountId": "accId2",
      "billingAccountId": "bAccId2",
      "isRemainderAdjustmentAccount": false,
      "percentage": 25
    }
  ],
  "isSuccess": true,
  "error": null
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​ArrangementId` | String | Unique ID of the billing arrangement. | Big, 66.0 | 66.0 |
| `billing​ArrangementLines` | [Billing Arrangement Line](./connect-responses-billing-arrangement-line.md)[] | List of billing arrangement lines associated with the latest version of the billing arrangement. | Big, 66.0 | 66.0 |
| `error` | [Error Response Output](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | Error details if the request was unsuccessful. | Big, 66.0 | 66.0 |
| `isAdjustment​ToOwnAccount` | Boolean | Indicates whether the remainder of the bill is adjusted to the owning account (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `isSuccess` | Boolean | Indicates whether the request was successfully processed (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `name` | String | Name of the billing arrangement. | Big, 66.0 | 66.0 |
| `numOf​AssociatedBSGs` | Integer | Total number of billing schedule groups associated with the billing arrangement. | Big, 66.0 | 66.0 |
| `remainderPercentage` | Double | Remaining percentage of the bill after all line allocations are calculated. | Big, 66.0 | 66.0 |
| `status` | String | Status of the billing arrangement. Valid values are `Draft`, `Active`, or `Inactive`. | Big, 66.0 | 66.0 |
| `versionNumber` | Integer | Current version number of the billing arrangement. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-arrangement-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
