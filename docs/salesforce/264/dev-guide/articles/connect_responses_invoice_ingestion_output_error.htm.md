---
page_id: connect_responses_invoice_ingestion_output_error.htm
title: Invoice Ingestion Output Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_ingestion_output_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Invoice Ingestion Output Error

Output representation of the details of an invoice generation error.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that indicates the type of error. | Small, 63.0 | 63.0 |
| `message` | String | Message that states the reason for error, if any. | Small, 63.0 | 63.0 |
| `reference​Id` | String | Reference ID that maps to the subrequest’s response and can be used to reference the response in later subrequests. | Small, 63.0 | 63.0 |
