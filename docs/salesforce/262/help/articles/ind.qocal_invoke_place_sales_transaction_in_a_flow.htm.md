---
article_id: ind.qocal_invoke_place_sales_transaction_in_a_flow.htm
title: Invoke the Place Sales Transaction API in a Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_invoke_place_sales_transaction_in_a_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Invoke the Place Sales Transaction API in a Flow

Invoke the Place Sales Transaction (PST) API to create, update, and delete quotes and orders and price their related products and services. Before you can invoke the action, create and set the values of an Apex-defined variable to use as the graph input for the action. You can use the other inputs to configure how Salesforce prices and validates the quote or order. The action returns the ID of the sales transaction as well as status information.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

In Flow Builder, add an Action element to your flow. Select the Revenue Cloud category, and search for Invoke Place Sales Transaction API.

Set Input Values
INPUT PARAMETER	DESCRIPTION
Catalog Rates Preferences	

Specify how Agentforce Revenue Management prices a quote or order during processing. For example, if you add a quote line item to a quote, it’s possible that you don’t want to price the quote yet. Possible values are:

Force—Always price the quote or order.
Skip—Never price the quote or order.
System—Follow the system preference, which is used to determine whether a pricing calculation is required.

The default value is System.


Configuration Method	

Specify when Agentforce Revenue Management fetches rate card entries for quote line items with usage-based pricing during the quote creation process. Possible values are:

Fetch—Retrieve the rate card entries during the quote creation process.
Skip—Skip retrieving rate card entries for quote line items during the quote creation process.

The default value is Skip. This property is available only when usage-based selling is enabled.


Configuration Options	

Specify the rules that Salesforce follows to validate a quote or order. These options are expressed as booleans. To specify Revenue Cloud to perform an action, set the value for the option to true. You can specify true for multiple options. Options include:

validateProductCatalog—When true, validates against the product catalog.
validateAmendRenewCancel—When true, runs validations for amend, renew, or cancel processes.
executeConfigurationRules—When true, the order must adhere to configuration rules during processing. When false, the rules are bypassed and a warning is issued.
addDefaultConfiguration—When true, automatically add the default configurations to the quote or order.

The default value for all options is false.


Context Detail	Specify a string that contains the context ID so you can reuse the session context in a subsequent Place Sales Transaction API operation.
Graph	

This input is an Apex-defined variable of class RevSalesTrxn_RecordReference. It has two fields.

graphId—A string that identifies the graph.
records—An Apex-defined variable of class RevSalesTrxn_RecordReference.

The value of the records field depends on the object that you’re acting on and the action that you’re taking on the object. For example, to add line items to a Quote, you can set the records field as follows.

RecordReference.referenceId—A string that identifies the variable.
RecordReference.record.method—A string that defines the API method to call, for example, POST.
RecordReference.record.type—A string that defines the object to change, for example, QuoteLineItem.
RecordReference.record.fieldValues—A collection of Apex-defined variables of class RevSalesTrxn_RecordMapWrapper. Add the value of these Apex-defined variables to the fieldValues collection.
TransactionNameRecordMapWrapper
OppNameRecordMapWrapper
PricebookNameRecordMapWrapper
Store Output Values
OUTPUT PARAMETER	DESCRIPTION
Context Detail	An alphanumeric string that identifies the context.
Sales Transaction ID	The ID of the quote or order in this transaction.
Status URL	A link to the AsyncOperationTracker table that shows the status of your request. To return the status of that action, append an action’s Tracker ID to the URL.
Tracker ID	An alphanumeric string that identifies the specific action. To return the action’s status, append this ID to the Status URL.
Usage

To set up the Place Sales Transaction API input:

Use an Assignment element to set the field values of the TransactionNameRecordMapWrapper, OppNameRecordMapWrapper, and PricebookNameRecordMapWrapper of RevSalesTrxn_RecordMapWrapper class variables.
If you want to include configuration options, create the options as new Boolean variables.
NOTE Updates made through the Sales Transaction Line Editor don’t trigger record-triggered flows on Quote Line Group. The Sales Transaction Line Editor processes these updates through the Place Sales Transaction API in this order: Quote, Quote Line Group, and then Quote Line Item. When a Quote Line Group field changes in the Sales Transaction Line Editor and related Quote Line Items require updates, use custom Apex hooks instead of declarative record-triggered flows.
