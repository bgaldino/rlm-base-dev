---
page_id: apex_ConnectAPI_Billing_static_methods.htm
title: Billing Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_Billing_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# Billing Class

Manage billing scenarios by using the Billing class. You can convert negative invoice
lines, create and apply a credit memo to an invoice, generate invoices, and recover billing
schedules.

## Namespace

ConnectApi

## Billing Methods

These methods are for `Billing`. All methods are
static.

- **[convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_convertNegativeInvoiceLines)**  
  Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.
- **[createCreditMemos(CreditMemoInputRequest)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_createCreditMemos_1)**  
  Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.
- **[creditInvoice(CreditInvoiceInput, invoiceId)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_creditInvoice_1)**  
  Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.
- **[generateInvoices(inputRequest)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_generateInvoices_1)**  
  Create an invoice from a billing schedule.
- **[recoverBillingSchedules(inputRequest)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_recoverBillingSchedules_1)**  
  Recover the latest generated invoice associated with the billing schedules in the Error or Processing status.
- **[voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_voidPostedCreditMemo_1)**  
  Invoke the Void Posted Credit Memo API by providing a credit memo ID.
- **[voidPostedInvoice(invoiceId)](./apex_ConnectAPI_Billing_static_methods.htm.md#apex_ConnectAPI_Billing_voidPostedInvoice_1)**  
  Void a posted invoice to rebill the customer, if necessary.

### convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)

Convert a list of invoice lines with a negative amount into a posted credit memo. This
conversion is applicable for a single invoice at a time.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.ConvertNegativeInvoiceLinesResult
convertNegativeInvoiceLines(ConnectApi.ConvertNegativeInvoiceLinesInputRequest
ConvertNegativeInvoiceLinesInput, String invoiceId)`

```
ConnectApi.Billing, convertNegativeInvoiceLines, [ConnectApi.ConvertNegativeInvoiceLinesInputRequest, String], ConnectApi.ConvertNegativeInvoiceLinesResult
```

#### Parameters

ConvertNegativeInvoiceLinesInput
:   Type: [ConnectApi.ConvertNegativeInvoiceLinesInputRequest](./apex_connectapi_input_convert_negative_invoice_lines.htm.md "Input representation of the request details to convert a negative invoice line into a credit.")
:   Input parameters to convert a negative invoice line to a credit.

invoiceId
:   Type: String
:   ID of the invoice whose negative invoice lines must be converted.

#### Return Value

Type: [ConnectApi.ConvertNegativeInvoiceLinesResult](./apex_connectapi_output_convert_negative_invoice_lines_output.htm.md "Output representation of the details of the credit memo along with the status of the request.")

#### Usage

You need the Credit Memo Operations User permission set to use this method.

Keep these considerations in mind when you use this method.

- All invoice lines must be related to the same invoice.
- The invoice line must have a negative amount.
- The invoice line must not be a previously converted credit memo.
- The invoice must have the `Posted` status.
- The invoice must not have any active settlements such as credit applications.

### createCreditMemos(CreditMemoInputRequest)

Create a credit memo without applying it to an invoice. You can credit the invoice at a
later date.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation createCreditMemos(ConnectApi.StandaloneCreditMemoInputRequest CreditMemoInputRequest)`

#### Parameters

CreditMemoInputRequest
:   Type: [`ConnectApi.StandaloneCreditMemoInputRequest`](./apex_connectapi_input_standalone_credit_memo.htm.md "Input representation of the details required to create a standalone credit memo.")
:   Input representation of the details required to create a standalone credit memo.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex_connectapi_output_revenue_async.htm.md "Output representation of the result of the API request with the request identifier.")

#### Usage

You need the Credit Memo Operations User permission set to use this
method.

Specify the credit memo header information, charge parameters, adjustment
parameters, and tax parameters. A credit memo requires at least one credit memo line. The
credit memo line can be a charge or an adjustment.

