---
page_id: apex_class_commercetax_RuleDetailsResponse.htm
title: RuleDetailsResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_RuleDetailsResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# RuleDetailsResponse Class

Contains details about the tax rules used for tax
calculation.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[RuleDetailsResponse Methods](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_methods)**  
  Learn more about the available methods with the `RuleDetailsResponse` class.

## RuleDetailsResponse Methods

Learn more about the available methods with the `RuleDetailsResponse` class.

The `RuleDetailsResponse` includes these methods.

- **[RuleDetailsResponse()](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_RuleDetailsResponse)**  
  Contains information about the tax rules used when calculating tax for line items.
- **[setNonTaxableRuleId(nonTaxableRuleId)](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_setNonTaxableRuleId)**  
  Sets the NonTaxableRuleId field of the `RuleDetailsResponse`.
- **[setNonTaxableType(nonTaxableType)](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_setNonTaxableType)**  
  Sets the NonTaxableType field of the `RuleDetailsResponse`.
- **[setRateRuleId(rateRuleId)](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_setRateRuleId)**  
  Sets the RateRuleId field of the `RuleDetailsResponse`.
- **[setRateSourceId(rateSourceId)](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_commercetax_RuleDetailsResponse_setRateSourceId)**  
  Sets the RateSourceId field on the `RuleDetailsResponse`.

### RuleDetailsResponse()

Contains information about the tax rules used when calculating tax
for line items.

#### Signature

`global void
RuleDetailsResponse()`

#### Return Value

Type: void

### setNonTaxableRuleId(nonTaxableRuleId)

Sets the NonTaxableRuleId field of the `RuleDetailsResponse`.

#### Signature

`global void
setNonTaxableRuleId(String
nonTaxableRuleId)`

#### Parameters

nonTaxableRuleId
:   Type: String
:   ID of the tax rule applied to non-taxable line items.

#### Return Value

Type: void

### setNonTaxableType(nonTaxableType)

Sets the NonTaxableType field of the `RuleDetailsResponse`.

#### Signature

`global void
setNonTaxableType(String
nonTaxableType)`

#### Parameters

nonTaxableType
:   Type: String
:   Reason
    (from
    several possible types) that a line item is non-taxable.

#### Return Value

Type: void

### setRateRuleId(rateRuleId)

Sets the RateRuleId field of the `RuleDetailsResponse`.

#### Signature

`global void
setRateRuleId(String
rateRuleId)`

#### Parameters

rateRuleId
:   Type: String
:   ID of the tax rule used to determine a tax rate.

#### Return Value

Type: void

### setRateSourceId(rateSourceId)

Sets the RateSourceId field on the `RuleDetailsResponse`.

#### Signature

`global void
setRateSourceId(String
rateSourceId)`

#### Parameters

rateSourceId
:   Type: String
:   ID of the source object used for calculating tax rate.

#### Return Value

Type: void
