---
article_id: ind.product_configurator_set_up_constraint_engine_context_definitions.htm
title: Set Up Context Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_constraint_engine_context_definitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_set_up_constraints_engine.htm
fetched_at: 2026-09-04
---

# Set Up Context Definitions

Update the extended SalesTransactionContext context definition and set up a custom asset context definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Update the Extended SalesTransactionContext Context Definition

To use the custom ConstraintEngineNodeStatus field, update the extended SalesTransactionContext context definition ​that's configured for the default pricing procedure on the Revenue Settings page.

Add Attributes

Edit the extended SalesTransactionContext context definition and add these attributes.

ADD ATTRIBUTE TO	ATTRIBUTE NAME	TYPE	DATA TYPE
SalesTransactionItem node	ConstraintEngineNodeStatus	INPUTOUTPUT	STRING
AssetActionSource	AssetConstraintEngineNodeStatus	INPUTOUTPUT	STRING

See Edit Context Definitions and Add Attributes.

Map Attributes

If you're using Business Rules Engine and want to set up Constraint Rules Engine, or want to use both engines, the TransactionType attribute mapping switches between the rules engines at the transaction level.

Open the extended SalesTransactionContext context definition, go to the Map Data tab, and map the necessary attributes.

Before you map these attributes, turn on Transaction processing for quotes and orders on the Revenue Settings page.

MAPPING NAME	ATTRIBUTE	MAP TO
QuoteEntitiesMapping	ConstraintEngineNodeStatus	ConstraintEngineNodeStatus__c field on the QuoteLineItem object
QuoteEntitiesMapping	TransactionType on the SalesTransaction node	TransactionType field on the Quote object
OrderEntitiesMapping	ConstraintEngineNodeStatus	ConstraintEngineNodeStatus__c field on the OrderItem object
OrderEntitiesMapping	TransactionType on the SalesTransaction node	TransactionType field on the Order object
AssetEntitiesMapping	AssetConstraintEngineNodeStatus	ConstraintEngineNodeStatus__c field on the AssetActionSource object

Then, edit AssetToSalesTransactionMapping. Select the data source as Context Definition, select your extended Sales Transaction context definition, and find the SalesTransactionItem node listed. Then, map the AssetConstraintEngineNodeStatus attribute to the ConstraintEngineNodeStatus__c field on the SalesTransactionItem node.

See Add Context Mapping.

Activate Context Definition

Activate the updated SalesTransactionContext context definition.

See Activate a Context Definition.

Set Up Custom Asset Context Definition

Set up an asset context definition to get asset data based on the selected context. Use this asset data when you configure asset-based rules and constraints in the CML Editor, and apply other filters on the data as needed.

An asset context is required to create asset-based configuration rules and constraints. If you don't define one, Constraint Rules Engine doesn't fetch any asset data.

NOTE You can set up a custom asset context definition only from Summer ’25 and onwards.
Create Custom Asset Context Definitions

To fetch assets for a specific account, product, or a custom or standard field of the asset, define a custom asset context definition.

Extend the standard AssetContext__stdctx context definition.
Customize the mappings according to your requirements.

See Extend a Context Definition and Edit Context Definitions.

Select an Asset Context for Constraint Rules Engine

Select the asset context for Constraint Rules Engine to apply asset-based configuration rules and constraints.

NOTE Select an asset context for Product Configurator only if your constraint model uses assets.
From Setup, in the Quick find box, enter Revenue Settings, and then select Revenue Settings.
In the Set Up Asset Context for Product Configurator section, select the asset context definition that you want to use.

After you select the asset context definition, filter the asset data directly in the CML Editor based on your requirements when you define configuration rules and constraints.

To learn about creating rules and constraints by using Constraint Rules Engine, see Use Constraint Builder With Constraint Rules Engine.