Specify the credit memo lines that
you want as lists of charges and adjustments. Each credit memo line must be related to a
product.

### creditInvoice(CreditInvoiceInput, invoiceId)

Create a credit memo and apply it to an invoice. The credit memo can fully or partially
credit the invoice.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncLineLevelOutputResponse creditInvoice(ConnectApi.CreditInvoiceInputRequest CreditInvoiceInput, String invoiceId)`

```
ConnectApi.Billing, creditInvoice, [ConnectApi.CreditInvoiceInputRequest, String], ConnectApi.RevenueAsyncLineLevelOutputResponse
```

#### Parameters

CreditInvoiceInput
:   Type: [`ConnectApi.CreditInvoiceInputRequest`](./apex_connectapi_input_credit_invoice.htm.md "Input representation of the details of the request to create a credit memo.")
:   Input representation of the details of the request to create a credit memo.

invoiceId
:   Type: String
:   ID of the invoice to be credited partially or fully. The status of the invoice must be `Posted`.

#### Return Value

Type: [`ConnectApi.RevenueAsyncLineLevelOutputResponse`](./apex_connectapi_output_revenue_async_line_level.htm.md "Output representation of the result of the API request for the async line level operations.")

#### Usage

Use this method to adjust an outstanding invoice balance or rectify errors in an invoice.
Pass a list of invoice lines to credit. Keep these considerations in mind when you use this
API.

- The request must contain at least one invoice line. Each invoice line must have the
  invoice line’s ID, the amount to credit, and any optional tax details. The invoice lines
  must be a part of the invoice passed in the resource.
- The amount to credit must not exceed the charge or adjustment amount of an individual
  invoice line.
- The request body's credit amount inclusive of taxes must not exceed the target invoice
  line's amount inclusive of taxes, except for taxes calculated through an external tax
  service.
- The request body's total credit amount inclusive of taxes calculated through an external
  tax service must not exceed the outstanding invoice balance, which is also inclusive of
  taxes.

This method creates and posts a credit memo. The credit memo has one credit memo line for
each invoice line passed in the API request. The invoice’s balance is then reduced by a
value equal to the credit memo’s balance. This API modifies the balance of a posted invoice
or invoice line based on the specified credit application level for your org. See [Apply Credits to Posted Invoices or
Invoice Lines](https://help.salesforce.com/s/articleView?id=sf.billing_setup_credit_application_level.htm&language=en_US "HTML (New Window)").

### generateInvoices(inputRequest)

Create an invoice from a billing schedule.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation generateInvoices(ConnectApi.InvoiceInputRepresentation inputRequest)`

```
ConnectApi.Billing, generateInvoices, [ConnectApi.InvoiceInputRepresentation], ConnectApi.RevenueAsyncRepresentation
```

#### Parameters

inputRequest
:   Type: [ConnectApi.InvoiceInputRepresentation](./apex_connectapi_input_invoice.htm.md "Input representation of the details of the billing schedule.")
:   Input representation of the details of the billing schedule.

#### Return Value

Type: [ConnectApi.RevenueAsyncRepresentation](./apex_connectapi_output_revenue_async.htm.md "Output representation of the result of the API request with the request identifier.")

#### Usage

You need the Generate Invoices From Billing Schedule API permission
set to use this method.

This method creates one billing period item for each unbilled
period between the billing schedule's next billing date and the invoice's target date.
Additionally, one invoice line is created for each billing period item. This method creates
up to six billing periods per request.

### recoverBillingSchedules(inputRequest)

