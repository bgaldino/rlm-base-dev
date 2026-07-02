---
page_id: apex_ConnectAPI_CreditMemoApply_static_methods.htm
title: CreditMemoApply Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoApply_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# CreditMemoApply Class

Manage credit memo applications by using the CreditMemoApply class.

## Namespace

ConnectApi

## CreditMemoApply Methods

These methods are for `CreditMemoApply`. All
methods are static.

- **[applyCreditMemos(CreditMemoApplyInput, creditMemoId)](./apex_ConnectAPI_CreditMemoApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoApply_applyCreditMemos_1)**  
  Adjust or correct already issued invoices by applying an existing credit memo to an invoice.
- **[unapplyCreditMemos(CreditMemoUnapplyInput, creditMemoInvApplicationId)](./apex_ConnectAPI_CreditMemoApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoApply_unapplyCreditMemos_1)**  
  Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states.

### applyCreditMemos(CreditMemoApplyInput, creditMemoId)

Adjust or correct already issued invoices by applying an existing credit memo to an
invoice.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.ApplyCreditResults applyCreditMemos(ConnectApi.CreditMemoApplyInputRequest CreditMemoApplyInput, String creditMemoId)`

#### Parameters

CreditMemoApplyInput
:   Type: [ConnectApi.CreditMemoApplyInputRequest](./apex_connectapi_input_credit_memo_apply.htm.md "Input representation of the request to apply a credit memo to an invoice.")
:   Input representation of the request to apply a credit memo to an invoice.

creditMemoId
:   Type: String
:   ID of the credit memo record.

#### Return Value

Type: [ConnectApi.ApplyCreditResults](./apex_connectapi_output_credit_memo_apply_list_output.htm.md "Output representation of the list of applied credit memo results.")

#### Usage

Specify the credit memo ID and the amounts to be applied, with the total of all applied
amounts not exceeding the credit memo's balance.

The credit amount for each invoice can’t surpass the original charge or adjustment amount,
and the overall credit amount must not exceed the invoice's outstanding balance. The
exceptions include any taxes calculated by an external service.

For example, your organization sold 10 tablets at US$500 each, totaling $5000, to a vendor
who later reported that 6 tablets were defective. Using this method, your accounts
receivable team creates a $3000 credit memo and applies this credit to the original
invoice.

### unapplyCreditMemos(CreditMemoUnapplyInput, creditMemoInvApplicationId)

Unapply a credit memo from an invoice and return the invoice and the credit memo to their
pre-application states.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.UnapplyCreditResult unapplyCreditMemos(ConnectApi.CreditMemoUnapplyInputRequest CreditMemoUnapplyInput, String creditMemoInvApplicationId)`

#### Parameters

CreditMemoUnapplyInput
:   Type: [ConnectApi.CreditMemoUnapplyInputRequest](./apex_connectapi_input_credit_memo_unapply.htm.md "Input representation of the request to unapply a credit memo from an invoice.")
:   Input representation of the request to unapply a credit memo from an invoice.

creditMemoInvApplicationId
:   Type: String
:   ID of the credit memo invoice application.

#### Return Value

Type: [ConnectApi.UnapplyCreditResult](./apex_connectapi_output_credit_memo_unapply_output.htm.md "Output representation of the details of the credit memo invoice application record with the status of the request.")

#### Usage

Use this method if an error occurred when a credit is issued. For example, if an incorrect
credit memo is applied to an invoice, or if a credit memo is created for an incorrect
amount, use this method to unapply the credit memo.
