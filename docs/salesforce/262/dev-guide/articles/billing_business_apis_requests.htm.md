---
page_id: billing_business_apis_requests.htm
title: Request Bodies
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_business_apis_requests.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_api_overview.htm
fetched_at: 2026-06-09
---

# Request Bodies

Learn more about the available request bodies of Billing APIs.

- **[Address Input](./connect_requests_address_input.htm.md)**  
  Input representation of the details of an address.
- **[Addresses Input](./connect_requests_addresses_input.htm.md)**  
  Input representation of the details of the addresses for calculating tax.
- **[Batch Invoice Filter Criteria Input](./connect_requests_batch_invoice_filter_criteria_input.htm.md)**  
  Input representation of the filter criteria for an invoice batch run.
- **[Batch Invoice Scheduler Input](./connect_requests_batch_invoice_scheduler_input.htm.md)**  
  Input representation of the details of the request to create an invoice scheduler.
- **[Billing Schedule Recovery Input](./connect_requests_billing_schedule_recovery_input.htm.md)**  
  Input representation of the details of the billing schedules to recover the associated invoice.
- **[Context-Aware Billing Schedule](./connect_requests_context_aware_billing_schedule_input.htm.md)**  
  Input representation of the billing transaction details.
- **[Standalone Billing Schedule Input](./connect_requests_context_aware_standalone_billing_schedule_input.htm.md)**  
  Input representation of the request to create a billing schedule based on transaction details. This representation includes the transaction and context service details.
- **[Standalone Billing Schedule Metadata Input](./connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm.md)**  
  Input representation of the metadata details to create a billing schedule. This representation includes the name of the context definition and context mapping along with the mapping details of the transaction, billing schedule, and billing schedule group.
- **[Convert Negative Invoice Lines Input](./connect_requests_convert_negative_invoice_lines_input.htm.md)**  
  Input representation of the details of the request to convert a list of negative invoice lines into a credit.
- **[Credit Invoice Input](./connect_requests_credit_invoice_input.htm.md)**  
  Input representation of the details of the request to create a credit memo.
- **[Credit Invoice Line Input](./connect_requests_credit_invoice_line_input.htm.md)**  
  Input representation of the details of the invoice lines to be credited.
- **[Credit Invoice Line Tax Input](./connect_requests_credit_invoice_line_tax_input.htm.md)**  
  Input representation of the details of the tax lines to be created manually for the invoice line.
- **[Credit Memo Addresses Input](./connect_requests_credit_memo_addresses_input.htm.md)**  
  Input representation of the details of the billing and shipping addresses.
- **[Credit Memo Apply Input](./connect_requests_credit_memo_apply_input.htm.md)**  
  Input representation of the request to apply a credit memo to an invoice.
- **[Credit Memo Apply Application Input](./connect_requests_credit_memo_apply_application_input.htm.md)**  
  Input representation of the request to specify one or more applications to apply a credit memo for, with each application representing an invoice.
- **[Credit Memo Draft to Posted Input](./connect_requests_credit_memo_draft_to_posted_input.htm.md)**  
  Input representation of the request to post a draft credit memo.
- **[Credit Memo Unapply Input](./connect_requests_credit_memo_unapply_input.htm.md)**  
  Input representation of the request to unapply a credit memo from an invoice.
- **[Credit Memo Line Apply Input](./connect_requests_credit_memo_line_apply_input.htm.md)**  
  Input representation of the details of the request to apply a credit memo line to an invoice line.
- **[Credit Memo Line Application Input](./connect_requests_credit_memo_line_application_input.htm.md)**  
  Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.
- **[Credit Memo Line Unapply Input](./connect_requests_credit_memo_line_unapply_input.htm.md)**  
  Input representation of the details of the request to unapply a credit memo line from an invoice line.
- **[Customer Details Input](./connect_requests_customer_details_input.htm.md)**  
  Input representation of the customer details for tax calculation.
- **[Frequency Cadence Options](./connect_requests_frequency_cadence_options.htm.md)**  
  Input representation of the frequency cadence options for an invoice scheduler.
- **[Graph Record for Invoice Ingestion](./connect_requests_graph_record_input.htm.md)**  
  A Graph record is an object that’s a part of the graph structure, representing both the fields and relationships among different objects. Each record in the graph can contain attributes, which are fields of the object, and references to other related records.
- **[Invoice Draft To Posted Input](./connect_requests_draft_to_posted_invoice_input.htm.md)**  
  Input representation of the details of the draft invoice that’s posted.
- **[Invoice Estimated Tax Calculation Input](./connect_requests_invoice_estimated_tax_calculation_input.htm.md)**  
  Details of the invoice for which the estimated tadsfsefx must be calculated.
- **[Invoice Ingestion Input](./connect_requests_invoice_ingestion_input.htm.md)**  
  Input representation of the details of the invoice to be processed. The details include the tax processing status, user preferences for tax callouts, and associated object graph representation.
- **[Invoice Input for Ingestion](./connect_requests_invoice_input_for_ingestion.htm.md)**  
  Input representation of the details of the invoice that must be generated for or ingested into Billing.
- **[Invoice Input](./connect_requests_invoice_input.htm.md)**  
  Input representation of the details of the billing schedule.