Recover the latest generated invoice associated with the billing schedules in the Error
or Processing status.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.BillingScheduleRecoveryResults recoverBillingSchedules(ConnectApi.BillingScheduleRecoveryInputRequest inputRequest)`

```
ConnectApi.Billing, recoverBillingSchedules, [ConnectApi.BillingScheduleRecoveryInputRequest], ConnectApi.BillingScheduleRecoveryResults
```

#### Parameters

inputRequest
:   Type: [ConnectApi.BillingScheduleRecoveryInputRequest](./apex_connectapi_input_billing_schedule_recovery.htm.md "Input representation of the details of the billing schedules to recover the associated invoice.")
:   Input representation of the details of the billing schedules to recover the associated
    invoice.

#### Return Value

Type: [ConnectApi.BillingScheduleRecoveryResults](./apex_connectapi_output_billing_schedule_recovery_list_output.htm.md "Output representation of the recovered details of the billing schedules and associated invoice.")

#### Usage

You need the Manage Errors Using Invoice Error Recovery API permission set to use this
method.

Billing schedules include critical details such as the amount to be billed, next billing
date, and status. An invoice can be associated with one or more billing schedules. When an
invoice is generated or posted, the billing schedules are updated to reflect the accurate
state of the invoice. The billing schedules associated with an invoice are marked in the
`Error` status if any of the invoicing processes have
errors. Use this method to recover the invoice associated with the billing schedules in the
`Error` or `Processing` status.

### voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

#### API Version

66.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.VoidPostedCreditMemoOutputRepresentation voidPostedCreditMemo(ConnectApi.VoidPostedCreditMemoInputRepresentation VoidPostedCreditMemoInput, String creditMemoId)`

```
ConnectApi.Billing, voidPostedCreditMemo, [ConnectApi.VoidPostedCreditMemoInputRepresentation, String], ConnectApi.VoidPostedCreditMemoOutputRepresentation
```

#### Parameters

VoidPostedCreditMemoInput
:   Type: [`ConnectApi.VoidPostedCreditMemoInputRepresentation`](./apex_connectapi_input_void_posted_credit_memo.htm.md "Input representation of the details of a credit memo to be voided.")
:   Input representation of the details of a credit memo to be voided.

creditMemoId
:   Type: String
:   Required. ID of the credit memo record in posted status to be voided.

#### Return Value

Type: [`ConnectApi.VoidPostedCreditMemoOutputRepresentation`](./apex_connectapi_output_void_posted_credit_memo_output.htm.md "Output representation of the request to void a posted credit memo.")

### voidPostedInvoice(invoiceId)

Void a posted invoice to rebill the customer, if necessary.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation
voidPostedInvoice(String invoiceId)`

#### Parameters

invoiceId
:   Type: String
:   ID of the posted invoice to be voided.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex_connectapi_output_revenue_async.htm.md "Output representation of the result of the API request with the request identifier.")

#### Usage

You need the Void a Posted Invoice API permission set to use this
method.

This method changes the invoice status from `Posted` to `Void In Progress`. The invoice
remains in the `Void In Progress` status until the credit
is applied and financial fields are recalculated on the invoice’s related billing period
items and billing schedule. The invoice status changes to `Voided` after all recalculations are completed.

Keep these considerations
in mind when you use this method.

- The balance and total amount on the invoice must be equal. If these amounts aren’t equal
  due to payments or credits, the API request fails.
- You can’t call other APIs on an invoice with the `Void In
  Progress` status. You also can’t update the invoice fields.
- You can void only the most recently posted invoice on a billing schedule.
- To void an invoice that has payments or credits, use the [Credit Memo
  Unapply (POST)](https://developer.salesforce.com/docs/./connect_resources_credit_memo_invoice_application_unapply.htm.md "HTML (New Window)")  API.

Credit Memos
:   The void process creates a credit memo, which contains one credit memo line for each
    invoice line, including tax lines. For example, if the invoice line has a balance of
    US$20, the related credit memo line has a balance of $20. The credit memo’s balance is
    then allocated to the invoice header’s balance, reducing it to zero. A credit memo
    invoice application is created to record the details of the void process.

Negative Invoice Lines
:   If an invoice has negative invoice lines that aren’t converted to a credit memo, you
    can use this endpoint to void the posted invoice.
