---
page_id: apex_connectapi_input_invoice.htm
title: ConnectApi.InvoiceInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_invoice.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.InvoiceInputRepresentation

Input representation of the details of the billing schedule.

- 
- 

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | `ConnectApi.InvoiceAction` | Type of invoice to be created. Valid values are: `Draft` `Posted` | Required | 62.0 |
| `billing​ScheduleIds` | List<`String`> | List of billing schedule IDs that’s used to create the invoices. You can specify a maximum of 200 billing schedules. | Required | 62.0 |
| `correlation​Id` | String | Property that’s tagged against the published `InvoiceProcessedEvent` event, if specified. | Optional | 62.0 |
| `invoice​Date` | String | Stamping date of the invoice in ISO 8601 format. | Required | 62.0 |
| `target​Date` | String | Date in ISO 8601 format used to decide the billing periods that are included to create invoices. | Required | 62.0 |
