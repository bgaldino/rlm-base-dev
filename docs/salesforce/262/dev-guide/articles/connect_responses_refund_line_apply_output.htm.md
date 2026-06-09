---
page_id: connect_responses_refund_line_apply_output.htm
title: Refund Line Applied Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_refund_line_apply_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Refund Line Applied Response

Output representation of the details of an applied refund. This representation includes
the properties of a refund line, such as the date when the refund is applied against a payment
and ID of the refund line record.

JSON example
:   ```
    {
      "appliedDate": "2020-08-11T08:09:01.000Z",
      "id": "0dRR000000000CsMAI"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `appliedDate` | String | Date when the refund is applied against a payment. | Big, 64.0 | 64.0 |
| `id` | String | ID of the refund line record. | Big, 64.0 | 64.0 |
