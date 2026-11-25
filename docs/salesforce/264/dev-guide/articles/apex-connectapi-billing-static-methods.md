---
page_id: apex-connectapi-billing-static-methods
title: Billing Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-billing-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_Billing_static_methods.htm
fetched_at: 2026-11-25
---

# Billing Class

Manage billing scenarios by using the Billing class. You can convert negative invoice lines, create and apply a credit memo to an invoice, generate invoices, and recover billing schedules.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## Billing Methods

These methods are for `Billing`. All methods are static.

- 

**[convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)](#convertnegativeinvoicelinesconvertnegativeinvoicelinesinput-invoiceid)**

Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.

- 

**[createCreditMemos(CreditMemoInputRequest)](#createcreditmemoscreditmemoinputrequest)**

Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.

- 

**[creditInvoice(CreditInvoiceInput, invoiceId)](#creditinvoicecreditinvoiceinput-invoiceid)**

Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.

- 

**[generateInvoices(inputRequest)](#generateinvoicesinputrequest)**

Create an invoice from a billing schedule.

- 

**[recoverBillingSchedules(inputRequest)](#recoverbillingschedulesinputrequest)**

Recover the latest generated invoice associated with the billing schedules in the Error or Processing status.

- 

**[voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)](#voidpostedcreditmemovoidpostedcreditmemoinput-creditmemoid)**

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

- 

**[voidPostedInvoice(invoiceId)](#voidpostedinvoiceinvoiceid)**

Void a posted invoice to rebill the customer, if necessary.

### convertNegativeInvoiceLines(ConvertNegativeInvoiceLinesInput, invoiceId)

Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.ConvertNegativeInvoiceLinesResult convertNegativeInvoiceLines(ConnectApi.ConvertNegativeInvoiceLinesInputRequest ConvertNegativeInvoiceLinesInput, String invoiceId)`

#### Parameters

***ConvertNegativeInvoiceLinesInput***

Type: [ConnectApi.ConvertNegativeInvoiceLinesInputRequest](./apex-connectapi-input-convert-negative-invoice-lines.md)

Input parameters to convert a negative invoice line to a credit.

***invoiceId***

Type: String

ID of the invoice whose negative invoice lines must be converted.

#### Return Value

Type: [ConnectApi.ConvertNegativeInvoiceLinesResult](./apex-connectapi-output-convert-negative-invoice-lines-output.md)

#### Usage

You need the Credit Memo Operations User permission set to use this method.

Keep these considerations in mind when you use this method.

- All invoice lines must be related to the same invoice.

- The invoice line must have a negative amount.

- The invoice line must not be a previously converted credit memo.

- The invoice must have the `Posted` status.

- The invoice must not have any active settlements such as credit applications.

### createCreditMemos(CreditMemoInputRequest)

Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation createCreditMemos(ConnectApi.StandaloneCreditMemoInputRequest CreditMemoInputRequest)`

#### Parameters

***CreditMemoInputRequest***

Type: [`ConnectApi.StandaloneCreditMemoInputRequest`](./apex-connectapi-input-standalone-credit-memo.md)

Input representation of the details required to create a standalone credit memo.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex-connectapi-output-revenue-async.md)

#### Usage

You need the Credit Memo Operations User permission set to use this method.

Specify the credit memo header information, charge parameters, adjustment parameters, and tax parameters. A credit memo requires at least one credit memo line. The credit memo line can be a charge or an adjustment.

Specify the credit memo lines that you want as lists of charges and adjustments. Each credit memo line must be related to a product.

### creditInvoice(CreditInvoiceInput, invoiceId)

Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncLineLevelOutputResponse creditInvoice(ConnectApi.CreditInvoiceInputRequest CreditInvoiceInput, String invoiceId)`

#### Parameters

***CreditInvoiceInput***

Type: [`ConnectApi.CreditInvoiceInputRequest`](./apex-connectapi-input-credit-invoice.md)

Input representation of the details of the request to create a credit memo.

***invoiceId***

Type: String

ID of the invoice to be credited partially or fully. The status of the invoice must be `Posted`.

#### Return Value

Type: [`ConnectApi.RevenueAsyncLineLevelOutputResponse`](./apex-connectapi-output-revenue-async-line-level.md)

#### Usage

Use this method to adjust an outstanding invoice balance or rectify errors in an invoice. Pass a list of invoice lines to credit. Keep these considerations in mind when you use this API.

- The request must contain at least one invoice line. Each invoice line must have the invoice line’s ID, the amount to credit, and any optional tax details. The invoice lines must be a part of the invoice passed in the resource.

- The amount to credit must not exceed the charge or adjustment amount of an individual invoice line.

- The request body’s credit amount inclusive of taxes must not exceed the target invoice line’s amount inclusive of taxes, except for taxes calculated through an external tax service.

- The request body’s total credit amount inclusive of taxes calculated through an external tax service must not exceed the outstanding invoice balance, which is also inclusive of taxes.

This method creates and posts a credit memo. The credit memo has one credit memo line for each invoice line passed in the API request. The invoice’s balance is then reduced by a value equal to the credit memo’s balance. This API modifies the balance of a posted invoice or invoice line based on the specified credit application level for your org. See [Apply Credits to Posted Invoices or Invoice Lines](https://help.salesforce.com/s/articleView?id=sf.billing_setup_credit_application_level.htm).

### generateInvoices(inputRequest)

Create an invoice from a billing schedule.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation generateInvoices(ConnectApi.InvoiceInputRepresentation inputRequest)`

#### Parameters

***inputRequest***

Type: [ConnectApi.InvoiceInputRepresentation](./apex-connectapi-input-invoice.md)

Input representation of the details of the billing schedule.

#### Return Value

Type: [ConnectApi.RevenueAsyncRepresentation](./apex-connectapi-output-revenue-async.md)

#### Usage

You need the Generate Invoices From Billing Schedule API permission set to use this method.

This method creates one billing period item for each unbilled period between the billing schedule’s next billing date and the invoice’s target date. Additionally, one invoice line is created for each billing period item. This method creates up to six billing periods per request.

### recoverBillingSchedules(inputRequest)

Recover the latest generated invoice associated with the billing schedules in the Error or Processing status.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.BillingScheduleRecoveryResults recoverBillingSchedules(ConnectApi.BillingScheduleRecoveryInputRequest inputRequest)`

#### Parameters

***inputRequest***

Type: [ConnectApi.BillingScheduleRecoveryInputRequest](./apex-connectapi-input-billing-schedule-recovery.md)

Input representation of the details of the billing schedules to recover the associated invoice.

#### Return Value

Type: [ConnectApi.BillingScheduleRecoveryResults](./apex-connectapi-output-billing-schedule-recovery-list-output.md)

#### Usage

You need the Manage Errors Using Invoice Error Recovery API permission set to use this method.

Billing schedules include critical details such as the amount to be billed, next billing date, and status. An invoice can be associated with one or more billing schedules. When an invoice is generated or posted, the billing schedules are updated to reflect the accurate state of the invoice. The billing schedules associated with an invoice are marked in the `Error` status if any of the invoicing processes have errors. Use this method to recover the invoice associated with the billing schedules in the `Error` or `Processing` status.

### voidPostedCreditMemo(VoidPostedCreditMemoInput, creditMemoId)

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

#### API Version

66.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.VoidPostedCreditMemoOutputRepresentation voidPostedCreditMemo(ConnectApi.VoidPostedCreditMemoInputRepresentation VoidPostedCreditMemoInput, String creditMemoId)`

#### Parameters

***VoidPostedCreditMemoInput***

Type: [`ConnectApi.VoidPostedCreditMemoInputRepresentation`](./apex-connectapi-input-void-posted-credit-memo.md)

Input representation of the details of a credit memo to be voided.

***creditMemoId***

Type: String

Required. ID of the credit memo record in posted status to be voided.

#### Return Value

Type: [`ConnectApi.VoidPostedCreditMemoOutputRepresentation`](./apex-connectapi-output-void-posted-credit-memo-output.md)

### voidPostedInvoice(invoiceId)

Void a posted invoice to rebill the customer, if necessary.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation voidPostedInvoice(String invoiceId)`

#### Parameters

***invoiceId***

Type: String

ID of the posted invoice to be voided.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex-connectapi-output-revenue-async.md)

#### Usage

You need the Void a Posted Invoice API permission set to use this method.

This method changes the invoice status from `Posted` to `Void In Progress`. The invoice remains in the `Void In Progress` status until the credit is applied and financial fields are recalculated on the invoice’s related billing period items and billing schedule. The invoice status changes to `Voided` after all recalculations are completed.

Keep these considerations in mind when you use this method.

- The balance and total amount on the invoice must be equal. If these amounts aren’t equal due to payments or credits, the API request fails.

- You can’t call other APIs on an invoice with the `Void In Progress` status. You also can’t update the invoice fields.

- You can void only the most recently posted invoice on a billing schedule.

- To void an invoice that has payments or credits, use the [Credit Memo Unapply (POST)](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_invoice_application_unapply.htm) API.

**Credit Memos**

The void process creates a credit memo, which contains one credit memo line for each invoice line, including tax lines. For example, if the invoice line has a balance of US$20, the related credit memo line has a balance of $20. The credit memo’s balance is then allocated to the invoice header’s balance, reducing it to zero. A credit memo invoice application is created to record the details of the void process.

**Negative Invoice Lines**

If an invoice has negative invoice lines that aren’t converted to a credit memo, you can use this endpoint to void the posted invoice.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-billing-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
