---
page_id: apex_connectapi_input_credit_memo_unapply.htm
title: ConnectApi.CreditMemoUnapplyInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_unapply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditMemoUnapplyInputRequest

Input representation of the request to unapply a credit memo from an invoice.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemoInvApplicationId` | String | ID of the credit memo invoice application. | Required | 62.0 |
| `description` | String | Explanation or reason for unapplying the credit memo. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |
