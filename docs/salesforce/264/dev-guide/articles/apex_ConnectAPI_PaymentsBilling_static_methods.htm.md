---
page_id: apex_ConnectAPI_PaymentsBilling_static_methods.htm
title: PaymentsBilling Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_PaymentsBilling_static_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

 

# PaymentsBilling Class

 
 
 
Use the PaymentsBilling class to allocate the balance of a payment to reduce the balance
  of an invoice. Additionally, revert the application of a payment line from an invoice.

  

## Namespace

   
   

ConnectApi

  

 

 

## PaymentsBilling Methods

 These methods are for `PaymentsBilling`. All
  methods are static.

 

- 
**[applyPaymentLine(PaymentLineApplyInput, paymentId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyPaymentLine_1)**  

Allocate the balance of a payment to reduce the balance of an invoice. The response     includes an ID of the payment line invoice that represents the payment balance allocated against     the invoice.

- 
**[applyRefundLine(RefundLineApplyInput, refundId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_applyRefundLine_1)**  

Make a refund transaction against a payment.

- 
**[unapplyPaymentLine(PaymentLineUnapplyInput, paymentId, paymentLineId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_1)**  

Revert the application of a payment line from an invoice, and return the payment and     invoices to their pre-application state. Use this method if you need to correct an input during     the payment application process.

- 
**[unapplyPaymentLine(PaymentLineUnapplyInput, paymentLineId)](./apex_ConnectAPI_PaymentsBilling_static_methods.htm.md#apex_ConnectAPI_PaymentsBilling_unapplyPaymentLine_2)**  

Revert the application of a payment line from an invoice, and return the payment and     invoices to their pre-application state. Use this method if you need to correct an input during     the payment application process.

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

**PaymentLineApplyInput**

: Type: [`ConnectApi.PaymentLineApplyRequest`](./apex_connectapi_input_payment_line_apply.htm.md)

: Input representation of the payment line details.

**paymentId**

: Type: String

: 

ID of the payment record.

#### Return Value

Type: [`ConnectApi.PaymentLineApplyResponse`](./apex_connectapi_output_payment_line_apply_output.htm.md)

#### Usage

Use the Commerce Payments APIs to send your payment and
        refund details to external payment gateways for processing against a customer's bank. See
          [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_resources_payments.htm)
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

**RefundLineApplyInput**

: Type: [`ConnectApi.RefundLineApplyRequest`](./apex_connectapi_input_refund_line_apply.htm.md)

: Input representation of the details of a transaction refund request. This representation
            outlines the properties of a refund, including the refund amount and ID of the payment
            or credit memo record that the refund is applied to.

**refundId**

: Type: String

: ID of the refund record.

#### Return Value

Type: [`ConnectApi.RefundLineApplyResponse`](./apex_connectapi_output_refund_line_apply_output.htm.md)

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

**PaymentLineUnapplyInput**

: Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex_connectapi_input_payment_line_unapply.htm.md)

: Input representation of the payment line details.

**paymentId**

: Type: String

: 

ID of the payment record.

**paymentLineId**

: Type: String

: 

ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex_connectapi_output_payment_line_unapply_output.htm.md)

#### Usage

      

Use the Commerce Payments APIs to send your payment and
        refund details to external payment gateways for processing against a customer's bank. See
          [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_resources_payments.htm)
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

**PaymentLineUnapplyInput**

: Type: [`ConnectApi.PaymentLineUnapplyRequest`](./apex_connectapi_input_payment_line_unapply.htm.md)

          
: Input representation of the payment line details.

**paymentLineId**

: Type: String

: 

ID of the payment line record.

#### Return Value

Type: [`ConnectApi.PaymentLineUnapplyResponse`](./apex_connectapi_output_payment_line_unapply_output.htm.md)

#### Usage

      

Use the Commerce Payments APIs to send your payment and
        refund details to external payment gateways for processing against a customer's bank. See
          [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_resources_payments.htm)
        to check the APIs for payment gateways, payment captures, and payment authorizations.
