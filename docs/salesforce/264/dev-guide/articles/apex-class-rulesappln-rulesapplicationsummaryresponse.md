---
page_id: apex-class-rulesappln-rulesapplicationsummaryresponse
title: RulesApplicationSummaryResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationsummaryresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-rulesappln
legacy_page_id: apex_class_RulesAppln_RulesApplicationSummaryResponse.htm
fetched_at: 2026-11-25
---

# RulesApplicationSummaryResponse Class

Contains properties to store the summary details of the rules application, including payment and credit memo counts and application statistics.

## Namespace

[RulesAppln](./apex-namespace-rulesappln.md)

- 

**[RulesApplicationSummaryResponse Constructors](#rulesapplicationsummaryresponse-constructors)**

Learn more about the constructors available with the RulesApplicationSummaryResponse class.

- 

**[RulesApplicationSummaryResponse Properties](#rulesapplicationsummaryresponse-properties)**

Learn more about the properties available with the RulesApplicationSummaryResponse class.

## RulesApplicationSummaryResponse Constructors

Learn more about the constructors available with the RulesApplicationSummaryResponse class.

The `RulesApplicationSummaryResponse` class includes these constructors.

- 

**[RulesApplicationSummaryResponse(fetchedPaymentsCount, fetchedCreditMemosCount, totalPaymentApplications, totalCreditMemoApplications, areAllInvoicesConsidered)](#rulesapplicationsummaryresponsefetchedpaymentscount-fetchedcreditmemoscount-totalpaymentapplications-totalcreditmemoapplications-areallinvoicesconsidered)**

Initializes the RulesApplicationSummaryResponse class that stores the summary details of the rules application.

- 

**[RulesApplicationSummaryResponse()](#rulesapplicationsummaryresponse)**

Initializes an empty instance of the RulesApplicationSummaryResponse class.

### RulesApplicationSummaryResponse(fetchedPaymentsCount, fetchedCreditMemosCount, totalPaymentApplications, totalCreditMemoApplications, areAllInvoicesConsidered)

Initializes the RulesApplicationSummaryResponse class that stores the summary details of the rules application.

#### Signature

`public RulesApplicationSummaryResponse(Integer fetchedPaymentsCount, Integer fetchedCreditMemosCount, Integer totalPaymentApplications, Integer totalCreditMemoApplications, Boolean areAllInvoicesConsidered)`

#### Parameters

***fetchedPaymentsCount***

Type: Integer

Number of payment records retrieved for an account.

***fetchedCreditMemosCount***

Type: Integer

Number of credit memo or credit memo line records retrieved for an account.

***totalPaymentApplications***

Type: Integer

Number of payments that are applied to invoices and invoice lines.

***totalCreditMemoApplications***

Type: Integer

Number of credit memos that are applied to the invoice or invoice lines.

***areAllInvoicesConsidered***

Type: Boolean

Indicates whether all invoices are considered (`true`) or not (`false`).

### RulesApplicationSummaryResponse()

Initializes an empty instance of the RulesApplicationSummaryResponse class.

#### Signature

`public RulesApplicationSummaryResponse()`

## RulesApplicationSummaryResponse Properties

Learn more about the properties available with the RulesApplicationSummaryResponse class.

The `RulesApplicationSummaryResponse` class includes these properties.

- 

**[areAllInvoicesConsidered](#areallinvoicesconsidered)**

Indicates whether all invoices are considered (true) or not (false).

- 

**[fetchedCreditMemosCount](#fetchedcreditmemoscount)**

Get the number of credit memo or credit memo line records retrieved for an account.

- 

**[fetchedPaymentsCount](#fetchedpaymentscount)**

Get the number of payment records retrieved for an account.

- 

**[totalCreditMemoApplications](#totalcreditmemoapplications)**

Get the number of credit memos that are applied to the invoice or invoice lines.

- 

**[totalPaymentApplications](#totalpaymentapplications)**

Get the number of payments that are applied to invoices and invoice lines.

### areAllInvoicesConsidered

Indicates whether all invoices are considered (true) or not (false).

#### Signature

`public Boolean areAllInvoicesConsidered {get; set;}`

#### Property Value

Type: Boolean

### fetchedCreditMemosCount

Get the number of credit memo or credit memo line records retrieved for an account.

#### Signature

`public Integer fetchedCreditMemosCount {get; set;}`

#### Property Value

Type: Integer

### fetchedPaymentsCount

Get the number of payment records retrieved for an account.

#### Signature

`public Integer fetchedPaymentsCount {get; set;}`

#### Property Value

Type: Integer

### totalCreditMemoApplications

Get the number of credit memos that are applied to the invoice or invoice lines.

#### Signature

`public Integer totalCreditMemoApplications {get; set;}`

#### Property Value

Type: Integer

### totalPaymentApplications

Get the number of payments that are applied to invoices and invoice lines.

#### Signature

`public Integer totalPaymentApplications {get; set;}`

#### Property Value

Type: Integer

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationsummaryresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
