---
article_id: ind.qocal_extend_your_transactions_with_custom_field_support.htm
title: Extend and Map Sales Transactions in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_extend_your_transactions_with_custom_field_support.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_capture.htm
fetched_at: 2026-09-04
---

# Extend and Map Sales Transactions in Revenue Management

Extend or customize default features to meet business-specific requirements by creating and mapping custom fields in Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

For example, if your business requires delivery or installation dates that aren’t available by default on sObjects, you can add these custom fields to your sales process objects. Mapping these fields in context definitions makes sure that they appear during transactions and that entered values persist after a refresh.

Before you Begin
Complete these requirements before configuring your extended transactions:
Extend the Sales Transaction Context Definition
Extend the standard definition to preserve necessary nodes and attributes for your custom requirements.
Create Custom Fields and Add Custom Attributes
After extending the definition, add the actual fields to Salesforce objects and the corresponding attributes to the context.
Map Custom Fields in Context Service
Use Context Service to map custom fields across definitions to make sure that values persist during transactions. If you don’t map custom fields to their corresponding attributes, you can’t update those fields on records.
Link Context Definitions to Pricing Procedures
Link your pricing procedure to your extended context definition to enable efficient data access.
Example: Map an Installation Date Field
Follow these steps to track a custom InstallationDate__c field across the sales lifecycle.
