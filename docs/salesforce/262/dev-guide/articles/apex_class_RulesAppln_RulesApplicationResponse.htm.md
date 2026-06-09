---
page_id: apex_class_RulesAppln_RulesApplicationResponse.htm
title: RulesApplicationResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RulesAppln_RulesApplicationResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_RulesAppln.htm
fetched_at: 2026-06-09
---

# RulesApplicationResponse Class

Contains properties to store the response details for the rules application request.

## Namespace

[RulesAppln](./apex_namespace_RulesAppln.htm.md "Apply payments and credits to posted invoices by adhering to the specified rules.")

- **[RulesApplicationResponse Constructors](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_constructors)**  
  Learn more about the constructors available with the RulesApplicationResponse class.
- **[RulesApplicationResponse Properties](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_properties)**  
  Learn more about the properties available with the RulesApplicationResponse class.

## RulesApplicationResponse Constructors

Learn more about the constructors available with the RulesApplicationResponse
class.

The `RulesApplicationResponse` class includes these
constructors.

- **[RulesApplicationResponse(isSuccess, appliedRules, rulesApplicationSummary, errors)](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_ctor)**  
  Initializes the RulesApplicationResponse class that stores the response details for the rules application request.
- **[RulesApplicationResponse()](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_ctor_2)**  
  Initializes an empty instance of the RulesApplicationResponse class.

### RulesApplicationResponse(isSuccess, appliedRules, rulesApplicationSummary, errors)

Initializes the RulesApplicationResponse class that stores the response details for the rules application request.

#### Signature

`public RulesApplicationResponse(Boolean isSuccess, List<String> appliedRules, RulesAppln.RulesApplicationSummaryResponse rulesApplicationSummary, List<RulesAppln.RulesApplicationErrorResponse> errors)`

```
RulesAppln.RulesApplicationResponse, newinstance, [Boolean, List<String>, RulesAppln.RulesApplicationSummaryResponse, List<RulesAppln.RulesApplicationErrorResponse>], RulesAppln.RulesApplicationResponse
```

#### Parameters

isSuccess
:   Type: Boolean
:   Indicates whether the rules are applied (`true`) or not
    (`false`).

appliedRules
:   Type: List<String>
:   Comma-delimited list of applied rules.

rulesApplicationSummary
:   Type: [RulesAppln.RulesApplicationSummaryResponse](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_class_RulesAppln_RulesApplicationSummaryResponse "Contains properties to store the summary details of the rules application, including payment and credit memo counts and application statistics.")
:   Details of the rules application that includes these details.

    - Payment and credit memo count for the account
    - Payment and credit memo count that's applied to invoices or invoice lines
    - Details of rules

errors
:   Type: List<[RulesAppln.RulesApplicationErrorResponse](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_class_RulesAppln_RulesApplicationErrorResponse "Contains properties to store error details that occurred during the rules application.")>
:   List of error responses that occurred during the rules application.

### RulesApplicationResponse()

Initializes an empty instance of the RulesApplicationResponse class.

#### Signature

`public RulesApplicationResponse()`

```
RulesAppln.RulesApplicationResponse, newinstance, [], RulesAppln.RulesApplicationResponse
```

## RulesApplicationResponse Properties

Learn more about the properties available with the RulesApplicationResponse
class.

The `RulesApplicationResponse` class includes these
properties.

- **[appliedRules](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_appliedRules)**  
  Get the comma-delimited list of rules that were applied.
- **[errors](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_errors)**  
  Get the list of error responses that occurred during the rules application.
- **[isSuccess](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_isSuccess)**  
  Get the boolean value that indicates whether the rules were applied (true) or not (false).
- **[rulesApplicationSummary](./apex_class_RulesAppln_RulesApplicationResponse.htm.md#apex_RulesAppln_RulesApplicationResponse_rulesApplicationSummary)**  
  Get the details of the rules application that includes payment and credit memo count for the account, payment and credit memo count that's applied to invoices or invoice lines, and whether the exact amount rule is applied.

### appliedRules

Get the comma-delimited list of rules that were applied.

#### Signature

`public List<String> appliedRules {get; set;}`

```
RulesAppln.RulesApplicationResponse, appliedRules
```

#### Property Value

Type: List<String>

### errors

Get the list of error responses that occurred during the rules application.

#### Signature

`public List<RulesAppln.RulesApplicationErrorResponse> errors {get; set;}`

```
RulesAppln.RulesApplicationResponse, errors
```

#### Property Value

Type: List<[RulesAppln.RulesApplicationErrorResponse](./apex_class_RulesAppln_RulesApplicationErrorResponse.htm.md#apex_class_RulesAppln_RulesApplicationErrorResponse "Contains properties to store error details that occurred during the rules application.")>

### isSuccess

Get the boolean value that indicates whether the rules were applied (true) or not
(false).

#### Signature

`public Boolean isSuccess {get; set;}`

```
RulesAppln.RulesApplicationResponse, isSuccess
```

#### Property Value

Type: Boolean

### rulesApplicationSummary

Get the details of the rules application that includes payment and credit memo count for
the account, payment and credit memo count that's applied to invoices or invoice lines, and
whether the exact amount rule is applied.

#### Signature

`public RulesAppln.RulesApplicationSummaryResponse rulesApplicationSummary {get; set;}`

```
RulesAppln.RulesApplicationResponse, rulesApplicationSummary
```

#### Property Value

Type: [RulesAppln.RulesApplicationSummaryResponse](./apex_class_RulesAppln_RulesApplicationSummaryResponse.htm.md#apex_class_RulesAppln_RulesApplicationSummaryResponse "Contains properties to store the summary details of the rules application, including payment and credit memo counts and application statistics.")
