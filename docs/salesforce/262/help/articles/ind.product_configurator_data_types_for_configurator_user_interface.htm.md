---
article_id: ind.product_configurator_data_types_for_configurator_user_interface.htm
title: Data Types for Configurator User Interface
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_data_types_for_configurator_user_interface.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Data Types for Configurator User Interface

The Apex classes contain data accessible through the user interface. The Configurator’s Data Manager acts as the primary user interface component that exports data to other components. As a third-party user you can pass the data into your own user interface component without the need for separate queries to fetch data.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

The effective method to interact with the user interface is to import data through the Flow user interface properties that the Data Manager exports.

The effective way to modify quantities, attribute values, product options, and other state changes is to trigger LMS events for any updates your user interface component makes.

The Data Manager simplifies data management in your user interface component. It constantly updates and sends the latest information whenever changes occur. This creates a seamless flow where you don't need to actively listen for updates. Instead, you can simply import or watch the data directly from the flow properties.

The Configurator User Interface Data Manager exports the following Apex data types. This data is readily available for use by third-party configurators in the user interface, eliminating the need for them to query the data separately.

Apex Data Type: ProductConfig__Product
ProductConfig__Product
FIELD NAME	TYPE
id	String
quantity	Double
isConfigurable	Boolean
isActive	Boolean
quantityReadOnly	Boolean
isAssetizable	Boolean
isQuantityEditable	Boolean
isSelected	Boolean
isPersisted	Boolean
isHidden	Boolean
disabled	Boolean
isSoldOnlyWithOtherProds	Boolean
name	String
nodeType	String
productCode	String
productType	String
productComponentGroups	List<OptionGroup>
attributeCategories	List<AttributeCategory>
productKey	List<String>
additionalFields	Map<String, Object>
prices	List<Price>
productClassification	ProductClassification
productSellingModelOptions	List<ProductSellingModelOption>
qualificationContext	QualificationContext
minOptions	Integer
maxOptions	Integer
sequence	Integer
Apex Data Type: ProductConfig__Attribute
ProductConfig__Attribute
FIELD NAME	TYPE
id	String
name	String
label	String
attributeCategoryId	String
attributeNameOverride	String
code	String
dataType	String
defaultValue	String
description	String
productKey	List<String>
isCloneable	Boolean
isConfigurable	Boolean
isHidden	Boolean
isPriceImpacting	Boolean
isReadOnly	Boolean
isRequired	Boolean
assetAttributeValue	String
attributeValue	String
attributeKey	String
attributePicklistValue	String
businessObjectType	String
Apex Data Type: ProductConfig__AttributeCategory
ProductConfig__AttributeCategory
FIELD NAME	TYPE
code	String
id	String
name	String
attributes	List<Attribute>
Apex Data Type: ProductConfig__ConfiguratorContext
ProductConfig__ConfiguratorContext
FIELD NAME	TYPE
transactionLineId	String
parentName	String
origin	String
transactionId	String
addedNodes	List<SalesTransactionItem>
Apex Data Type: ProductConfig__Message
ProductConfig__Message
FIELD NAME	TYPE
text	String
type	String
Apex Data Type: ProductConfig__NavigationInfo
ProductConfig__NavigationInfo
FIELD NAME	TYPE
index	Integer
name	String
productKey	List<String>
Apex Data Type: ProductConfig__OptionGroup
ProductConfig__OptionGroup
FIELD NAME	TYPE
id	String
name	String
minOptions	Integer
maxOptions	Integer
sequence	Integer
components	List<Product>
productKey	List<String>
classifications	List<ProductClassification>
parentProductId	String
pricebookId	String
parentProductName	String
Apex Data Type: ProductConfig__Price
ProductConfig__Price
FIELD NAME	TYPE
pricebookEntryId	String
pricebookId	String
unitPrice	Double
pricingModel	PricingModel
Apex Data Type: ProductConfig__PricingModel
ProductConfig__PricingModel
FIELD NAME	TYPE
id	String
name	String
pricingModelType	String
Apex Data Type: ProductConfig__PricingSummary
ProductConfig__PricingSummary
FIELD NAME	TYPE
id	String
name	String
sequence	Integer
quantity	Double
hasErrors	Boolean
productRelatedComponentId	String
productKey	List<String>
prices	List<SummaryPrice>
transactionLineAttributes	List<Attribute>
transactionLineGroups	List<OptionGroup>
Apex Data Type: ProductConfig__ProductClassification
ProductConfig__ProductClassification
FIELD NAME	TYPE
id	String
Apex Data Type: ProductConfig__ProductSellingModel
ProductConfig__ProductSellingModel
FIELD NAME	TYPE
id	String
name	String
sellingModelType	String
status	String
Apex Data Type: ProductConfig__ProductSellingModelOption
ProductConfig__ProductSellingModelOption
FIELD NAME	TYPE
id	String
productId	String
productSellingModelId	String
productSellingModel	ProductSellingModel
Apex Data Type: ProductConfig__QualificationContext
ProductConfig__QualificationContext
FIELD NAME	TYPE
reason	String
isQualified	Boolean
Apex Data Type: ProductConfig__SalesTransactionItem
ProductConfig__SalesTransactionItem
FIELD NAME	TYPE
id	String
salesTransactionItemSource	String
pricebookEntry	String
productSellingModel	String
sellingModelType	String
subscriptionTerm	Integer
pricingTermUnit	String
unitPrice	Double
quantity	Double
product	String
productCode	String
productName	String
productBasedOn	String
businessObjectType	String
Apex Data Type: ProductConfig__SummaryPrice
ProductConfig__SummaryPrice
FIELD NAME	TYPE
netAmount	Double
netUnitPrice	Double
isInclusive	Boolean
pricingTermUnit	String
Apex Data Type: ProductConfig__TransactionRecord
ProductConfig__TransactionRecord
FIELD NAME	TYPE
parentId	String
parentName	String
origin	String
pricingTermUnit	String
