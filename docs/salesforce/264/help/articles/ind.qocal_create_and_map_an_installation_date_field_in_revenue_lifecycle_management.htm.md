---
article_id: ind.qocal_create_and_map_an_installation_date_field_in_revenue_lifecycle_management.htm
title: "Example: Map an Installation Date Field"
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_and_map_an_installation_date_field_in_revenue_lifecycle_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extend_your_transactions_with_custom_field_support.htm
fetched_at: 2026-11-23
---

# Example: Map an Installation Date Field

Follow these steps to track a custom InstallationDate__c field across the sales lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Add Products

Add the field to the Product and Quote Line Item objects. Then, update the Product Discovery and Sales Transaction context definitions. 

Use Object Manager to add InstallationDate__c to Product and Quote Line Item.
In Context Service, edit your Product Discovery context definition.
Under the CategoryProduct node, create an InstallationDate attribute.
Under the CategoryProduct node, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a Product object mapping in ProductDiscoveryMapping.
In Context Service, edit your Sales Transaction context definition.
Under the QuoteLineItem node, create an InstallationDate attribute.
Under the QuoteLineItem node, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a QuoteLineItem object mapping in QuoteEntitiesMapping.
Create a cross-context attribute mapping in ProductDiscoveryContextMapping that maps ProductDiscoveryContext.Product.InstallationDate to SalesTransactionContext.QuoteLineItem.InstallationDate.
Quote to Order

Add the field to Quote Line Item and Order Item. Then, update the Sales Transaction context definition.

Use Object Manager to add InstallationDate__c to Quote Line Item and Order Item.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransactionItem node, create an InstallationDate attribute.
Under the SalesTransactionItem node, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a QuoteLineItem object mapping in QuoteEntitiesMapping.
To map InstallationDate to InstallationDate__c, add an OrderItem object mapping in OrderEntitiesMapping.
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Quote to Contract

Add the field to Quote and Contract. Then, update the Sales Transaction context definition.

Use Object Manager to add InstallationDate__c to Quote and Contract.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransaction and Contract nodes, create an InstallationDate attribute.
Under the SalesTransaction and Contract nodes, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a Quote object mapping in QuoteToContractSlsTrxnMapping.
To map InstallationDate to InstallationDate__c, add a Contract object mapping in ContractNodeMapping.
To map InstallationDate from SalesTransaction node to InstallationDate on the Contract node, create a mapping in ContractToSalesTxnMapping.
ContractToSalesTxnMapping is an intra-context mapping. Select the Context Definition object next to the mapping as well. Then, map from source (SalesTransaction node) to target (Contract node).
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Quote Line Item to Contract Item Price

Add the field to Quote Line Item and Contract Item Price. Then, update the Sales Transaction context definition.

Use Object Manager to add InstallationDate__c to QuoteLineItem and ContractItemPrice.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransactionItem and ContractItemPrice nodes, create an InstallationDate attribute.
Under the SalesTransactionItem and ContractItemPrice nodes, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a QuoteLineItem object mapping in QuoteToContractSlsTrxnMapping.
To map InstallationDate to InstallationDate__c, add a ContractItemPrice object mapping in ContractNodeMapping.
To map InstallationDate from SalesTransactionItem node to InstallationDate on the ContractItemPrice node, create a mapping in ContractToSalesTxnMapping.
ContractToSalesTxnMapping is an intra-context mapping. Select the Context Definition object next to the mapping as well. Then, map from source (SalesTransactionItem node) to target (ContractItemPrice node).
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Order to Contract

Add the field to Order and Contract. Then, update the Sales Transaction context definition.

Use Object Manager to add InstallationDate__c to Order and Contract.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransaction and Contract nodes, create an InstallationDate attribute.
Under the SalesTransaction and Contract nodes, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add an Order object mapping in OrderToContractSlsTrxnMapping.
To map InstallationDate to InstallationDate__c, add a Contract object mapping in ContractNodeMapping.
To map InstallationDate from SalesTransaction node to InstallationDate on the Contract node create a mapping in ContractToSalesTxnMapping.
ContractToSalesTxnMapping is an intra-context mapping. Select the Context Definition object next to the mapping as well. Then, map from source (SalesTransaction node) to target (Contract node).
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Order to Asset

