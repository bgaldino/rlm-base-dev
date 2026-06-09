---
page_id: connect_responses_credit_memo_apply_list_output.htm
title: Credit Memo Apply List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_apply_list_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Credit Memo Apply List

Output representation of the list of applied credit memo results.

JSON example
:   ```
    {
      "applyCreditResults" : [ {
        "appliedToId" : "3ttxx000000003FAAQ",
        "errors" : null,
        "id" : "4sFxx00000002ppEAA",
        "success" : true
      }, {
        "appliedToId" : "3ttxx0000000001AAA",
        "errors" : null,
        "id" : "4sFxx00000002pqEAA",
        "success" : true
      } ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applyCredit​Results` | [Credit Memo Apply](./connect_responses_credit_memo_apply_output.htm.md "Output representation of the list of applied credit memo results.")[] | Output list of the applied credit memo results. | Big, 62.0 | 62.0 |
