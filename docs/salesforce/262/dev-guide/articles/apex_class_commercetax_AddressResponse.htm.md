---
page_id: apex_class_commercetax_AddressResponse.htm
title: AddressResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AddressResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# AddressResponse Class

Contains a location code sent from the external tax
engine.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

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

- **[AddressResponse Methods](./apex_class_commercetax_AddressResponse.htm.md#apex_commercetax_AddressResponse_methods)**  
  Learn more about the available methods with the `AddressResponse` class.

## AddressResponse Methods

Learn more about the available methods with the `AddressResponse` class.

The `AddressResponse` class includes these
methods.

- **[setLocationCode(locationCode)](./apex_class_commercetax_AddressResponse.htm.md#apex_commercetax_AddressResponse_setLocationCode)**  
  Sets the value of a LocationCode field.

### setLocationCode(locationCode)

Sets the value of a LocationCode field.

#### Signature

`global void
setLocationCode(String
locationCode)`

#### Parameters

locationCode
:   Type: String
:   A code that contains address information. This value can be passed to a
    method
    that sets the value of an address field.

#### Return Value

Type: void
