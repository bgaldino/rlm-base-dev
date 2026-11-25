---
page_id: billing-invocable-actions-parent
title: Billing Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-invocable-actions-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_invocable_actions_parent.htm
fetched_at: 2026-11-25
---

# Billing Standard Invocable Actions

Use standard invocable actions to automate processes such as credit application, billing schedules creation, and invoice management.

## Commerce Payments Invocable Actions

This table provides a list of the invocable actions of Commerce Payments, which can be used for Billing.

| Resource | Description |
| --- | --- |
| [`/services/data/v68.0/actions/standard/applyPayment`](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_obj_payment_apply.htm) (POST) | Apply a payment record to an invoice header by creating a PaymentLineInvoice record with `Applied` type. |
| [`/services/data/v68.0/actions/standard/paymentSale`](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_obj_payment_sale.htm) (POST) | Capture a payment without any prior authorization, and create a payment record. |

Billing provides these invocable actions.

- 

**[Create Collection Plan Action](./actions-obj-create-collection-plan.md)**

Create one or more collection plans, each with its optional nested collection plan items.

- 

**[Apply Credit Action](./actions-obj-run-apply-credit.md)**

Apply a credit memo or credit memo line to an invoice or invoice line, respectively.

- 

**[Apply Payments and Credits by Rules Action](./actions-obj-apply-rules.md)**

Apply payments and credits to posted invoices by adhering to the specified rules.

- 

**[Automate Refund Action](./actions-obj-automate-refund.md)**

Initiate refund orchestration for a credit memo generated from a subscription cancellation or negative amendment.

- 

**[Process Refund Credit Memo Action](./actions-obj-process-refund-credit-memo.md)**

Initiates a refund against a posted credit memo. This action locks the credit memo, calls the Commerce Refund API, and returns the refund and application record IDs.

- 

**[Create Billing Schedules From Billing Transaction Action](./actions-obj-create-billing-schedule-from-billing-transaction.md)**

Create one or more billing schedules for a specified billing transaction ID.

- 

**[Create Standalone Billing Schedules Action](./actions-obj-create-billing-schedules-from-transaction.md)**

Creates billing schedules for internal or external transaction records by calling the Create Standalone Billing Schedules API.

- 

**[Extend Invoice Due Date Action](./actions-obj-blng-svc-inv-extend-due-date.md)**

Update the due date on an invoice to accommodate payment extensions or resolve billing disputes.

- 

**[Generate Account Statement](./actions-obj-generate-statement-of-account.md)**

Generates a comprehensive account statement for a specified account with transaction history and balance information.

- 

**[Generate Invoice Documents Action](./actions-obj-generate-batch-invoice-documents.md)**

Asynchronously generate PDF documents for the invoices associated with an invoice batch run record that are in the `Draft` or `Posted` status.

- 

**[Issue Credit Memo Action](./actions-obj-blng-dspt-issue-credit-memo.md)**

Issue credit memos for disputed invoices to resolve billing disputes.

- 

**[Post Draft Credit Memo Action](./actions-obj-post-draft-credit-memo.md)**

Post a draft credit memo to a credit memo record for review and approval.

- 

**[Post Draft Invoice Action](./actions-obj-post-draft-invoice.md)**

Update the status of an invoice from `Draft` to `Posted` for a credit memo application.

- 

**[Post Draft Invoice Batch Run Action](./actions-obj-post-draft-invoice-batch-run.md)**

Update the status of a batch of invoices from `Draft` to `Posted` for a credit memo application.

- 

**[Recover Billing Schedules Action](./actions-obj-recover-billing-schedule.md)**

Recover one or more billing schedules in the `Error` or `Processing` status.

- 

**[Send Dunning Email Action](./actions-obj-blng-send-dunning-email.md)**

Run an orchestration that sends dunning process emails for collection plans to recover overdue revenue and notify customers about amounts still due.

- 

**[Suspend Billing Action](./actions-obj-blng-svc-suspend-billing.md)**

Suspend or resume the billing of an account to handle billing disputes.

- 

**[Update Bill To Contact Action](./actions-obj-blng-svc-update-bill-to-contact.md)**

Update the Bill to Contact detail on an invoice to ensure accurate billing communication and routing.

- 

**[Unapply Credit Action](./actions-obj-run-unapply-credit.md)**

Unapply a credit memo or credit memo line from an invoice or invoice line, respectively.

- 

**[Unapply Payment Action](./actions-obj-unapply-payment.md)**

Unapplies a payment that’s already been applied to an invoice or invoice line by crediting the amount back to the payment and the invoice or invoice line.

- 

**[Void Posted Credit Memo Action](./actions-obj-void-posted-credit-memo.md)**

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

- 

**[Write Off Invoices Action](./actions-obj-write-off-invoices.md)**

Write off partially paid or unpaid invoices to manage pending debts and to maintain accurate financial records. This action calls the Posted Invoice List Write-Off (POST) API.

**See Also**

- [*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_intro_overview.htm)

- [*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_actions_invocable_standard.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-invocable-actions-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
