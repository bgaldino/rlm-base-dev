---
page_id: apex_class_commercetax_TaxDetailsResponse.htm
title: TaxDetailsResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxDetailsResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxDetailsResponse Class

Stores details of the tax values that an external tax engine
calculates in response to a tax calculation request.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Usage

If your tax calculation request contains multiple line items,
we recommend building your adapter using a list of `TaxDetailsResponse` instances. Each instance represents the tax details
calculated for a given line item.

## Example

List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
for(integer i =0;i<1;i++){
Integer rate = 1;
Double taxableAmount = lineItem.amount;
commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
taxDetailsResponse.setRate(Double.valueOf(rate));
taxDetailsResponse.setTaxableAmount(taxableAmount);
Double tax = taxableAmount\*rate;
totalLineTax+=tax;
taxDetailsResponse.setTax(taxableAmount\*rate);
taxDetailsResponse.setExemptAmount(0);
taxDetailsResponse.setExemptReason('exemptReason');
taxDetailsResponse.setTaxRegionId('taxRegionId');
taxDetailsResponse.setTaxId(String.valueOf(getRandomInteger(0,2323233)));
taxDetailsResponse.setSerCode('serCode');
taxDetailsResponse.setTaxAuthorityTypeId('taxAuthorityTypeId');
if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
taxDetailsResponse.setImposition(null);
}else{
commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
imposition.setSubType('subtype');
imposition.setType('type');
taxDetailsResponse.setImposition(imposition);
}
if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
taxDetailsResponse.setJurisdiction(null);
}else{
commercetax.JurisdictionResponse jurisdiction = new commercetax.JurisdictionResponse();
jurisdiction.setCountry('country');
jurisdiction.setRegion('region');
jurisdiction.setName('name');
jurisdiction.setStateAssignedNumber('stateAssignedNo');
jurisdiction.setId('id');
jurisdiction.setLevel('level');
taxDetailsResponse.setJurisdiction(jurisdiction);
}
taxDetailsResponses.add(taxDetailsResponse);
}
lineItemResponse.setTaxes(taxDetailsResponses);
totalTax +=totalLineTax;
totalAmount+=lineItem.amount;

- **[TaxDetailsResponse Methods](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_methods)**  
  Learn more about the available methods with the `TaxDetailsResponse` class.

## TaxDetailsResponse Methods

Learn more about the available methods with the `TaxDetailsResponse` class.

The `TaxDetailsResponse` class includes these
methods.

- **[setCustomTaxAttributes(customTaxAttributes)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setCustomTaxAttributes)**  
  Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax response at the tax line item level.
- **[setExemptAmount(exemptAmount)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setExemptAmount)**  
  Sets the ExemptAmount field of the `TaxDetailsResponse` class.
- **[setExemptReason(reason)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setExemptReason)**  
  Sets the ExemptReason field of the `TaxDetailsResponse` class.
- **[setImposition(imposition)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setImposition)**  
  Sets the Imposition field of the `TaxDetailsResponse` class using an instance of the `ImpositionResponse` class.
- **[setJurisdiction(jurisdiction)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setJurisdiction)**  
  Sets the Jurisdiction field of the `TaxDetailsResponse` using an instance of the `JurisdictionResponse` class.
- **[setRate(rate)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setRate)**  
  Sets the Rate field of the `TaxDetailsResponse` class.
- **[setSerCode(serCode)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setSerCode)**  
  Sets the Service Code field of the `TaxDetailsResponse` class.
- **[setTax(tax)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTax)**  
  Sets the Tax field of the `TaxDetailsResponse` class.
- **[setTaxAuthorityTypeId(taxAuthorityTypeId)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTaxAuthorityTypeId)**  
  Sets the TaxAuthorityTypeId field of the `TaxDetailsResponse` class.
- **[setTaxId(taxId)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTaxId)**  
  Sets the TaxId field of the `TaxDetailsResponse` class.
- **[setTaxRegionId(taxRegionId)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTaxRegionId)**  
  Sets the TaxRegionId field on the `TaxDetailsResponse` class.
- **[setTaxRuleDetails(taxRuleDetails)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTaxRuleDetails)**  
  Sets the TaxRuleDetails field of the `TaxDetailsResponse` class.
- **[setTaxableAmount(taxableAmount)](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_commercetax_TaxDetailsResponse_setTaxableAmount)**  
  Sets the TaxableAmount field of the `TaxDetailsResponse class`.

### setCustomTaxAttributes(customTaxAttributes)

Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax
response at the tax line item level.

#### Signature

`global void
setCustomTaxAttributes(commercetax.CustomTaxAttributesResponse
customTaxAttributes)`

#### Parameters

