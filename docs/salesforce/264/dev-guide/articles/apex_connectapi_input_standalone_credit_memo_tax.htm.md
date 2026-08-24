---
page_id: apex_connectapi_input_standalone_credit_memo_tax.htm
title: ConnectApi.StandaloneCreditMemoTaxInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_standalone_credit_memo_tax.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.StandaloneCreditMemoTaxInputRequest

Connect API representation of Tax input request

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `taxAmount` | Double | Amount of tax to be applied. | Required | 62.0 |
| `taxCode` | String | Tax code to be used to create the tax line. | Optional | 62.0 |
| `taxName` | String | Name of tax to be applied. | Optional | 62.0 |
| `taxRate` | Double | Tax rate to be used to create the tax line. | Optional | 62.0 |
