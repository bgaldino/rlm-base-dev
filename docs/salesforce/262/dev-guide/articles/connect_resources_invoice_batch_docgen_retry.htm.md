---
page_id: connect_resources_invoice_batch_docgen_retry.htm
title: Batch Invoices Document Generation Retry (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_invoice_batch_docgen_retry.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Batch Invoices Document Generation Retry (POST)

Asynchronously regenerate PDF documents for the invoices that are in
the `Draft` or `Posted`
status and failed in an earlier invoice batch run.

Special Access Rules
:   This API is available with Revenue Cloud Billing. To use this API, enable Document
    Generation for Billing. Additionally, you need either the Billing Operations User
    permission set or the Billing Admin permission set, along with the Docgen Designer
    permission set and Docgen Designer Standard User permission set.

Resource
:   ```
    /commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName
    ```
:   - The invoiceBatchRunId parameter is the ID of the invoice batch
      run record that created the `Draft` or `Posted` invoices.
    - The actionName parameter is the name of the action you want to
      perform on the specified invoice batch run record. In this case, the action is to
      retry generating the `Draft` or `Posted` invoices that failed earlier.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/billing/invoices/invoice-batch-docgen/5IRxx0000004GSmGAM/actions/retry
    ```

Available version
:   63.0

HTTP methods
:   POST

Response body for POST
:   [Batch Invoice
    Document Generation](./connect_responses_batch_invoice_doc_gen_output.htm.md "Output representation of the request to generate or regenerate the PDF documents for the invoices that are in the Draft or Posted status.")
