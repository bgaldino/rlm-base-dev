---
page_id: apex_ConnectAPI_CreditMemoLineApply_static_methods.htm
title: CreditMemoLineApply Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_CreditMemoLineApply_static_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

 

# CreditMemoLineApply Class

 
 
 
Manage credit memo line applications by using the CreditMemoLineApply class.

  

## Namespace

   
   

ConnectApi

  

 

 

## CreditMemoLineApply Methods

 These methods are for `CreditMemoLineApply`. All
  methods are static.

 

- 
**[applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_applyCreditMemoLines_1)**  

Adjust or correct already issued invoices by applying an existing credit memo line to an     invoice line.

- 
**[unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)](./apex_ConnectAPI_CreditMemoLineApply_static_methods.htm.md#apex_ConnectAPI_CreditMemoLineApply_unapplyCreditMemoLines_1)**  

Unapply a credit memo line from an invoice line and return the invoice line and the     credit memo line to their pre-application states.

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

**CreditMemoLineApplyInput**

: Type: [ConnectApi.CreditMemoLineApplyInput](./apex_connectapi_input_credit_memo_line_apply.htm.md)

: Input representation of the details of the request to apply a credit memo line to an invoice
            line.

**creditMemoLineId**

: Type: String

: ID of the credit memo line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineAppliedResponse](./apex_connectapi_output_credit_memo_line_applied.htm.md)

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

**CreditMemoLineUnapplyInput**

: Type: [ConnectApi.CreditMemoLineUnapplyInput](./apex_connectapi_input_credit_memo_line_unapply.htm.md)

: Input representation of the details of the request to unapply a credit memo line from an invoice
            line.

**creditMemoLineInvoiceLineId**

: Type: String

: ID of the credit memo line invoice line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineUnappliedResponse](./apex_connectapi_output_credit_memo_line_unapplied.htm.md)

#### Usage

You need the Credit Memo Operations User permission set to use this method.
