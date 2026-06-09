---
page_id: apex_namespace_commercetax.htm
title: CommerceTax Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_commercetax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_apex_reference.htm
fetched_at: 2026-06-09
---

# CommerceTax Namespace

Manage the communication between Salesforce and an external tax engine.

The `CommerceTax` namespace includes these classes.

- **[AbstractTransactionResponse Class](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_class_commercetax_AbstractTransactionResponse)**  
  Abstract class that contains methods for setting tax fields based on the external tax provider's response. Response classes that extend `AbstractTransactionResponse` inherit these methods.
- **[AddressesResponse Class](./apex_class_commercetax_AddressesResponse.htm.md#apex_class_commercetax_AddressesResponse)**  
  Sets the tax address fields based on a response from the external tax engine. Contains setter methods for the Ship From, Ship To, and Sold To addresses.
- **[AddressResponse Class](./apex_class_commercetax_AddressResponse.htm.md#apex_class_commercetax_AddressResponse)**  
  Contains a location code sent from the external tax engine.
- **[AmountDetailsResponse Class](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_class_commercetax_AmountDetailsResponse)**  
  Sets tax amount fields based on a response from the external tax engine.
- **[CalculateTaxRequest Class](./apex_class_commercetax_CalculateTaxRequest.htm.md#apex_class_commercetax_CalculateTaxRequest)**  
  Represents a request to an external tax engine to calculate tax. Extends the TaxTransactionRequest class and is the top-level request class.
- **[CalculateTaxResponse Class](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_class_commercetax_CalculateTaxResponse)**  
  Sets the values of the tax transaction following a response from the external tax engine. Extends the AbstractTransactionResponse class and is the top-level response class.
- **[CalculateTaxType Enum](./apex_enum_commercetax_CalculateTaxType.htm.md)**  
  Shows whether a tax calculation request is for estimated or actual tax.
- **[CustomTaxAttributesResponse Class](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_class_commercetax_CustomTaxAttributesResponse)**  
  Sets additional data or custom attributes in the tax response.
- **[ErrorResponse Class](./apex_class_commercetax_ErrorResponse.htm.md#apex_class_commercetax_ErrorResponse)**  
  Use to respond with an error after receiving errors from the PaymentGatewayAdapter methods of the [CommercePayments](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_namespace_commercepayments.htm "HTML (New Window)") namespace, such as request-forbidden responses, custom validation errors, or expired API tokens.
- **[HeaderTaxAddressesRequest Class](./apex_class_commercetax_HeaderTaxAddressesRequest.htm.md#apex_class_commercetax_HeaderTaxAddressesRequest)**  
  Captures the address values that are applicable for the quote or order transaction.
- **[ImpositionResponse Class](./apex_class_commercetax_ImpositionResponse.htm.md#apex_class_commercetax_ImpositionResponse)**  
  Stores details of tax impositions from the external tax engine.
- **[JurisdictionResponse Class](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_class_commercetax_JurisdictionResponse)**  
  Stores details from the external tax engine about the tax jurisdiction used in the tax calculation process. A tax jurisdiction represents a government entity that collects tax.
- **[LineItemResponse Class](./apex_class_commercetax_LineItemResponse.htm.md#apex_class_commercetax_LineItemResponse)**  
  Response class that stores details of a list of one or more line items on which the tax engine has calculated tax.
- **[LineTaxAddressesRequest Class](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_class_commercetax_LineTaxAddressesRequest)**  
  Stores details of the addresses applied per line item in a tax calculation request.
- **[RequestType Enum](./apex_enum_commercetax_RequestType.htm.md)**  
  Shows the type of tax request made to the tax engine.
- **[ResultCode Enum](./apex_enum_commercetax_ResultCode.htm.md)**  
  Code that represents the results of a tax request made to the tax engine.
- **[RuleDetailsResponse Class](./apex_class_commercetax_RuleDetailsResponse.htm.md#apex_class_commercetax_RuleDetailsResponse)**  
  Contains details about the tax rules used for tax calculation.
- **[TaxAddressesRequest Class](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest)**  
  Contains methods to get and set tax address values.
- **[TaxAddressRequest Class](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest)**  
  Contains address details used for tax calculation.
- **[TaxApiException Class](./apex_class_commercetax_TaxApiException.htm.md#apex_class_commercetax_TaxApiException)**  
  Contains details about any exceptions during the tax calculation process. Extends the `ApexBaseException` class.
- **[TaxCustomerDetailsRequest Class](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_class_commercetax_TaxCustomerDetailsRequest)**  
  Contains customer details used in tax calculation.
- **[TaxDetailsResponse Class](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_class_commercetax_TaxDetailsResponse)**  
  Stores details of the tax values that an external tax engine calculates in response to a tax calculation request.
- **[TaxEngineAdapter Interface](./apex_interface_commercetax_TaxEngineAdapter.htm.md#apex_interface_commercetax_TaxEngineAdapter)**  
  Retrieves information from the tax engine and evaluates the information to define tax details.
- **[TaxEngineContext Class](./apex_class_commercetax_TaxEngineContext.htm.md#apex_class_commercetax_TaxEngineContext)**  
  Wrapper class that stores details about the type of a tax calculation request.
- **[TaxLineItemRequest Class](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_class_commercetax_TaxLineItemRequest)**  
  Contains line item details of a tax request.
- **[TaxSellerDetailsRequest Class](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_class_commercetax_TaxSellerDetailsRequest)**  
  Contains tax code details used in the tax calculation request.
- **[TaxTransactionRequest Class](./apex_class_commercetax_TaxTransactionRequest.htm.md#apex_class_commercetax_TaxTransactionRequest)**  
  Abstract class for storing customer details used in tax calculation and estimation requests.
- **[TaxTransactionStatus Enum](./apex_enum_commercetax_TaxTransactionStatus.htm.md)**  
  Shows whether the tax transaction has been committed or uncommitted.
- **[TaxTransactionType Enum](./apex_enum_commercetax_TaxTransactionType.htm.md)**  
  Shows whether the tax transaction is for a credit or debit transaction.
