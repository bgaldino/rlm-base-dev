---
page_id: apex-namespace-revsalestrxn
title: RevSalesTrxn Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-revsalestrxn.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-apex-reference
legacy_page_id: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-11-25
---

# RevSalesTrxn Namespace

Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.

The `RevSalesTrxn` namespace includes these classes.

- 

**[CatalogRatesPreferenceEnum Enum](./apex-enum-revsalestrxn-catalogratespreferenceenum.md)**

Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

- 

**[ConfigurationExecutionEnum Enum](./apex-enum-revsalestrxn-configurationexecutionenum.md)**

Specifies the configuration method for the place sales transaction request.

- 

**[ConfigurationOptionsInput Class](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)**

Contains methods and properties to set the configuration options for the input to the product configurator.

- 

**[GraphRequest Class](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)**

Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.

- 

**[GroupRampActionEnum Enum](./apex-enum-revsalestrxn-grouprampactionenum.md)**

Specifies the action ‌that you want to perform on group ramp segments. Additionally, you can also convert a non-ramped group into a ramped group.

- 

**[PersistPreferenceEnum Enum](./apex-enum-revsalestrxn-persistpreferenceenum.md)**

Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.

- 

**[PlaceSalesTransactionException Class](./apex-class-revsalestrxn-placesalestransactionexception.md#placesalestransactionexception-class)**

Contains methods to hold the exception details for the place sales transaction request.

- 

**[PlaceSalesTransactionExecutor Class](./apex-class-revsalestrxn-placesalestransactionexecutor.md#placesalestransactionexecutor-class)**

Contains methods to place a sales transaction with details of the graph request, pricing preferences, and configuration options.

- 

**[PlaceSalesTransactionResponse Class](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)**

Contains properties to hold the response to the place sales transaction request.

- 

**[PricingPreferenceEnum Enum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)**

Specifies the pricing preference during the creation of a sales transaction.

- 

**[RecordResource Class](./apex-class-revsalestrxn-recordresource.md#recordresource-class)**

Contains constructors and properties to create a record object from the field values of a sales transaction.

- 

**[RecordWithReferenceRequest Class](./apex-class-revsalestrxn-recordwithreferencerequest.md#recordwithreferencerequest-class)**

Contains constructors and properties to associate a record object with a reference identifier.

- 

**[TaxPreferenceEnum Enum](./apex-enum-revsalestrxn-taxpreferenceenum.md)**

Specifies whether to execute or skip the tax calculation step for each sales transaction record. Available in API version 65.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-revsalestrxn.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