Add the field to Order and Asset Action Source. Then, update the Sales Transaction context definition. 

NOTE Custom field mapping from Order to Asset Action Source is only available for Agentforce Revenue Cloud.
Use Object Manager to add InstallationDate__c to Order Item and Asset Action Source.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransactionItem and AssetActionSource nodes, create an InstallationDate attribute.
Under the SalesTransactionItem and AssetActionSource nodes, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add an OrderItem object mapping in OrderEntitiesMapping.
To map InstallationDate to InstallationDate__c, add an AssetActionSource object mapping in AssetEntitiesMapping.
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Create a new mapping from the Installation Date in AssetActionSource to InstallationDate in SalesTransactionItem in the Order to Asset inter-context mapping called AssetToSalesTransactionMapping.
Amend, Renew, Cancel

Add the field to Quote Line Item, Order Item and Asset State Period. Then, update the Sales Transaction context definition.

Use Object Manager to add InstallationDate__c to QuoteLineItem, OrderItem and AssetStatePeriod.
In Context Service, edit your Sales Transaction context definition.
Under the SalesTransactionItem and Asset State Period nodes, create an InstallationDate attribute.
Under the SalesTransactionItem and Asset State Period nodes, create an InstallationDate tag.
To map InstallationDate to InstallationDate__c, add a Quote Line Item object mapping in QuoteEntitiesMapping.
To map InstallationDate to InstallationDate__c, add an Order Item object mapping in OrderEntitiesMapping.
To map InstallationDate to InstallationDate__c, add an AssetStatePeriod object mapping in AssetEntitiesMapping.
Set SalesTransaction as the default mapping on the extended SalesTransactionContext and then activate it.
Create a new mapping between the Installation Date in SalesTransactionItem to InstallationDate in AssetStatePeriod in the Amend, Renew, Cancel cross-context mapping called SalesTxnItmToAssetStatePrdMap.
Cross-context mappings don’t have default connected objects. Select the data source Context Definition Objects and the context definition you're using from the dropdown to create mappings between the two entities.
Create a new mapping between the Installation Date in AssetStatePeriod to InstallationDate in SalesTransactionItem in the cross-context mapping called AssetStatePrdToSalesTxnItmMap.
Map Custom Fields between AssetActionSource and Quote Line Item Detail or Order Item Detail

When quotes or orders include detail lines, map custom fields on the detail node so asset action source records store the detail-line field values.

IMPORTANT Configure the detail-line mapping in addition to the item-level mapping. To cover standard lines and detail lines, configure the SalesTransactionItem mapping and the SalesTransactionItemDetail mapping.
In Object Manager, add a custom field with the API name InstallationDate__c on Quote Line Item Detail or Order Item Detail, and on Asset Action Source.
In Context Service, edit the Sales Transaction context definition.
Under the SalesTransactionItemDetail node, create an attribute and a tag for InstallationDate__c.
Under the AssetActionSource node, create an attribute and a tag for InstallationDate__c.
To map InstallationDate__c to the quote or order object, add a mapping on the SalesTransactionItemDetail node in QuoteEntitiesMapping or OrderEntitiesMapping.
To map InstallationDate__c to the Asset Action Source object, add a mapping on the AssetActionSource node in AssetEntitiesMapping.
Create a mapping between the InstallationDate__c in AssetActionSource and SalesTransactionItemDetail in the Order to Asset mapping called AssetToSalesTransactionMapping.
Create a mapping between the InstallationDate__c in SalesTransactionItemDetail and AssetActionSource in the Amend, Renew, Cancel mapping called SalesTransactionToAssetMapping.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_and_map_an_installation_date_field_in_revenue_lifecycle_management.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
