---
page_id: apex_ConnectAPI_CreditMemoLineApply_static_methods.htm
title: CreditMemoLineApply Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoLineApply_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# CreditMemoLineApply Class

Manage credit memo line applications by using the CreditMemoLineApply class.

## Namespace

ConnectApi

## CreditMemoLineApply Methods

These methods are for `CreditMemoLineApply`. All
methods are static.

- **[applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_applyCreditMemoLines_1)**  
  Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.
- **[unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_unapplyCreditMemoLines_1)**  
  Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.

### applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)

Adjust or correct already issued invoices by applying an existing credit memo line to an
invoice line.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.CreditMemoLineAppliedResponse applyCreditMemoLines(ConnectApi.CreditMemoLineApplyInput CreditMemoLineApplyInput, String creditMemoLineId)`

#### Parameters

CreditMemoLineApplyInput
:   Type: [ConnectApi.CreditMemoLineApplyInput](./apex_connectapi_input_credit_memo_line_apply.htm.md "Input representation of the details of the request to apply a credit memo line to an invoice line.")
:   Input representation of the details of the request to apply a credit memo line to an invoice
    line.

creditMemoLineId
:   Type: String
:   ID of the credit memo line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineAppliedResponse](./apex_connectapi_output_credit_memo_line_applied.htm.md "Output representation of the list of applied credit memo line results.")

#### Usage

You need the Credit Memo Operations User permission set to use this method.

### unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)

Unapply a credit memo line from an invoice line and return the invoice line and the
credit memo line to their pre-application states.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.CreditMemoLineUnappliedResponse unapplyCreditMemoLines(ConnectApi.CreditMemoLineUnapplyInput CreditMemoLineUnapplyInput, String creditMemoLineInvoiceLineId)`

#### Parameters

CreditMemoLineUnapplyInput
:   Type: [ConnectApi.CreditMemoLineUnapplyInput](./apex_connectapi_input_credit_memo_line_unapply.htm.md "Input representation of the details of the request to unapply a credit memo line from an invoice line.")
:   Input representation of the details of the request to unapply a credit memo line from an invoice
    line.

creditMemoLineInvoiceLineId
:   Type: String
:   ID of the credit memo line invoice line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineUnappliedResponse](./apex_connectapi_output_credit_memo_line_unapplied.htm.md "Output representation of the details of the credit memo line invoice line record with the status of the request.")

#### Usage

You need the Credit Memo Operations User permission set to use this method.
