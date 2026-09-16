---
page_id: billing_apex_reference.htm
title: Billing Apex Reference
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_apex_reference.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Apex Reference

Billing provides the `ConnectApi`
      namespace (also called Connect in Apex) that contains classes for accessing the same
      capabilities that are available in the Billing Business APIs. Additionally, you can use other
      built-in Apex classes and interfaces grouped by namespace.

    

This table lists the available Billing Apex methods with the associated Connect REST API.

    

        
        
        
          
            

            

          

        

        
          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

        

      
| Apex Method | Connect REST API |
| --- | --- |
| [`convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_convertNegativeInvoiceLines) | [`Negative Invoice Lines to Credit Conversion (POST)`](./connect_resources_convert_negative_invoice_lines_to_credit.htm.md) |
| [`generateInvoices(inputRequest)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_generateInvoices_1) | [`Invoices By Using Billing Schedules (POST)`](./connect_resources_create_invoices_from_billing_schedules.htm.md) |
| [`recoverBillingSchedules(inputRequest)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_recoverBillingSchedules_1) | [`Billing Schedule Recovery List (POST)`](./connect_resources_recover_billing_schedules.htm.md) |
| [`creditInvoice(CreditInvoiceInput, invoiceId)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_creditInvoice_1) | [`Credit Memo Create and Apply (POST)`](./connect_resources_create_and_apply_a_credit_memo.htm.md) |
| [`applyCreditMemos(CreditMemoApplyInput, creditMemoId)`](./apex_ConnectAPI_CreditMemoApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoApply_applyCreditMemos_1) | [`Credit Memo Apply List(POST)`](./connect_resources_credit_memo_apply.htm.md) |
| [`unapplyCreditMemos(CreditMemoUnapplyInput, creditMemoInvApplicationId)`](./apex_ConnectAPI_CreditMemoApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoApply_unapplyCreditMemos_1) | [`Credit Memo Unapply (POST)`](./connect_resources_credit_memo_invoice_application_unapply.htm.md) |
| [`applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)`](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_applyCreditMemoLines_1) | [`Credit Memo Line Apply (POST)`](./connect_resources_credit_memo_line_level_apply.htm.md) |
| [`unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)`](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_unapplyCreditMemoLines_1) | [`Credit Memo Line Unapply (POST)`](./connect_resources_credit_memo_line_level_unapply.htm.md) |
| [`triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)`](./apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm.md#apex_ConnectAPI_BatchInvoiceApplication_triggerInvoiceBatchDraftToPosted_1) | [`Invoices Batch Draft to Posted Status (POST)`](./connect_resources_batch_draft_invoices_to_posted.htm.md) |
| [`postDraftInvoices(inputRequest)`](./apex_ConnectAPI_HarmonizeBilling_static_methods.htm.md#apex_ConnectAPI_HarmonizeBilling_postDraftInvoices_1) | [`Invoice Draft to Posted Status (POST)`](./connect_resources_draft_to_posted_invoice.htm.md) |
| [`createCreditMemos(CreditMemoInputRequest)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_createCreditMemos_1) | [`Credit Memo Create and Apply (POST)`](./connect_resources_create_and_apply_a_credit_memo.htm.md) |
| [`voidPostedInvoice(invoiceId)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_voidPostedInvoice_1) | [`Posted Invoice Voidance (POST)`](./connect_resources_void_a_posted_invoice.htm.md) |
| [`calculateTax(calculateTax)`](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_ConnectAPI_TaxPlatform_static_methods.htm) | [`Tax Calculation (POST)`](./connect_resources_calculate_taxes.htm.md) |
| [`applyPaymentLine(PaymentLineApplyInput, paymentId)`](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyPaymentLine_1) | [`Payment Line Apply (POST)`](./connect_resources_payment_line_apply.htm.md) |
| [`unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)`](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_1) | [`Payment Line Unapply (POST)`](./connect_resources_payment_line_unapply.htm.md) |
| [`applyRefundLine(RefundLineApplyInput, refundId)`](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyRefundLine_1) | [`Refund Line Apply (POST)`](./connect_resources_apply_refund_to_payment.htm.md) |
| [`reconcileSequences(sequenceGapReconciliationInputRepresentation)`](./apex_ConnectAPI_SequencingWithoutAura_static_methods.htm.md#apex_ConnectAPI_SequencingWithoutAura_reconcileSequences_1) | [`Sequence Gap Reconciliation (POST)`](./connect_resources_sequences_gap_reconciliation.htm.md) |
| [`sequenceAssignment(sequencesAssignmentInputRepresentation)`](./apex_ConnectAPI_SequencingWithoutAura_static_methods.htm.md#apex_ConnectAPI_SequencingWithoutAura_sequenceAssignment_1) | [`Sequence Assignment (POST)`](./connect_resources_sequences_assignment.htm.md) |
| [`voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)`](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_voidPostedCreditMemo_1) | [`Void Posted Credit Memo (POST)`](./connect_resources_void_posted_credit_memo.htm.md) |

    

For more information about Apex classes that are available for Commerce Payments, see [CommercePayments Namespace](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_namespace_commercepayments.htm).

  

- 
**[ConnectApi Namespace](./billing_connect_api_namespace.htm.md)**  

The `ConnectApi` namespace (also called Connect in         Apex) provides classes to manage credit applications and billing scenarios.

- 
**[InvoiceWriteOff Namespace](./apex_namespace_InvoiceWriteOff.htm.md)**  

Create credit memos with the total charge amount on the invoice as the write-off amount     and close the invoice.

- 
**[IssueCreditMemo Namespace](./apex_namespace_IssueCreditMemo.htm.md)**  

Issue credit memos from disputed invoices. Use this namespace to create and apply credit     memos against invoices or invoice lines based on dispute adjustments.

- 
**[RulesAppln Namespace](./apex_namespace_RulesAppln.htm.md)**  

Apply payments and credits to posted invoices by adhering to the specified rules.

- 
**[TaxEngineAdapter Interface](./billing_tax_engine_adapter_interface_for_standard_tax.htm.md)**  

Retrieves and evaluates the details from a tax engine to define tax         details.
