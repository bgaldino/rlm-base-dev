---
page_id: apex_ConnectAPI_PaymentsBilling_static_methods.htm
title: PaymentsBilling Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_PaymentsBilling_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# PaymentsBilling Class

Use the PaymentsBilling class to allocate the balance of a payment to reduce the balance
of an invoice. Additionally, revert the application of a payment line from an invoice.

## Namespace

ConnectApi

## PaymentsBilling Methods

These methods are for `PaymentsBilling`. All
methods are static.

- **[applyPaymentLine(PaymentLineApplyInput, paymentId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyPaymentLine_1)**  
  Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice that represents the payment balance allocated against the invoice.
- **[applyRefundLine(RefundLineApplyInput, refundId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyRefundLine_1)**  
  Make a refund transaction against a payment.
- **[unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_1)**  
  Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.
- **[unapplyPaymentLine(PaymentLineUnapplyInput, paymentLineId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_2)**  
  Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. Use this method if you need to correct an input during the payment application process.

### applyPaymentLine(PaymentLineApplyInput, paymentId)

Allocate the balance of a payment to reduce the balance of an invoice. The response
includes an ID of the payment line invoice that represents the payment balance allocated against
the invoice.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineApplyResponse applyPaymentLine(ConnectApi.PaymentLineApplyRequest PaymentLineApplyInput, String paymentId)`

#### Parameters

PaymentLineApplyInput
:   Type: [`ConnectApi.PaymentLineApplyRequest`](./apex_connectapi_input_payment_line_apply.htm.md "Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields, such as associated account and effective date.")
:   Input representation of the payment line details.

paymentId
:   Type: String
:   ID of the payment record.

#### Return Value

Type: [`ConnectApi.PaymentLineApplyResponse`](./apex_connectapi_output_payment_line_apply_output.htm.md "Output representation of the details of the applied payment line. The details include the ID of the payment record and date when the payment line was applied.")

#### Usage

Use the Commerce Payments APIs to send your payment and
refund details to external payment gateways for processing against a customer's bank. See
[Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)")
to check the APIs for payment gateways, payment captures, and payment authorizations.

### applyRefundLine(RefundLineApplyInput, refundId)

Make a refund transaction against a payment.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RefundLineApplyResponse applyRefundLine(ConnectApi.RefundLineApplyRequest RefundLineApplyInput, String refundId)`

#### Parameters

RefundLineApplyInput
:   Type: [`ConnectApi.RefundLineApplyRequest`](./apex_connectapi_input_refund_line_apply.htm.md "Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.")
:   Input representation of the details of a transaction refund request. This representation
    outlines the properties of a refund, including the refund amount and ID of the payment
    or credit memo record that the refund is applied to.

refundId
:   Type: String
:   ID of the refund record.

#### Return Value

Type: [`ConnectApi.RefundLineApplyResponse`](./apex_connectapi_output_refund_line_apply_output.htm.md "Output representation of the details of an applied refund. This representation includes the properties of a refund line, such as the date when the refund is applied against a payment and ID of the refund line record.")

### unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)

Revert the application of a payment line from an invoice, and return the payment and
invoices to their pre-application state. Use this method if you need to correct an input during
the payment application process.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineUnapplyResponse unapplyPaymentLine(ConnectApi.PaymentLineUnapplyRequest PaymentLineUnapplyInput, String paymentId, String paymentLineId)`

#### Parameters

PaymentLineUnapplyInput
:   Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex_connectapi_input_payment_line_unapply.htm.md "Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application.")
:   Input representation of the payment line details.

paymentId
:   Type: String
:   ID of the payment record.

paymentLineId
:   Type: String
:   ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex_connectapi_output_payment_line_unapply_output.htm.md "Output representation of the details of the reversed payment line application. The details include the ID of the payment line record and date when the payment line application was reversed.")

#### Usage

Use the Commerce Payments APIs to send your payment and
refund details to external payment gateways for processing against a customer's bank. See
[Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)")
to check the APIs for payment gateways, payment captures, and payment authorizations.

### unapplyPaymentLine(PaymentLineUnapplyInput, paymentLineId)

Revert the application of a payment line from an invoice, and return the payment and
invoices to their pre-application state. Use this method if you need to correct an input during
the payment application process.

#### API Version

64.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.PaymentLineUnapplyResponse unapplyPaymentLine(ConnectApi.PaymentLineUnapplyRequest PaymentLineUnapplyInput, String paymentLineId)`

#### Parameters

PaymentLineUnapplyInput
:   Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex_connectapi_input_payment_line_unapply.htm.md "Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application.")
:   Input representation of the payment line details.

paymentLineId
:   Type: String
:   ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex_connectapi_output_payment_line_unapply_output.htm.md "Output representation of the details of the reversed payment line application. The details include the ID of the payment line record and date when the payment line application was reversed.")

#### Usage

Use the Commerce Payments APIs to send your payment and
refund details to external payment gateways for processing against a customer's bank. See
[Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)")
to check the APIs for payment gateways, payment captures, and payment authorizations.
