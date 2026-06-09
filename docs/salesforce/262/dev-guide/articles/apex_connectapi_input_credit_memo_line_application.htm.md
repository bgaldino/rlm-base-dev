---
page_id: apex_connectapi_input_credit_memo_line_application.htm
title: ConnectApi.CreditDetailsApplyInput
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_line_application.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditDetailsApplyInput

Input representation of the request to specify one or more applications to apply a credit
memo line for, with each application representing an invoice line.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `appliedAmount` | Double | Credit amount to be applied to the invoice line. | Required | 62.0 |
| `description` | String | Explanation or reason for applying the credit memo line. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo line. | Optional | 62.0 |
| `invoiceLineId` | String | ID of the invoice line record to apply the credit for. | Required | 62.0 |
