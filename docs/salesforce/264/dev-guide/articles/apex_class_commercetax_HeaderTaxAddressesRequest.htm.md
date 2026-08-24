---
page_id: apex_class_commercetax_HeaderTaxAddressesRequest.htm
title: HeaderTaxAddressesRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_HeaderTaxAddressesRequest.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

  

# HeaderTaxAddressesRequest Class

  
  
  
Captures the address values that are applicable for the quote or
      order transaction.

    

## Namespace

      
      

[CommerceTax](./apex_namespace_commercetax.htm.md)

    

    
    
    
    
  

- 
**[HeaderTaxAddressesRequest Constructors](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_constructors)**  

Learn more about the constructors available with the `HeaderTaxAddressesRequest` class.

- 
**[HeaderTaxAddressesRequest Properties](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_properties)**  

Learn more about the available properties with the `HeaderTaxAddressesRequest` class.

- 
**[HeaderTaxAddressesRequest Methods](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_methods)**  

Learn more about the available methods with the `HeaderTaxAddressesRequest` class.

  

## HeaderTaxAddressesRequest Constructors

  
  
  
Learn more about the constructors available with the `HeaderTaxAddressesRequest` class.

    
      

The `HeaderTaxAddressesRequest` class includes these
        constructors.

    

    
  

- 
**[HeaderTaxAddressesRequest(shipFrom, shipTo, soldTo, billTo, taxEngineAddress)](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_ctor)**  

Constructor for initializing the required addresses of the tax             addresses request such as the ship from, ship to, sold to, and bill to addresses. This             constructor is intended for test usage and throws an exception if used outside of the             Apex test context.

    

### HeaderTaxAddressesRequest(shipFrom, shipTo, soldTo,
            billTo, taxEngineAddress)

    
    
    
Constructor for initializing the required addresses of the tax
            addresses request such as the ship from, ship to, sold to, and bill to addresses. This
            constructor is intended for test usage and throws an exception if used outside of the
            Apex test context.

        

#### Signature

`global HeaderTaxAddressesRequest(commercetax.TaxAddressRequest
                    shipFrom, commercetax.TaxAddressRequest shipTo, commercetax.TaxAddressRequest
                    soldTo, commercetax.TaxAddressRequest billTo, commercetax.TaxAddressRequest
                    taxEngineAddress)`

        

#### Parameters

                
- 
**shipFrom**:

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

Address where a line item was shipped from.

                
- 
**shipTo**:

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

Address where a line item was shipped to.

                
- 
**soldTo**:

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

Address of the line item's buyer.

                
- 
**billTo**:

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

Person or group who was billed

for the line item.

                
- 
**taxEngineAddress**:

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

Address that the tax engine uses to calculate tax.

            

    

  

## HeaderTaxAddressesRequest Properties

  
  
  
Learn more about the available properties with the `HeaderTaxAddressesRequest` class.

    
      

The `HeaderTaxAddressesRequest` class includes these
        properties.

    

    
  

- 
**[billTo](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_billTo)**  

Specifies the billTo address for a       line       item on which tax was calculated.

- 
**[shipFrom](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_shipFrom)**  

Specifies the shipFrom address for a line       item       on which tax was calculated.

- 
**[shipTo](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_shipTo)**  

Specifies the shipTo address for a line       item       on which tax was calculated.

- 
**[soldTo](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_soldTo)**  

Specifies the soldTo address for a line       item       on which tax was calculated.

- 
**[taxEngineAddress](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_taxEngineAddress)**  

Address used by the tax engine when calculating tax for       a       line item.

  

### billTo

  
  
  
Specifies the billTo address for a
      line
      item on which tax was calculated.

    

#### Signature

`global commercetax.TaxAddressRequest billTo {get;
        set;}`

    

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

  

  

### shipFrom

  
  
  
Specifies the shipFrom address for a line
      item
      on which tax was calculated.

    

#### Signature

`global commercetax.TaxAddressRequest shipFrom {get;
        set;}`

    

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

  

  

### shipTo

  
  
  
Specifies the shipTo address for a line
      item
      on which tax was calculated.

    

#### Signature

`global commercetax.TaxAddressRequest shipTo {get;
        set;}`

    

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

  

  

### soldTo

  
  
  
Specifies the soldTo address for a line
      item
      on which tax was calculated.

    

#### Signature

`global commercetax.TaxAddressRequest soldTo {get;
        set;}`

    

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

  

  

### taxEngineAddress

  
  
  
Address used by the tax engine when calculating tax for
      a
      line item.

    

#### Signature

`global commercetax.TaxAddressRequest taxEngineAddress {get;
          set;}`

    

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)

  

  

## HeaderTaxAddressesRequest Methods

  
  
  
Learn more about the available methods with the `HeaderTaxAddressesRequest` class.

    
      

The `HeaderTaxAddressesRequest` class includes these
        methods.

    

    
  

- 
**[equals(obj)](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_equals)**  

Maintains the integrity of lists of type `HeaderTaxAddressesRequest` by determining the equality of external objects in a       list. This method is dynamic and is based on the `equals()`       method in Java.

- 
**[hashCode()](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_hashCode)**  

Maintains the integrity of lists of type `TaxAddressesRequest` by determining the uniqueness of the external objects in a       list.

- 
**[toString()](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_commercetax_HeaderTaxAddressesRequest_toString)**  

Converts a value to a string.

  

### equals(obj)

  
  
  
Maintains the integrity of lists of type `HeaderTaxAddressesRequest` by determining the equality of external objects in a
      list. This method is dynamic and is based on the `equals()`
      method in Java.

    

#### Signature

`global Boolean
          equals(Object
      obj)`

    

#### Parameters

        
- 
**obj**:

Type: 

Object External object
            whose
            key is to be validated.

      

    

#### Return Value

      
      

Type: Boolean

    

  

  

### hashCode()

  
  
  
Maintains the integrity of lists of type `TaxAddressesRequest` by determining the uniqueness of the external objects in a
      list.

    

#### Signature

`global Integer
          hashCode()`

    

#### Return Value

Type: Integer

  

  

### toString()

  
  
  
Converts a value to a string.

    

#### Signature

`global String
          toString()`

    

#### Return Value

Type: String
