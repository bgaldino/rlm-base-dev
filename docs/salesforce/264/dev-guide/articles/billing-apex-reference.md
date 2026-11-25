---
page_id: billing-apex-reference
title: Billing Apex Reference
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-apex-reference.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_apex_reference.htm
fetched_at: 2026-11-25
---

# Billing Apex Reference

Billing provides the `ConnectApi` namespace (also called Connect in Apex) that contains classes for accessing the same capabilities that are available in the Billing Business APIs. Additionally, you can use other built-in Apex classes and interfaces grouped by namespace.

This table lists the available Billing Apex methods with the associated Connect REST API.

| Apex Method | Connect REST API |
| --- | --- |
| [`convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_convertNegativeInvoiceLines) | [`Negative Invoice Lines to Credit Conversion (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_convert_negative_invoice_lines_to_credit.htm) |
| [`generateInvoices(inputRequest)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_generateInvoices_1) | [`Invoices By Using Billing Schedules (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_invoices_from_billing_schedules.htm) |
| [`recoverBillingSchedules(inputRequest)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_recoverBillingSchedules_1) | [`Billing Schedule Recovery List (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_recover_billing_schedules.htm) |
| [`creditInvoice(CreditInvoiceInput, invoiceId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_creditInvoice_1) | [`Credit Memo Create and Apply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_and_apply_a_credit_memo.htm) |
| [`applyCreditMemos(CreditMemoApplyInput, creditMemoId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoApply_static_methods.htm#apex_ConnectAPI_CreditMemoApply_applyCreditMemos_1) | [`Credit Memo Apply List(POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_apply.htm) |
| [`unapplyCreditMemos(CreditMemoUnapplyInput, creditMemoInvApplicationId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoApply_static_methods.htm#apex_ConnectAPI_CreditMemoApply_unapplyCreditMemos_1) | [`Credit Memo Unapply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_invoice_application_unapply.htm) |
| [`applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoLineApply_static_methods.htm#apex_ConnectAPI_CreditMemoLineApply_applyCreditMemoLines_1) | [`Credit Memo Line Apply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_line_level_apply.htm) |
| [`unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoLineApply_static_methods.htm#apex_ConnectAPI_CreditMemoLineApply_unapplyCreditMemoLines_1) | [`Credit Memo Line Unapply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_line_level_unapply.htm) |
| [`triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm#apex_ConnectAPI_BatchInvoiceApplication_triggerInvoiceBatchDraftToPosted_1) | [`Invoices Batch Draft to Posted Status (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_batch_draft_invoices_to_posted.htm) |
| [`postDraftInvoices(inputRequest)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_HarmonizeBilling_static_methods.htm#apex_ConnectAPI_HarmonizeBilling_postDraftInvoices_1) | [`Invoice Draft to Posted Status (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_draft_to_posted_invoice.htm) |
| [`createCreditMemos(CreditMemoInputRequest)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_createCreditMemos_1) | [`Credit Memo Create and Apply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_and_apply_a_credit_memo.htm) |
| [`voidPostedInvoice(invoiceId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_voidPostedInvoice_1) | [`Posted Invoice Voidance (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_void_a_posted_invoice.htm) |
| [`calculateTax(calculateTax)`](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_ConnectAPI_TaxPlatform_static_methods.htm) | [`Tax Calculation (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_calculate_taxes.htm) |
| [`applyPaymentLine(PaymentLineApplyInput, paymentId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_PaymentsBilling_static_methods.htm#apex_ConnectAPI_PaymentsBilling_applyPaymentLine_1) | [`Payment Line Apply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_payment_line_apply.htm) |
| [`unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_PaymentsBilling_static_methods.htm#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_1) | [`Payment Line Unapply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_payment_line_unapply.htm) |
| [`applyRefundLine(RefundLineApplyInput, refundId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_PaymentsBilling_static_methods.htm#apex_ConnectAPI_PaymentsBilling_applyRefundLine_1) | [`Refund Line Apply (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_apply_refund_to_payment.htm) |
| [`reconcileSequences(sequenceGapReconciliationInputRepresentation)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_SequencingWithoutAura_static_methods.htm#apex_ConnectAPI_SequencingWithoutAura_reconcileSequences_1) | [`Sequence Gap Reconciliation (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_sequences_gap_reconciliation.htm) |
| [`sequenceAssignment(sequencesAssignmentInputRepresentation)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_SequencingWithoutAura_static_methods.htm#apex_ConnectAPI_SequencingWithoutAura_sequenceAssignment_1) | [`Sequence Assignment (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_sequences_assignment.htm) |
| [`voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm#apex_ConnectAPI_Billing_voidPostedCreditMemo_1) | [`Void Posted Credit Memo (POST)`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_void_posted_credit_memo.htm) |

For more information about Apex classes that are available for Commerce Payments, see [CommercePayments Namespace](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_namespace_commercepayments.htm).

- 

**[ConnectApi Namespace](./billing-connect-api-namespace.md)**

The `ConnectApi` namespace (also called Connect in Apex) provides classes to manage credit applications and billing scenarios.

- 

**[InvoiceWriteOff Namespace](./apex-namespace-invoicewriteoff.md)**

Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.

- 

**[IssueCreditMemo Namespace](./apex-namespace-issuecreditmemo.md)**

Issue credit memos from disputed invoices. Use this namespace to create and apply credit memos against invoices or invoice lines based on dispute adjustments.

- 

**[RulesAppln Namespace](./apex-namespace-rulesappln.md)**

Apply payments and credits to posted invoices by adhering to the specified rules.

- 

**[TaxEngineAdapter Interface](./billing-tax-engine-adapter-interface-for-standard-tax.md)**

Retrieves and evaluates the details from a tax engine to define tax details.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-apex-reference.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
