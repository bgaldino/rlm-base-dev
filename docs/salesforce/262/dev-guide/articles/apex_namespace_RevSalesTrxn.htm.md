---
page_id: apex_namespace_RevSalesTrxn.htm
title: RevSalesTrxn Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_RevSalesTrxn.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_apex_reference.htm
fetched_at: 2026-06-09
---

# RevSalesTrxn Namespace

Create a sales transaction, such as a quote or an order, with integrated
pricing and configuration. Additionally, update an order or a quote, and insert and delete
order or quote line items to calculate the estimated tax.

The `RevSalesTrxn` namespace includes these classes.

- **[CatalogRatesPreferenceEnum Enum](./apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm.md)**  
  Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.
- **[ConfigurationExecutionEnum Enum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md)**  
  Specifies the configuration method for the place sales transaction request.
- **[ConfigurationOptionsInput Class](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md)**  
  Contains methods and properties to set the configuration options for the input to the product configurator.
- **[GraphRequest Class](./apex_class_RevSalesTrxn_GraphRequest.htm.md)**  
  Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.
- **[GroupRampActionEnum Enum](./apex_enum_RevSalesTrxn_GroupRampActionEnum.htm.md)**  
  Specifies the action ‌that you want to perform on group ramp segments. Additionally, you can also convert a non-ramped group into a ramped group.
- **[PersistPreferenceEnum Enum](./apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm.md)**  
  Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.
- **[PlaceSalesTransactionException Class](./apex_class_RevSalesTrxn_PlaceSalesTransactionException.htm.md)**  
  Contains methods to hold the exception details for the place sales transaction request.
- **[PlaceSalesTransactionExecutor Class](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md)**  
  Contains methods to place a sales transaction with details of the graph request, pricing preferences, and configuration options.
- **[PlaceSalesTransactionResponse Class](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md)**  
  Contains properties to hold the response to the place sales transaction request.
- **[PricingPreferenceEnum Enum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md)**  
  Specifies the pricing preference during the creation of a sales transaction.
- **[RecordResource Class](./apex_class_RevSalesTrxn_RecordResource.htm.md)**  
  Contains constructors and properties to create a record object from the field values of a sales transaction.
- **[RecordWithReferenceRequest Class](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md)**  
  Contains constructors and properties to associate a record object with a reference identifier.
- **[TaxPreferenceEnum Enum](./apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm.md)**  
  Specifies whether to execute or skip the tax calculation step for each sales transaction record. Available in API version 65.0 and later.
