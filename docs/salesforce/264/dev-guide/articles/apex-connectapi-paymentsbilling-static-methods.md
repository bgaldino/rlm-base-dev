---
page_id: apex-connectapi-paymentsbilling-static-methods
title: PaymentsBilling Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-paymentsbilling-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_PaymentsBilling_static_methods.htm
fetched_at: 2026-11-25
---

# PaymentsBilling Class

Use the PaymentsBilling class to allocate the balance of a payment to reduce the balance of an invoice. Additionally, revert the application of a payment line from an invoice.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## PaymentsBilling Methods

These methods are for `PaymentsBilling`. All methods are static.

- 

**[applyPaymentLine(PaymentLineApplyInput, paymentId)](#applypaymentlinepaymentlineapplyinput-paymentid)**

Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice that represents the payment balance allocated against the invoice.

- 

**[applyRefundLine(RefundLineApplyInput, refundId)](#applyrefundlinerefundlineapplyinput-refundid)**

Make a refund transaction against a payment.

- 

**[unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)](#unapplypaymentlinepaymentlineunapplyinput-paymentid-paymentlineid)**

Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.

- 

**[unapplyPaymentLine(PaymentLineUnapplyInput, paymentLineId)](#unapplypaymentlinepaymentlineunapplyinput-paymentlineid)**

Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.

### applyPaymentLine(PaymentLineApplyInput, paymentId)

Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice that represents the payment balance allocated against the invoice.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineApplyResponse applyPaymentLine(ConnectApi.PaymentLineApplyRequest PaymentLineApplyInput, String paymentId)`

#### Parameters

***PaymentLineApplyInput***

Type: [`ConnectApi.PaymentLineApplyRequest`](./apex-connectapi-input-payment-line-apply.md)

Input representation of the payment line details.

***paymentId***

Type: String

ID of the payment record.

#### Return Value

Type: [`ConnectApi.PaymentLineApplyResponse`](./apex-connectapi-output-payment-line-apply-output.md)

#### Usage

Use the Commerce Payments APIs to send your payment and refund details to external payment gateways for processing against a customer’s bank. See [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_resources_payments.htm) to check the APIs for payment gateways, payment captures, and payment authorizations.

### applyRefundLine(RefundLineApplyInput, refundId)

Make a refund transaction against a payment.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RefundLineApplyResponse applyRefundLine(ConnectApi.RefundLineApplyRequest RefundLineApplyInput, String refundId)`

#### Parameters

***RefundLineApplyInput***

Type: [`ConnectApi.RefundLineApplyRequest`](./apex-connectapi-input-refund-line-apply.md)

Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.

***refundId***

Type: String

ID of the refund record.

#### Return Value

Type: [`ConnectApi.RefundLineApplyResponse`](./apex-connectapi-output-refund-line-apply-output.md)

### unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)

Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineUnapplyResponse unapplyPaymentLine(ConnectApi.PaymentLineUnapplyRequest PaymentLineUnapplyInput, String paymentId, String paymentLineId)`

#### Parameters

***PaymentLineUnapplyInput***

Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex-connectapi-input-payment-line-unapply.md)

Input representation of the payment line details.

***paymentId***

Type: String

ID of the payment record.

***paymentLineId***

Type: String

ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex-connectapi-output-payment-line-unapply-output.md)

#### Usage

Use the Commerce Payments APIs to send your payment and refund details to external payment gateways for processing against a customer’s bank. See [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_resources_payments.htm) to check the APIs for payment gateways, payment captures, and payment authorizations.

### unapplyPaymentLine(PaymentLineUnapplyInput, paymentLineId)

Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineUnapplyResponse unapplyPaymentLine(ConnectApi.PaymentLineUnapplyRequest PaymentLineUnapplyInput, String paymentLineId)`

#### Parameters

***PaymentLineUnapplyInput***

Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex-connectapi-input-payment-line-unapply.md)

Input representation of the payment line details.

***paymentLineId***

Type: String

ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex-connectapi-output-payment-line-unapply-output.md)

#### Usage

Use the Commerce Payments APIs to send your payment and refund details to external payment gateways for processing against a customer’s bank. See [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_resources_payments.htm) to check the APIs for payment gateways, payment captures, and payment authorizations.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-paymentsbilling-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
