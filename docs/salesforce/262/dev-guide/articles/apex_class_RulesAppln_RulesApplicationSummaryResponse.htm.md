---
page_id: apex_class_RulesAppln_RulesApplicationSummaryResponse.htm
title: RulesApplicationSummaryResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RulesAppln_RulesApplicationSummaryResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_RulesAppln.htm
fetched_at: 2026-06-09
---

# RulesApplicationSummaryResponse Class

Contains properties to store the summary details of the rules application, including payment and credit memo counts and application statistics.

## Namespace

[RulesAppln](./apex_namespace_RulesAppln.htm.md "Apply payments and credits to posted invoices by adhering to the specified rules.")

- **[RulesApplicationSummaryResponse Constructors](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_constructors)**  
  Learn more about the constructors available with the RulesApplicationSummaryResponse class.
- **[RulesApplicationSummaryResponse Properties](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_properties)**  
  Learn more about the properties available with the RulesApplicationSummaryResponse class.

## RulesApplicationSummaryResponse Constructors

Learn more about the constructors available with the RulesApplicationSummaryResponse
class.

The `RulesApplicationSummaryResponse` class includes these
constructors.

- **[RulesApplicationSummaryResponse(fetchedPaymentsCount, fetchedCreditMemosCount, totalPaymentApplications, totalCreditMemoApplications, areAllInvoicesConsidered)](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_ctor)**  
  Initializes the RulesApplicationSummaryResponse class that stores the summary details of the rules application.
- **[RulesApplicationSummaryResponse()](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_ctor_2)**  
  Initializes an empty instance of the RulesApplicationSummaryResponse class.

### RulesApplicationSummaryResponse(fetchedPaymentsCount, fetchedCreditMemosCount, totalPaymentApplications, totalCreditMemoApplications, areAllInvoicesConsidered)

Initializes the RulesApplicationSummaryResponse class that stores the summary details of the rules application.

#### Signature

`public RulesApplicationSummaryResponse(Integer fetchedPaymentsCount, Integer fetchedCreditMemosCount, Integer totalPaymentApplications, Integer totalCreditMemoApplications, Boolean areAllInvoicesConsidered)`

```
RulesAppln.RulesApplicationSummaryResponse, newinstance, [Integer, Integer, Integer, Integer, Boolean], RulesAppln.RulesApplicationSummaryResponse
```

#### Parameters

fetchedPaymentsCount
:   Type: Integer
:   Number of payment records retrieved for an account.

fetchedCreditMemosCount
:   Type: Integer
:   Number of credit memo or credit memo line records retrieved for an account.

totalPaymentApplications
:   Type: Integer
:   Number of payments that are applied to invoices and invoice lines.

totalCreditMemoApplications
:   Type: Integer
:   Number of credit memos that are applied to the invoice or invoice lines.

areAllInvoicesConsidered
:   Type: Boolean
:   Indicates whether all invoices are considered (`true`) or not
    (`false`).

### RulesApplicationSummaryResponse()

Initializes an empty instance of the RulesApplicationSummaryResponse class.

#### Signature

`public RulesApplicationSummaryResponse()`

```
RulesAppln.RulesApplicationSummaryResponse, newinstance, [], RulesAppln.RulesApplicationSummaryResponse
```

## RulesApplicationSummaryResponse Properties

Learn more about the properties available with the RulesApplicationSummaryResponse
class.

The `RulesApplicationSummaryResponse` class includes these
properties.

- **[areAllInvoicesConsidered](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_areAllInvoicesConsidered)**  
  Indicates whether all invoices are considered (true) or not (false).
- **[fetchedCreditMemosCount](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_fetchedCreditMemosCount)**  
  Get the number of credit memo or credit memo line records retrieved for an account.
- **[fetchedPaymentsCount](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_fetchedPaymentsCount)**  
  Get the number of payment records retrieved for an account.
- **[totalCreditMemoApplications](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_totalCreditMemoApplications)**  
  Get the number of credit memos that are applied to the invoice or invoice lines.
- **[totalPaymentApplications](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_RulesAppln_RulesApplicationSummaryResponse_totalPaymentApplications)**  
  Get the number of payments that are applied to invoices and invoice lines.

### areAllInvoicesConsidered

Indicates whether all invoices are considered (true) or not (false).

#### Signature

`public Boolean areAllInvoicesConsidered {get; set;}`

```
RulesAppln.RulesApplicationSummaryResponse, areAllInvoicesConsidered
```

#### Property Value

Type: Boolean

### fetchedCreditMemosCount

Get the number of credit memo or credit memo line records retrieved for an
account.

#### Signature

`public Integer fetchedCreditMemosCount {get; set;}`

```
RulesAppln.RulesApplicationSummaryResponse, fetchedCreditMemosCount
```

#### Property Value

Type: Integer

### fetchedPaymentsCount

Get the number of payment records retrieved for an account.

#### Signature

`public Integer fetchedPaymentsCount {get; set;}`

```
RulesAppln.RulesApplicationSummaryResponse, fetchedPaymentsCount
```

#### Property Value

Type: Integer

### totalCreditMemoApplications

Get the number of credit memos that are applied to the invoice or invoice
lines.

#### Signature

`public Integer totalCreditMemoApplications {get; set;}`

```
RulesAppln.RulesApplicationSummaryResponse, totalCreditMemoApplications
```

#### Property Value

Type: Integer

### totalPaymentApplications

Get the number of payments that are applied to invoices and invoice lines.

#### Signature

`public Integer totalPaymentApplications {get; set;}`

```
RulesAppln.RulesApplicationSummaryResponse, totalPaymentApplications
```

#### Property Value

Type: Integer
