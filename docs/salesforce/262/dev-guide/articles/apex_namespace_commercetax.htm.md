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

- **[AbstractTransactionResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AbstractTransactionResponse.htm)**  
  Abstract class that contains methods for setting tax fields based on the external tax provider's response. Response classes that extend `AbstractTransactionResponse` inherit these methods.
- **[AddressesResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AddressesResponse.htm)**  
  Sets the tax address fields based on a response from the external tax engine. Contains setter methods for the Ship From, Ship To, and Sold To addresses.
- **[AddressResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AddressResponse.htm)**  
  Contains a location code sent from the external tax engine.
- **[AmountDetailsResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AmountDetailsResponse.htm)**  
  Sets tax amount fields based on a response from the external tax engine.
- **[CalculateTaxRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CalculateTaxRequest.htm)**  
  Represents a request to an external tax engine to calculate tax. Extends the TaxTransactionRequest class and is the top-level request class.
- **[CalculateTaxResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CalculateTaxResponse.htm)**  
  Sets the values of the tax transaction following a response from the external tax engine. Extends the AbstractTransactionResponse class and is the top-level response class.
- **[CalculateTaxType Enum](./apex_enum_commercetax_CalculateTaxType.htm.md)**  
  Shows whether a tax calculation request is for estimated or actual tax.
- **[CustomTaxAttributesResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CustomTaxAttributesResponse.htm)**  
  Sets additional data or custom attributes in the tax response.
- **[ErrorResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_ErrorResponse.htm)**  
  Use to respond with an error after receiving errors from the PaymentGatewayAdapter methods of the [CommercePayments](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_namespace_commercepayments.htm "HTML (New Window)") namespace, such as request-forbidden responses, custom validation errors, or expired API tokens.
- **[HeaderTaxAddressesRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_HeaderTaxAddressesRequest.htm)**  
  Captures the address values that are applicable for the quote or order transaction.
- **[ImpositionResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_ImpositionResponse.htm)**  
  Stores details of tax impositions from the external tax engine.
- **[JurisdictionResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_JurisdictionResponse.htm)**  
  Stores details from the external tax engine about the tax jurisdiction used in the tax calculation process. A tax jurisdiction represents a government entity that collects tax.
- **[LineItemResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_LineItemResponse.htm)**  
  Response class that stores details of a list of one or more line items on which the tax engine has calculated tax.
- **[LineTaxAddressesRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_LineTaxAddressesRequest.htm)**  
  Stores details of the addresses applied per line item in a tax calculation request.
- **[RequestType Enum](./apex_enum_commercetax_RequestType.htm.md)**  
  Shows the type of tax request made to the tax engine.
- **[ResultCode Enum](./apex_enum_commercetax_ResultCode.htm.md)**  
  Code that represents the results of a tax request made to the tax engine.
- **[RuleDetailsResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_RuleDetailsResponse.htm)**  
  Contains details about the tax rules used for tax calculation.
- **[TaxAddressesRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxAddressesRequest.htm)**  
  Contains methods to get and set tax address values.
- **[TaxAddressRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxAddressRequest.htm)**  
  Contains address details used for tax calculation.
- **[TaxApiException Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxApiException.htm)**  
  Contains details about any exceptions during the tax calculation process. Extends the `ApexBaseException` class.
- **[TaxCustomerDetailsRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxCustomerDetailsRequest.htm)**  
  Contains customer details used in tax calculation.
- **[TaxDetailsResponse Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxDetailsResponse.htm)**  
  Stores details of the tax values that an external tax engine calculates in response to a tax calculation request.
- **[TaxEngineAdapter Interface](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_interface_commercetax_TaxEngineAdapter.htm)**  
  Retrieves information from the tax engine and evaluates the information to define tax details.
- **[TaxEngineContext Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxEngineContext.htm)**  
  Wrapper class that stores details about the type of a tax calculation request.
- **[TaxLineItemRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxLineItemRequest.htm)**  
  Contains line item details of a tax request.
- **[TaxSellerDetailsRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxSellerDetailsRequest.htm)**  
  Contains tax code details used in the tax calculation request.
- **[TaxTransactionRequest Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxTransactionRequest.htm)**  
  Abstract class for storing customer details used in tax calculation and estimation requests.
- **[TaxTransactionStatus Enum](./apex_enum_commercetax_TaxTransactionStatus.htm.md)**  
  Shows whether the tax transaction has been committed or uncommitted.
- **[TaxTransactionType Enum](./apex_enum_commercetax_TaxTransactionType.htm.md)**  
  Shows whether the tax transaction is for a credit or debit transaction.
