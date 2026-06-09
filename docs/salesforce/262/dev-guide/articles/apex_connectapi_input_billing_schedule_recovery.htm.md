---
page_id: apex_connectapi_input_billing_schedule_recovery.htm
title: ConnectApi.BillingScheduleRecoveryInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_billing_schedule_recovery.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.BillingScheduleRecoveryInputRepresentation

Input representation of the details of the billing schedules to recover the associated
invoice.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Schedule​Ids` | List<`String`> | IDs of the billing schedules to recover the invoice for. You can recover one billing schedule per API request. | Required | 62.0 |
