---
page_id: connect_responses_invoice_batch_run_recovery_output.htm
title: Invoice Batch Run Recovery
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_batch_run_recovery_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Invoice Batch Run Recovery

Output representation of the details of the invoice batch run recovery
record.

JSON example
:   ```
    {
      "invoiceBatchRunRecoveryId": ["0wBxx0000004TtwGAU"]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatchRun​RecoveryId` | String | ID of the invoice batch run recovery record for the specified invoice batch run. This record represents the background recovery process. | Small, 62.0 | 62.0 |
