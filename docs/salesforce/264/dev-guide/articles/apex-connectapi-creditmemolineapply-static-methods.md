---
page_id: apex-connectapi-creditmemolineapply-static-methods
title: CreditMemoLineApply Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-creditmemolineapply-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_CreditMemoLineApply_static_methods.htm
fetched_at: 2026-11-25
---

# CreditMemoLineApply Class

Manage credit memo line applications by using the CreditMemoLineApply class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## CreditMemoLineApply Methods

These methods are for `CreditMemoLineApply`. All methods are static.

- 

**[applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)](#applycreditmemolinescreditmemolineapplyinput-creditmemolineid)**

Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.

- 

**[unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)](#unapplycreditmemolinescreditmemolineunapplyinput-creditmemolineinvoicelineid)**

Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.

### applyCreditMemoLines(CreditMemoLineApplyInput, creditMemoLineId)

Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.CreditMemoLineAppliedResponse applyCreditMemoLines(ConnectApi.CreditMemoLineApplyInput CreditMemoLineApplyInput, String creditMemoLineId)`

#### Parameters

***CreditMemoLineApplyInput***

Type: [ConnectApi.CreditMemoLineApplyInput](./apex-connectapi-input-credit-memo-line-apply.md)

Input representation of the details of the request to apply a credit memo line to an invoice line.

***creditMemoLineId***

Type: String

ID of the credit memo line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineAppliedResponse](./apex-connectapi-output-credit-memo-line-applied.md)

#### Usage

You need the Credit Memo Operations User permission set to use this method.

### unapplyCreditMemoLines(CreditMemoLineUnapplyInput, creditMemoLineInvoiceLineId)

Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.CreditMemoLineUnappliedResponse unapplyCreditMemoLines(ConnectApi.CreditMemoLineUnapplyInput CreditMemoLineUnapplyInput, String creditMemoLineInvoiceLineId)`

#### Parameters

***CreditMemoLineUnapplyInput***

Type: [ConnectApi.CreditMemoLineUnapplyInput](./apex-connectapi-input-credit-memo-line-unapply.md)

Input representation of the details of the request to unapply a credit memo line from an invoice line.

***creditMemoLineInvoiceLineId***

Type: String

ID of the credit memo line invoice line record.

#### Return Value

Type: [ConnectApi.CreditMemoLineUnappliedResponse](./apex-connectapi-output-credit-memo-line-unapplied.md)

#### Usage

You need the Credit Memo Operations User permission set to use this method.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-creditmemolineapply-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
