---
page_id: apex_class_commercetax_AddressResponse.htm
title: AddressResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AddressResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

  

# AddressResponse Class

  
  
  
Contains a location code sent from the external tax
    engine.

    

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md)

    

## Usage

      
      

Use the `AddressResponse` class to set unique values for
        each address.

      

```
commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();

//AddressResponse containing ShipTo information
commercetax.AddressResponse shipToAddress = new commercetax.AddressResponse();
shipToAddress.setLocationCode('1234567');

//AddressResponse containing ShipFrom information
commercetax.AddressResponse shipFromAddress = new commercetax.AddressResponse();
shipFromAddress.setLocationCode('84720385');

//AddressResponse containing Sold To information
commercetax.AddressResponse soldToAddress = new commercetax.AddressResponse();
soldToAddress.setLocationCode('92381749');

//set values of addressesRes
addressesRes.setShipFrom(shipFromAddress);
addressesRes.setShipTo(shipToAddress);
addressesRes.setSoldTo(soldToAddress);

```

    

  

- 
**[AddressResponse Methods](./apex_class_commercetax_AddressResponse.htm.md#apex_commercetax_AddressResponse_methods)**  

Learn more about the available methods with the `AddressResponse` class.

  

## AddressResponse Methods

  
  
  
Learn more about the available methods with the `AddressResponse` class.

    
      

The `AddressResponse` class includes these
        methods.

    

    
  

- 
**[setLocationCode(locationCode)](./apex_class_commercetax_AddressResponse.htm.md#apex_commercetax_AddressResponse_setLocationCode)**  

Sets the value of a LocationCode field.

  

### setLocationCode(locationCode)

  
  
  
Sets the value of a LocationCode field.

    

#### Signature

`global void
          setLocationCode(String
      locationCode)`

    

#### Parameters

        
- 
**locationCode**:

Type: String

A code that contains address information. This value can be passed to a
            method
            that sets the value of an address field.

      

    

#### Return Value

Type: void
