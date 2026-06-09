---
page_id: billing_invocable_actions_parent.htm
title: Billing Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_invocable_actions_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-06-09
---

# Billing Standard Invocable Actions

Use standard invocable actions to automate processes such as credit application,
billing schedules creation, and invoice management.

## Commerce Payments Invocable Actions

This table provides a list of the
invocable actions of Commerce Payments, which can be used for Billing.

| Resource | Description |
| --- | --- |
| [`/services/data/v67.0/actions/standard/applyPayment`](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_obj_payment_apply.htm "HTML (New Window)") (POST) | Apply a payment record to an invoice header by creating a PaymentLineInvoice record with `Applied` type. |
| [`/services/data/v67.0/actions/standard/paymentSale`](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_obj_payment_sale.htm "HTML (New Window)") (POST) | Capture a payment without any prior authorization, and create a payment record. |

Billing provides these invocable actions.

- **[Apply Credit Action](./actions_obj_run_apply_credit.htm.md)**  
  Apply a credit memo or credit memo line to an invoice or invoice line, respectively.
- **[Apply Payments and Credits by Rules Action](./actions_obj_apply_rules.htm.md)**  
  Apply payments and credits to posted invoices by adhering to the specified rules.
- **[Automate Refund Action](./actions_obj_automate_refund.htm.md)**  
  Initiate refund orchestration for a credit memo generated from a subscription cancellation or negative amendment.
- **[Create Billing Schedules From Billing Transaction Action](./actions_obj_create_billing_schedule_from_billing_transaction.htm.md)**  
  Create one or more billing schedules for a specified billing transaction ID.
- **[Create Standalone Billing Schedules Action](./actions_obj_create_billing_schedules_from_transaction.htm.md)**  
  Creates billing schedules for internal or external transaction records by calling the Create Standalone Billing Schedules API.
- **[Extend Invoice Due Date Action](./actions_obj_blng_svc_inv_extend_due_date.htm.md)**  
  Update the due date on an invoice to accommodate payment extensions or resolve billing disputes.
- **[Generate Account Statement](./actions_obj_generate_statement_of_account.htm.md)**  
  Generates a comprehensive account statement for a specified account with transaction history and balance information.
- **[Generate Invoice Documents Action](./actions_obj_generate_batch_invoice_documents.htm.md)**  
  Asynchronously generate PDF documents for the invoices associated with an invoice batch run record that are in the `Draft` or `Posted` status.
- **[Issue Credit Memo Action](./actions_obj_blng_dspt_issue_credit_memo.htm.md)**  
  Issue credit memos for disputed invoices to resolve billing disputes.
- **[Post Draft Credit Memo Action](./actions_obj_post_draft_credit_memo.htm.md)**  
  Post a draft credit memo to a credit memo record for review and approval.
- **[Post Draft Invoice Action](./actions_obj_post_draft_invoice.htm.md)**  
  Update the status of an invoice from `Draft` to `Posted` for a credit memo application.
- **[Post Draft Invoice Batch Run Action](./actions_obj_post_draft_invoice_batch_run.htm.md)**  
  Update the status of a batch of invoices from `Draft` to `Posted` for a credit memo application.
- **[Recover Billing Schedules Action](./actions_obj_recover_billing_schedule.htm.md)**  
  Recover one or more billing schedules in the `Error` or `Processing` status.
- **[Send Dunning Email Action](./actions_obj_blng_send_dunning_email.htm.md)**  
  Run an orchestration that sends dunning process emails for collection plans to recover overdue revenue and notify customers about amounts still due.
- **[Suspend Billing Action](./actions_obj_blng_svc_suspend_billing.htm.md)**  
  Suspend or resume the billing of an account to handle billing disputes.
- **[Update Bill To Contact Action](./actions_obj_blng_svc_update_bill_to_contact.htm.md)**  
  Update the Bill to Contact detail on an invoice to ensure accurate billing communication and routing.
- **[Unapply Credit Action](./actions_obj_run_unapply_credit.htm.md)**  
  Unapply a credit memo or credit memo line from an invoice or invoice line, respectively.
- **[Unapply Payment Action](./actions_obj_unapply_payment.htm.md)**  
  Unapplies a payment that's already been applied to an invoice or invoice line by crediting the amount back to the payment and the invoice or invoice line.
- **[Void Posted Credit Memo Action](./actions_obj_void_posted_credit_memo.htm.md)**  
  Invoke the Void Posted Credit Memo API by providing a credit memo ID.
- **[Write Off Invoices Action](./actions_obj_write_off_invoices.htm.md)**  
  Write off partially paid or unpaid invoices to manage pending debts and to maintain accurate financial records. This action calls the Posted Invoice List Write-Off (POST) API.

#### See Also

- [*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_intro_overview.htm "Actions Developer Guide: Overview - HTML (New Window)")
- [*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/resources_actions_invocable_standard.htm "REST API Developer Guide: Invocable Actions Standard - HTML (New Window)")
