---
article_id: ind.qocal_before_you_begin_extending_your_transactions.htm
title: Before you Begin
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_before_you_begin_extending_your_transactions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extend_your_transactions_with_custom_field_support.htm
fetched_at: 2026-09-04
---

# Before you Begin

Complete these requirements before configuring your extended transactions:

Turn on Context Service in Salesforce Setup.
Verify Permissions: Make sure that you have the Context Service Admin and Manage Revenue Cloud permissions to extend definitions.
Assign Pricing Permissions: Assign the Salesforce Pricing Design Time User permission to edit pricing procedures.
Set Security: Configure field-level security for all fields you intend to extend so they map correctly.
Grant Access: Provide read access to source custom fields and edit access to destination custom fields to help APIs to populate data.
Review Mapping Paths: Confirm that your business process aligns with supported mapping flows, such as Product to Quote Line or Order to Asset.

This table maps the business process and mapping required between their objects.

BUSINESS PROCESS OR API	SOURCE OBJECT	DESTINATION OBJECT	CONTEXT TO CONTEXT MAPPING REQUIRED?
Browse Catalog	Product	Quote Line	Y
Product	Order Product	Y
Configuration	Product	Quote Line	Y
Product	Order Product	Y
Quote to Order	Quote	Order	N
Quote Line	Order Product
Quote Action	Order Action
Order to Asset	Order Product	Asset Action Source	

Y

Use the AssetToSalesTransactionMapping


Order Item Detail	Asset Action Source
Order Action	Asset Action
Asset to Quote and Asset to Order	Asset Action Source	Quote Line Detail	

Y

Use the SalesTransactionToAssetMapping


Asset Action Source	Order Item Detail
Quote to Contract	Quote	Contract	Y
Order to Contract	Order	Contract	Y
NOTE You can't map a QuoteLineItem or OrderItem object to an Asset object.
