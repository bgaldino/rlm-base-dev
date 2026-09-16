---
article_id: ind.qocal_map_custom_fields.htm
title: Map Custom Fields in Context Service
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_map_custom_fields.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extend_your_transactions_with_custom_field_support.htm
fetched_at: 2026-09-04
---

# Map Custom Fields in Context Service

Use Context Service to map custom fields across definitions to make sure that values persist during transactions. If you don’t map custom fields to their corresponding attributes, you can’t update those fields on records.

Here are the list of key mapping types.

sObject Mapping: Links a context definition node to a Salesforce object (for example, QuoteEntitiesMapping).
Cross-context mapping: Links attributes between two different definitions (for example, Product Discovery to Sales Transaction).
Context definition mapping: Links attributes within a specific flow (for example, Order to Asset).
CONTEXT DEFINITION	MAPPING	PROCESS	SOURCE	DESTINATION	TYPE OF MAPPING
ProductDiscovery Extended Context Definition	ProductDiscoveryMapping	Product Discovery	ProductDiscoveryExtended Context Definition	Product2	sObject
Sales Transaction Context Definition	ProductDiscoveryContextMapping	Product Discovery to Sales Transaction	SalesTransaction Context Definition	Product Discovery Extended Context Definition	Cross-context definition mapping
QuoteEntitiesMapping	Quote	SalesTransaction Context Definition	QuoteEntities	sObject
OrderEntitiesMapping	Order	SalesTransaction Context Definition	Order Entities	sObject
ContractNodeMapping	Contract	SalesTransaction Context Definition	Contract Entities	sObject
AssetEntitiesMapping	Assets	SalesTransaction Context Definition	Asset Entities	sObject
ContractToSalesTxnMapping	

Order to Contract 

Quote to Contract

	SalesTransaction Context Definition	SalesTransaction Context Definition	Context definition mapping
AssetToSalesTransactionMapping	Order to Asset	SalesTransaction Context Definition	SalesTransaction Context Definition	Context definition mapping
SalesTransactionToAssetMapping	Amend, Renew, Cancel	SalesTransaction Context Definition	SalesTransaction Context Definition	Context definition mapping
NOTE Twin mapping supports custom fields only. Standard-to-standard field mapping from Product2 to QuoteLineItem isn't supported. For a worked example of custom field twin mapping, see How to Twin Map a Custom Field from Product2 to QuoteLineItem. For details about the standard field limitation and available workarounds, see Twin Mapping Standard Fields from Product2 to QuoteLineItem Not Supported.
