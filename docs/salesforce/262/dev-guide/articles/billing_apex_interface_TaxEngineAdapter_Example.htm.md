---
page_id: billing_apex_interface_TaxEngineAdapter_Example.htm
title: TaxEngineAdapter Example Implementation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_apex_interface_TaxEngineAdapter_Example.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_tax_engine_adapter_interface_for_standard_tax.htm
fetched_at: 2026-06-09
---

# TaxEngineAdapter Example Implementation

Refer to the example implementation of the `TaxEngineAdapter` interface to accept information from a tax engine and
evaluate the information to define tax details.

## Namespace

See [commercetax](./apex_namespace_commercetax.htm.md "HTML (New Window)")
namespace to view the list of available classes.

## Usage

The `TaxEngineAdapter` interface accepts information
from the tax engine through the `TaxEngineContext`
class. The interface evaluates the information to define tax in the response with
details, such as tax amount and addresses. The response is used to update and create
entities in the Salesforce org.

## Considerations

From Winter ’26, the available state and country
values from orgs that are configured with [State and Country/Territory Picklists](https://help.salesforce.com/s/articleView?id=xcloud.admin_state_country_picklists_configure.htm&language=en_US) are
also supported.

## Example

Use these steps to build a sample tax adapter implementation. Each tax adapter
implementation varies based on your implementation requirements. Customize this
example to suit your business requirements.

See [Tax Engine Reference
Gateway Adapter](https://github.com/salesforce-misc/salesforce-tax-engine-reference-gateway-adapters "HTML (New Window)") for reference implementations of a tax engine
adapter.

- Get the tax rates from the created custom object. See [TaxEngineAdapter
  Interface](./billing_tax_engine_adapter_interface_for_standard_tax.htm.md "Retrieves and evaluates the details from a tax engine to define tax details.").
- The custom adapter class implements the `TaxEngineAdapter` interface. The `processRequest` method takes an instance of `TaxEngineContext` class and returns a response
  with the calculated tax details through the `TaxDetailsResponse` class or an error response through the
  `ErrorResponse` class.

  ```
  global virtual class StandardTaxAdapter implements commercetax.TaxEngineAdapter {
      global commercetax.TaxEngineResponse processRequest(commercetax.TaxEngineContext taxEngineContext) {
          commercetax.RequestType requestType = taxEngineContext.getRequestType();

          // Map of tax field name to the value of the corresponding entity field (EntityFieldName) at header level
          Map<String, Object> customTaxAttributeHeaderLevelMap = new Map<String, Object>();
          // Map of tax field name to the value of the corresponding entity field (EntityFieldName) at line level
          Map<String, Object> customTaxAttributeLineLevelMap = new Map<String, Object>();
          // Map of tax field name to the value of the corresponding entity field (EntityFieldName) at line tax level
          Map<String, Object> customTaxAttributeLineTaxLevelMap = new Map<String, Object>();

          commercetax.CustomTaxAttributesResponse customTaxAttributeHeaderLevelResponse = new commercetax.CustomTaxAttributesResponse();
          commercetax.CustomTaxAttributesResponse customTaxAttributeLineLevelResponse = new commercetax.CustomTaxAttributesResponse();
          commercetax.CustomTaxAttributesResponse customTaxAttributeLineTaxLevelResponse = new commercetax.CustomTaxAttributesResponse();

          customTaxAttributeHeaderLevelResponse.setData(customTaxAttributeHeaderLevelMap);
          customTaxAttributeLineLevelResponse.setData(customTaxAttributeLineLevelMap);
          customTaxAttributeLineTaxLevelResponse.setData(customTaxAttributeLineTaxLevelMap);

          commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest) taxEngineContext.getRequest();
          if (request.documentCode == null) {
              return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '404', 'documentCode  is mandatory');
          }
          if (request.documentCode == 'TaxEngineError') {
              return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '504', 'documentCode  - not supported');
          }
          if (request.documentCode == 'simulateUnhandledExceptionInAdapter') {
              Integer foo = 5 / 0;
          }
          if (request.documentCode == 'simulateValidationFailureInAdapter') {
              return new commercetax.ErrorResponse(
                  commercetax.resultcode.TaxEngineError,
                  '400',
                  'validations for documentCode failed in adapter'
              );
          }
          if (request.documentCode == 'simulateMalformedErrorInAdapter') {
              return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, null, 'malformed adapter error response');
          }
          if (request.documentCode == 'simulateTaxEngineProcessFailure') {
              return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '500', 'Tax Engine couldnt process your request');
          }
          if (request.documentCode == 'simulateReferenceDocumentCodeMissing') {
              return new commercetax.ErrorResponse(commercetax.resultcode.ReferenceDocumentCodeMissing, '400', 'Ref Document Code not found');
          }

          if (requestType == commercetax.RequestType.CalculateTax) {
              commercetax.calculatetaxtype type = request.taxtype;
              String docCode = '';
              if (request.DocumentCode == 'simulateEmptyDocumentCode')
                  docCode = '';
              else if (request.DocumentCode != null)
                  docCode = request.DocumentCode;
              else if (request.ReferenceEntityId != null)
                  docCode = request.ReferenceEntityId;
              else
                  docCode = String.valueOf(getRandomInteger(0, 2147483647));
              commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
              response.setCustomTaxAttributes(customTaxAttributeHeaderLevelResponse);
              if (request.isCommit == true) {
                  response.setStatus(commercetax.TaxTransactionStatus.Committed);
              } else {
                  response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
              }

              if (request.shouldVoidTax) {
                  if (request.documentCode.startsWith('simulateCalculateWhenRefDocIsLocked')) {
                      response.setDocumentCode(docCode);
                      response.setReferenceDocumentCode(request.referenceDocumentCode);
                      if (request.taxTransactionType == null) {
                          response.setTaxTransactionType(commercetax.TaxTransactionType.Debit);
                      } else {
                          response.setTaxTransactionType(request.taxTransactionType);
                      }
                  } else if (request.documentCode.startsWith('simulateRandomRefDocumentCode')) {
                      response.setDocumentCode(docCode);
                      response.setReferenceDocumentCode('simulateRandomRefDocumentCode2');
                      response.setTaxTransactionType(request.taxTransactionType);
                  } else if (request.documentCode.startsWith('simulateRandomCode')) {
                      response.setDocumentCode('simulateRandomCode2');
                      response.setReferenceDocumentCode(null);
                      response.setTaxTransactionType(commercetax.TaxTransactionType.Void);
                  } else {
                      response.setDocumentCode(request.referenceDocumentCode);
                      response.setReferenceDocumentCode(null);
                      response.setTaxTransactionType(commercetax.TaxTransactionType.Void);
                  }
              } else {
                  response.setDocumentCode(docCode);
                  response.setReferenceDocumentCode(request.referenceDocumentCode);

                  if (request.taxTransactionType == null) {
                      response.setTaxTransactionType(commercetax.TaxTransactionType.Debit);
                  } else {
                      response.setTaxTransactionType(request.taxTransactionType);
                  }
              }

              response.setTaxType(type);
              response.setStatusDescription('statusDescription');
              if (request.sellerDetails.code == 'testSellerCode') {
                  response.setDescription('SellerCode fetched from TaxEngine entity');
              } else {
                  response.setDescription('description');
              }
              response.setEffectiveDate(system.now());
              if (request.transactionDate == null) {
                  response.setTransactionDate(system.now());
              } else {
                  response.setTransactionDate(request.transactionDate);
              }

              if (request.currencyIsoCode == null || request.currencyIsoCode == '') {
                  response.setCurrencyIsoCode('USD');
              } else {
                  response.setCurrencyIsoCode(request.currencyIsoCode);
              }
              response.setReferenceEntityId(request.ReferenceEntityId);
              Double totalTax = 0.0;
              Double totalAmount = 0.0;
              Map<String, Double> countryTaxRateMap = getTaxes(request.lineItems);
              List<commercetax.LineItemResponse> lineItemResponses = new List<commercetax.LineItemResponse>();
              for (Commercetax.TaxLineItemRequest lineItem : request.lineItems) {
                  String country = getCountryFromLineItem(lineItem);
                  if (country == null) {
                      return new commercetax.ErrorResponse(
                          commercetax.resultcode.TaxEngineError,
                          '400',
                          'Country is mandatory for each line item'
                      );
                  }

                  Double taxRate = countryTaxRateMap.get(country);
                  if (taxRate == null) {
                      return new commercetax.ErrorResponse(
                          commercetax.resultcode.TaxEngineError,
                          '404',
                          'No tax rate found for the specified country: ' + country
                      );
                  }
                  commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();
                  if (request.DocumentCode == 'SetsNullForResponseWithoutException') {
                      addressesRes.setShipFrom(null);
                      addressesRes.setShipTO(null);
                      addressesRes.setSoldTo(null);
                  } else {
                      setAddresses(addressesRes, lineItem);
                      //System.debug('Line item addresses: ' + addressesRes);
                  }
                  //System.debug('ProductSKU: ' + lineItem.productSKU);
                  //System.debug('ReferenceDocumentCode: ' + lineItem.referenceDocumentCode);
                  commercetax.LineItemResponse lineItemResponse = new commercetax.LineItemResponse();
                  lineItemResponse.setCustomTaxAttributes(customTaxAttributeLineLevelResponse);
                  Double totalLineTax = 0;
                  List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
                  for (integer i = 0; i < 1; i++) {
                      Integer rate = 1;
                      Double taxableAmount = lineItem.amount;
                      commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
                      taxDetailsResponse.setRate(Double.valueOf(rate));
                      taxDetailsResponse.setTaxableAmount(taxableAmount);
                      Double tax = taxableAmount * rate;
                      totalLineTax += tax;
                      taxDetailsResponse.setTax(taxableAmount * rate);
                      taxDetailsResponse.setExemptAmount(0);
                      taxDetailsResponse.setExemptReason('exemptReason');
                      taxDetailsResponse.setTaxRegionId('taxRegionId');
                      taxDetailsResponse.setTaxId(String.valueOf(getRandomInteger(0, 2323233)));
                      taxDetailsResponse.setSerCode('serCode');
                      taxDetailsResponse.setCustomTaxAttributes(customTaxAttributeLineTaxLevelResponse);
                      taxDetailsResponse.setTaxAuthorityTypeId('taxAuthorityTypeId');
                      if (request.DocumentCode == 'SetsNullForResponseWithoutException') {
                          taxDetailsResponse.setImposition(null);
                      } else {
                          commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
                          imposition.setSubType('subtype');
                          imposition.setType('type');
                          taxDetailsResponse.setImposition(imposition);
                      }

                      if (request.DocumentCode == 'SetsNullForResponseWithoutException') {
                          taxDetailsResponse.setJurisdiction(null);
                      } else {
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
                  totalTax += totalLineTax;
                  totalAmount += lineItem.amount;

                  if (request.DocumentCode == 'SetsNullForResponseWithException') {
                      lineItemResponse.setAmountDetails(null);
                  } else {
                      commercetax.AmountDetailsResponse amountResponse = new commercetax.AmountDetailsResponse();
                      amountResponse.setTotalAmountWithTax(totalTax + totalAmount);
                      amountResponse.setExemptAmount(0);
                      amountResponse.setTotalAmount(totalAmount);
                      amountResponse.setTaxAmount(totalTax);
                      lineItemResponse.setAmountDetails(amountResponse);
                  }
                  lineItemResponse.setEffectiveDate(system.now());
                  lineItemResponse.setTaxCode(lineItem.taxCode);
                  lineItemResponse.setProductCode(lineItem.ProductCode);
                  lineItemResponse.setLineNumber(lineItem.linenumber);
                  lineItemResponse.setIsTaxable(true);
                  lineItemResponse.setQuantity(lineItem.quantity);
                  if (request.DocumentCode == 'SetsNullForResponseWithoutException') {
                      lineItemResponse.setAddresses(null);
                  } else {
                      lineItemResponse.setAddresses(addressesRes);
                  }
                  lineItemResponses.add(lineItemResponse);
              }
              if (request.DocumentCode == 'SetsNullForResponseWithException') {
                  lineItemResponses.add(null);
              }
              if (request.documentCode == 'nolines') {
                  // logic to skip adding lines to response
              } else {
                  response.setLineItems(lineItemResponses);
              }
              if (request.DocumentCode == 'SetsNullForResponseWithException') {
                  response.setAmountDetails(null);
              } else {
                  commercetax.AmountDetailsResponse headerAmountResponse = new commercetax.AmountDetailsResponse();
                  headerAmountResponse.setTotalAmountWithTax(totalTax + totalAmount);
                  headerAmountResponse.setExemptAmount(0);
                  headerAmountResponse.setTotalAmount(totalAmount);
                  headerAmountResponse.setTaxAmount(totalTax);
                  response.setAmountDetails(headerAmountResponse);
              }
              commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();
              commercetax.AddressResponse addRes = new commercetax.AddressResponse();
              addRes.setLocationCode('street, city, state, country, postalCode');
              addressesRes.setShipFrom(addRes);
              addressesRes.setShipTO(addRes);
              addressesRes.setSoldTo(addRes);
              response.setAddresses(addressesRes);
              return response;
          } else
              return null;
      }

      public static Integer getRandomInteger(Integer min, Integer max) {
          return min + (Integer.valueOf(Math.random()) * (max - min));
      }

      // Method to get the tax rates for the line items based on the address country codes
      private Map<String, Double> getTaxes(List<commercetax.TaxLineItemRequest> lineItems) {
          Set<String> countryCodes = new Set<String>();
          // Collecting all unique the country codes
          for (commercetax.TaxLineItemRequest lineItem : lineItems) {
              String country = getCountryFromLineItem(lineItem);
              if (country != null) {
                  countryCodes.add(country);
              }
          }
          // Query tax rates for the unique country codes and store it in a map
          Map<String, Double> countryTaxRateMap = new Map<String, Double>();
          if (!countryCodes.isEmpty()) {
              // Query the tax rate from the custom object based on the country code
              List<CountryTaxRate__c> taxRates = [
                  SELECT Country_Code__c, Tax_Rate__c
                  FROM CountryTaxRate__c
                  WHERE Country_Code__c IN :countryCodes
              ];
              for (CountryTaxRate__c taxRate : taxRates) {
                  countryTaxRateMap.put(taxRate.Country_Code__c, taxRate.Tax_Rate__c);
              }
          }
          return countryTaxRateMap;
      }
      // Method to retrieve the country for the line item
      private String getCountryFromLineItem(commercetax.TaxLineItemRequest lineItem) {
          if (lineItem.addresses != null) {
              commercetax.TaxAddressRequest addressRequest = lineItem.addresses.shipTo;
              if (addressRequest != null && addressRequest.country != null) {
                  return addressRequest.country;
              }
          }
          return null;
      }

      // Method to set addresses in the line item response
      private void setAddresses(commercetax.AddressesResponse addressesRes, Commercetax.TaxLineItemRequest lineItem) {
          commercetax.LineTaxAddressesRequest addressesReq = lineItem.addresses;
          if (addressesReq == null) {
              return;
          }
          addressesRes.setShipFrom(getShipFromAddressRes(addressesReq));
          addressesRes.setShipTo(getShipToAddressRes(addressesReq));
          addressesRes.setSoldTo(getSoldToAddressRes(addressesReq));
      }

      private commercetax.AddressResponse getShipFromAddressRes(commercetax.LineTaxAddressesRequest addressesReq) {
          return getAddressRes(addressesReq.shipFrom);
      }

      private commercetax.AddressResponse getShipToAddressRes(commercetax.LineTaxAddressesRequest addressesReq) {
          return getAddressRes(addressesReq.shipTo);
      }

      private commercetax.AddressResponse getSoldToAddressRes(commercetax.LineTaxAddressesRequest addressesReq) {
          if (addressesReq.soldTo != null) {
              return getAddressRes(addressesReq.soldTo);
          } else {
              return getAddressRes(addressesReq.billTo);
          }
      }

      private commercetax.AddressResponse getAddressRes(commercetax.TaxAddressRequest addressReq) {
          if (addressReq == null) {
              return null;
          }

          commercetax.AddressResponse addressRes = new commercetax.AddressResponse();

          List<String> addressEle = new List<String>();
          if (addressReq.street != null)
              addressEle.add(addressReq.street);
          if (addressReq.city != null)
              addressEle.add(addressReq.city);
          if (addressReq.state != null)
              addressEle.add(addressReq.state);
          if (addressReq.country != null)
              addressEle.add(addressReq.country);
          if (addressReq.postalCode != null)
              addressEle.add(addressReq.postalCode);

          addressRes.setLocationCode(String.join(addressEle, ', '));
          return addressRes;
      }
  }
  ```
- Select `StandardTaxAdapter` as the provider
  when you create a tax engine record in your org.