- **[Invoice Preview Input](./connect_requests_invoice_preview_input.htm.md)**  
  Input representation of the details of the billing transaction that the preview invoices are generated for.
- **[Line Item Input](./connect_requests_line_item_input.htm.md)**  
  Input representation of the details of the line item for tax calculation.
- **[On-Demand Document Generation Input](./connect_requests_on_demand_doc_gen_input.htm.md)**  
  Input representation of the details to generate a comprehensive on-demand document for specified record types.
- **[Payment Line Apply Input](./connect_requests_payment_line_apply_input.htm.md)**  
  Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields such as associated account and effective date.
- **[Payment Line Unapply Input](./connect_requests_payment_line_unapply_input.htm.md)**  
  Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application to their preapplication state.
- **[Payment Run Batch Filter Criteria Input](./connect_requests_payment_run_batch_filter_criteria_input.htm.md)**  
  Input representation of the filter criteria for an invoice batch run. This representation covers the criteria and sequence for filtering payment run details. It specifies the field and object names, comparison operations, and values to be used for filtering.
- **[Payment Batch Scheduler Input](./connect_requests_payment_scheduler_input.htm.md)**  
  Input representation of the details of the request to create a payment scheduler. This representation sets the rules and timing for a payment scheduler, including match types, dates, frequency, and filter criteria.
- **[Payment Scheduler Update Input](./connect_requests_payment_scheduler_update_input.htm.md)**  
  Input representation of the details of the request to update the status of a payment scheduler. This representation defines the status of a payment scheduler, which can be set to Active, Canceled, Draft, or Inactive.
- **[Posted Invoice List Write-Off Input](./connect_requests_write_off_posted_invoice_list_input.htm.md)**  
  Input representation of the request to write off a list of posted invoices. This representation includes the details of invoices that you want to write off.
- **[Posted Invoice Write-Off Input](./connect_requests_write_off_posted_invoice_input.htm.md)**  
  Input representation of the details of the request to write off a posted invoice. This representation includes invoice details such as invoice ID and reason for writing off invoices.
- **[Refund Line Apply Input](./connect_requests_refund_line_apply_input.htm.md)**  
  Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.
- **[Resume Billing Input](./connect_requests_resume_billing_input.htm.md)**  
  Input representation of the details of the request to resume the billing operation for an account or a billing schedule group.
- **[Resume Billing Object Input](./connect_requests_resume_billing_entity_input.htm.md)**  
  Input representation of the details such as the ID of the account or billing schedule group along with the effective date. These details are used to start the billing operation.
- **[Rules Application Input](./connect_requests_rules_application_input.htm.md)**  
  Input representation for applying payments and credits to invoices based on rules.
- **[Selection Condition Input](./connect_requests_selection_condition_input.htm.md)**  
  Input representation of the criteria that's used to determine which sequencing policy is applied to a record. The criteria stores the conditions based on any standard or custom fields of the record.
- **[Seller Details Input](./connect_requests_seller_details_input.htm.md)**  
  Input representation of the seller details for tax calculation.
- **[Send Email Input](./connect_requests_send_email_for_invoice_batch_run_input.htm.md)**  
  Input representation of the request to send an email for an invoice batch run.
- **[Sequence Policy Input](./connect_requests_sequence_policy_input.htm.md)**  
  Input representation of the configured rules and properties to generate unique, sequential numbers for objects.
- **[Sequence Gap Reconciliation Input](./connect_requests_sequence_gap_reconciliation_input.htm.md)**  
  Input representation of the details that are used to identify and reconcile gaps in sequence values based on the sequence policy or target object.
- **[Sequences Assignment Input](./connect_requests_sequences_assignment_input.htm.md)**  
  Input representation of the details of the target objects to which the sequence pattern values are assigned.
- **[Standalone Credit Memo Charge Input](./connect_requests_standalone_credit_memo_charge_input.htm.md)**  
  Input representation of the details of the charge lines of a credit memo.
- **[Standalone Credit Memo Input](./connect_requests_standalone_credit_memo_input.htm.md)**  
  Input representation of the details required to create a standalone credit memo.
- **[Standalone Credit Memo Tax Input](./connect_requests_standalone_credit_memo_tax_input.htm.md)**  
  Input representation of the details of the tax request.
- **[Account Statement Input](./connect_requests_statement_of_account_input.htm.md)**  
  Input representation of the details required to generate a comprehensive account statement with transaction history and balance information.
- **[Suspend Billing Input](./connect_requests_suspend_billing_input.htm.md)**  
  Input representation of the details of the request to suspend the billing operation for an account or a billing schedule group.
- **[Suspend Billing Object Input](./connect_requests_suspend_billing_entity_input.htm.md)**  
  Input representation of the details such as the ID of the account or billing schedule group along with the effective dates. These details are used to suspend the billing operation.
- **[Tax Calculation Input](./connect_requests_calculate_tax_input.htm.md)**  
  Input representation of the details of the request to calculate tax.
- **[Void Posted Credit Memo Input](./connect_requests_void_posted_credit_memo_input.htm.md)**  
  Input representation of the details of a credit memo to be voided.
- **[Void Posted Invoice Input](./connect_requests_void_posted_invoice_input.htm.md)**  
  Input representation of the details of the invoice to be voided.
