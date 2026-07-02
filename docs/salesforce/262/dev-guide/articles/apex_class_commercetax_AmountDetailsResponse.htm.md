---
page_id: apex_class_commercetax_AmountDetailsResponse.htm
title: AmountDetailsResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AmountDetailsResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# AmountDetailsResponse Class

Sets tax amount fields based on a response from the external tax
engine.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Example

In this example, an instance of `AmountDetailsResponse`
class in a mock adapter calculates several tax amount fields. The `totalTax` and `totalAmount` parameters were
defined in an instance of [`LineItemResponse`](./apex_class_commercetax_LineItemResponse.htm.md#apex_class_commercetax_LineItemResponse "Response class that stores details of a list of one or more line items on which the tax engine has calculated tax.") class. The adapter then assigns the instance to
`lineItemResponse`.

commercetax.AmountDetailsResponse amountResponse = new commercetax.AmountDetailsResponse();
amountResponse.setTotalAmountWithTax(totalTax+totalAmount);
amountResponse.setExemptAmount(0);
amountResponse.setTotalAmount(totalAmount);
amountResponse.setTaxAmount(totalTax);
lineItemResponse.setAmountDetails(amountResponse);

- **[AmountDetailsResponse Methods](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_commercetax_AmountDetailsResponse_methods)**  
  Learn more about the methods available from the `AmountDetailsResponse` class.

## AmountDetailsResponse Methods

Learn more about the methods available from the `AmountDetailsResponse` class.

The following are methods for `AmountDetailsResponse`.

- **[setExemptAmount(exemptAmount)](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_commercetax_AmountDetailsResponse_setExemptAmount)**  
  Sets the value of the ExemptAmount field.
- **[setTaxAmount(taxAmount)](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_commercetax_AmountDetailsResponse_setTaxAmount)**  
  Sets the value of the TaxAmount field.
- **[setTotalAmount(totalAmount)](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_commercetax_AmountDetailsResponse_setTotalAmount)**  
  Sets the value of the TotalAmount field.
- **[setTotalAmountWithTax(totalAmtWithTax)](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_commercetax_AmountDetailsResponse_setTotalAmountWithTax)**  
  Sets the value of the TotalAmountWithTax field.

### setExemptAmount(exemptAmount)

Sets the value of the ExemptAmount field.

#### Signature

`global void
setExemptAmount(Double
exemptAmount)`

#### Parameters

exemptAmount
:   Type: Double
:   The amount of a line item's total amount that's exempt from tax calculation.

#### Return Value

Type: void

### setTaxAmount(taxAmount)

Sets the value of the TaxAmount field.

#### Signature

`global void
setTaxAmount(Double
taxAmount)`

#### Parameters

taxAmount
:   Type: Double
:   The calculated amount of tax for a line item.

#### Return Value

Type: void

### setTotalAmount(totalAmount)

Sets the value of the TotalAmount field.

#### Signature

`global void
setTotalAmount(Double
totalAmount)`

#### Parameters

totalAmount
:   Type: Double
:   The total amount of a line item, excluding tax.

#### Return Value

Type: void

### setTotalAmountWithTax(totalAmtWithTax)

Sets the value of the TotalAmountWithTax field.

#### Signature

`global void setTotalAmountWithTax(Double totalAmtWithTax)`

#### Parameters

totalAmtWithTax
:   Type: Double
:   The total amount of a line item combined with the calculated tax for that line
    item.

#### Return Value

Type: void