customTaxAttributes
:   Type: [CustomTaxAttributesResponse](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_class_commercetax_CustomTaxAttributesResponse "Sets additional data or custom attributes in the tax response.")
:   Additional data or custom attributes to include in the tax response.

#### Return Value

Type: void

### setExemptAmount(exemptAmount)

Sets the ExemptAmount field of the `TaxDetailsResponse` class.

#### Signature

`global void
setExemptAmount(Double
exemptAmount)`

#### Parameters

exemptAmount
:   Type: Double
:   Amount of tax on a line item that is exempt from tax calculation.

#### Return Value

Type: void

### setExemptReason(reason)

Sets the ExemptReason field of the `TaxDetailsResponse` class.

#### Signature

`global void
setExemptReason(String
reason)`

#### Parameters

reason
:   Type: String
:   Optional user-defined information on why a tax exemption applies to a line item.

#### Return Value

Type: void

### setImposition(imposition)

Sets the Imposition field of the `TaxDetailsResponse` class using an instance of the `ImpositionResponse` class.

#### Signature

`global void setImposition(commercetax.ImpositionResponse
imposition)`

#### Parameters

imposition
:   Type: [ImpositionResponse](./apex_class_commercetax_ImpositionResponse.htm.md#apex_class_commercetax_ImpositionResponse "Stores details of tax impositions from the external tax engine.")
:   Contains information about why tax was imposed on a line item.

#### Return Value

Type: void

### setJurisdiction(jurisdiction)

Sets the Jurisdiction field of the `TaxDetailsResponse` using an instance of the `JurisdictionResponse` class.

#### Signature

`global void setJurisdiction(commercetax.JurisdictionResponse
jurisdiction)`

#### Parameters

jurisdiction
:   Type: [JurisdictionResponse](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_class_commercetax_JurisdictionResponse "Stores details from the external tax engine about the tax jurisdiction used in the tax calculation process. A tax jurisdiction represents a government entity that collects tax.")
:   Contains address information about the tax jurisdiction used in the tax calculation
    process.

#### Return Value

Type: void

### setRate(rate)

Sets the Rate field of the `TaxDetailsResponse` class.

#### Signature

`global void
setRate(Double
rate)`

#### Parameters

rate
:   Type: Double
:   Tax used during tax calculation. This value is often a decimal amount, such as 0.1 or
    0.06, based on the applied tax percentage.

#### Return Value

Type: void

### setSerCode(serCode)

Sets the Service Code field of the `TaxDetailsResponse` class.

#### Signature

`global void
setSerCode(String
serCode)`

#### Parameters

serCode
:   Type: String
:   Service code used in tax calculation.

#### Return Value

Type: void

### setTax(tax)

Sets the Tax field of the `TaxDetailsResponse` class.

#### Signature

`global void
setTax(Double
tax)`

#### Parameters

tax
:   Type: Double
:   Amount of tax for a line item.

#### Return Value

Type: void

### setTaxAuthorityTypeId(taxAuthorityTypeId)

Sets the TaxAuthorityTypeId field of the `TaxDetailsResponse` class.

#### Signature

`global void
setTaxAuthorityTypeId(String
taxAuthorityTypeId)`

#### Parameters

taxAuthorityTypeId
:   Type: String
:   ID of the organization that oversees tax collection.

#### Return Value

Type: void

### setTaxId(taxId)

Sets the TaxId field of the `TaxDetailsResponse` class.

#### Signature

`global void
setTaxId(String
taxId)`

#### Parameters

taxId
:   Type: String
:   ID value used to determine the tax for an individual or business.

#### Return Value

Type: void

### setTaxRegionId(taxRegionId)

Sets the TaxRegionId field on the `TaxDetailsResponse` class.

#### Signature

`global void
setTaxRegionId(String
taxRegionId)`

#### Parameters

taxRegionId
:   Type: String
:   ID of the tax region used in tax calculation. A tax region represents a geographical
    area where tax is applied.

#### Return Value

Type: void

### setTaxRuleDetails(taxRuleDetails)

Sets the
TaxRuleDetails
field of the `TaxDetailsResponse` class.

#### Signature

`global void setTaxRuleDetails(commercetax.RuleDetailsResponse
taxRuleDetails)`

#### Parameters

taxRuleDetails
:   Type: [RuleDetailsResponse](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_class_commercetax_RuleDetailsResponse "Contains details about the tax rules used for tax calculation.")
:   Information about the Salesforce tax rules used during tax calculation.

#### Return Value

Type: void

### setTaxableAmount(taxableAmount)

Sets the TaxableAmount field of the `TaxDetailsResponse class`.

#### Signature

`global void
setTaxableAmount(Double
taxableAmount)`

#### Parameters

taxableAmount
:   Type: Double
:   Amount that can be taxed on a line item.

#### Return Value

Type: void
