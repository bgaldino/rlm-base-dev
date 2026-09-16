---
page_id: apex_class_commercetax_AddressesResponse.htm
title: AddressesResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AddressesResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

  

# AddressesResponse Class

  
  
  
Sets the tax address fields based on a response from the external
      tax engine. Contains setter methods for the Ship From, Ship To, and Sold To
    addresses.

    

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md)

    

## Usage

Because `AddressesResponse`
      contains multiple addresses, we recommend using multiple instances of `AddressResponse` to set unique values for each address.

    

## Example

      
      

This code sample represents a portion of the code used in a mock tax adapter. In this
        example, you create three `AddressResponse` classes, set
        their location codes, and pass them to the `Ship
        To`, `Ship From`, and
          `Sold To` setter methods in `AddressesResponse`. In an actual implementation, your `AddressResponse` classes already have a location code based on
        the response from the external tax engine.

      

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
**[AddressesResponse Methods](./apex_class_commercetax_AddressesResponse.htm.md#apex_commercetax_AddressesResponse_methods)**  

Learn more about the methods for AddressesResponse class.

  

## AddressesResponse Methods

  
  
  
Learn more about the methods for AddressesResponse class.

    
      

The `AddressesResponse` class includes these
        methods.

    

    
  

- 
**[setShipFrom(shipFrom)](./apex_class_commercetax_AddressesResponse.htm.md#apex_commercetax_AddressesResponse_setShipFrom)**  

Sets the value of a       ShipFrom       address field.

- 
**[setShipTo(shipTo)](./apex_class_commercetax_AddressesResponse.htm.md#apex_commercetax_AddressesResponse_setShipTo)**  

Sets the value of a ShipTo address field.

- 
**[setSoldTo(soldTo)](./apex_class_commercetax_AddressesResponse.htm.md#apex_commercetax_AddressesResponse_setSoldTo)**  

Sets the value of a SoldTo address field.

  

### setShipFrom(shipFrom)

  
  
  
Sets the value of a
      ShipFrom
      address field.

    

#### Signature

`global void setShipFrom(commercetax.AddressResponse
          shipFrom)`

    

#### Parameters

        
- 
**shipFrom**:

Type: [AddressResponse](./apex_class_commercetax_AddressResponse.htm.md#apex_class_commercetax_AddressResponse)

A single address. Use this generic address parameter  to store any type of address,
            such as Ship From, Ship To, and Sold To details. Users set the specific address in an
              `AddressResponse` instance and then pass that
            instance to the `AddressesResponse`’s `setShipTo()`, `setShipFrom()`, and `setSoldTo()` methods as
            needed.

      

    

#### Return Value

Type: void

  

  

### setShipTo(shipTo)

  
  
  
Sets the value of a ShipTo address field.

    

#### Signature

`global void setShipTo(commercetax.AddressResponse
        shipTo)`

    

#### Parameters

        
- 
**shipTo**:

Type: [AddressResponse](./apex_class_commercetax_AddressResponse.htm.md#apex_class_commercetax_AddressResponse)

Stores

a single address. This is a generic address parameter and can be used to store
            any type of address, such as Ship From, Ship To, and Sold To details. Users set the
            specific address in an `AddressResponse` instance and
            then pass that instance to the `AddressesResponse`’s
              `setShipTo()`, `setShipFrom()`, and `setSoldTo()` methods as
            needed.

      

    

#### Return Value

Type: void

  

  

### setSoldTo(soldTo)

  
  
  
Sets the value of a SoldTo address field.

    

#### Signature

`global void setSoldTo(commercetax.AddressResponse
        soldTo)`

    

#### Parameters

        
- 
**soldTo**:

Type: [AddressResponse](./apex_class_commercetax_AddressResponse.htm.md#apex_class_commercetax_AddressResponse)

Stores

a single address. This is a generic address parameter and can be used to store
            any type of address, such as Ship From, Ship To, Sold To details. Users set the specific
            address in an AddressResponse instance and then pass that instance to the `AddressesResponse`’s `setShipTo()`, `setShipFrom()`, and `setSoldTo()` methods as needed.

      

    

#### Return Value

Type: void
