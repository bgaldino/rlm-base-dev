---
page_id: apex_connectapi_input_credit_invoice_invoice_line_tax.htm
title: ConnectApi.CreditInvoiceInvoiceLineTax
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_invoice_invoice_line_tax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditInvoiceInvoiceLineTax

Input representation of the details of the tax lines to be created manually for the
invoice line.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `taxAmount` | Double | Amount of tax to be applied related to this invoice line. | Required | 62.0 |
| `taxCode` | String | Tax code to be applied related to this invoice line to create the tax line. | Optional | 62.0 |
| `taxName` | String | Name of tax to be applied related to this invoice line. | Optional | 62.0 |
| `taxRate` | Double | Tax rate used to create the tax line. | Optional | 62.0 |
