---
article_id: release-notes.rn_billing_new_changed_connect_rest_apis.htm
title: New and Changed Connect REST APIs in Billing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_new_changed_connect_rest_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-09-30
---

# New and Changed Connect REST APIs in Billing

Improve checkout-to-cash operations for non-referenced refunds and unified checkout orchestration. You can also automate migration and invoicing workflows more effectively with enhanced scheduler controls, custom credit memo field support, custom billing cycle count, and flexible target-date billing behavior.

New Connect REST API Resources
Issue refunds directly against credit memos

Make a POST request to the new /revenue/billing/refunds/unreferenced-refunds/actions/process resource.

New request body: Refund Credit Memo Input

New response body: Refund Credit Memo

Create a unified checkout transaction for invoicing and payment

Make a POST request to the new /commerce/invoicing/invoices/collection/actions/checkout resource.

New request body: Billing Checkout Input

New response body: Billing Checkout

Create collection plans and their associated items in a single request

Make a POST request to the new /connect/collections/composite-collection-plan resource.

New request body: Composite Collection Plan Input

New response body: Composite Collection Plan

Changed Connect REST API Request Bodies
Batch Invoice Scheduler Input

This request body has these new properties.

jobType—Specifies the type of job the scheduler is running.
shouldRecalculateAllForecastLn—Indicates whether to select all billing schedules regardless of forecast status or eligible ones only.
shouldCatchUpBillRun—Indicates whether the invoice batch run must advance billing schedules to a target date without generating invoices for prior billing periods.
targetDayOfMonth—Specifies the day-of-month rule used to calculate the target date.
targetMonthOffset—Specifies the month offset used to calculate the target date.
billingCycleCount—Specifies the number of billing cycles to be invoiced.
Schedule Options Input

This request body has this new property.

shouldGenerateInvoiceDocuments—Indicates whether invoice documents are automatically generated during batch processing for runs triggered by the scheduler.
Standalone Credit Memo Input

This request body has this new property.

customFields—Specifies custom field values on the credit memo record.
Standalone Credit Memo Charge Input

This request body has this new property.

customFields—Specifies custom field values on each credit memo line in the charges list.
SEE ALSO
Revenue Cloud Developer Guide: Billing Business APIs
