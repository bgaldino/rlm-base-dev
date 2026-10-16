---
article_id: ind.qocal_extend_and_use_sales_transaction_context_definition.htm
title: Extend the Sales Transaction Context Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_extend_and_use_sales_transaction_context_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extend_your_transactions_with_custom_field_support.htm
fetched_at: 2026-09-04
---

# Extend the Sales Transaction Context Definition

Extend the standard definition to preserve necessary nodes and attributes for your custom requirements.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To extend context definitions:	

Context Service Admin

AND

Manage Revenue Management


To edit pricing procedures:	Salesforce Pricing Design Time User
From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
Locate SalesTransactionContext in the Standard Definitions tab.
Click the dropdown menu and select Extend.
 Give your extended context definition a name and save your changes.
In the Custom Definitions tab, click Edit on your new definition.
Set the Effective From date to occur earlier than your pricing procedure’s start date.
Click Next, leave default structure options unchanged, and save.
Optional: Under the Map Data tab, click Edit as SObject Mapping for Sales Transaction, select Mark as Default, and click Map.
Select your custom definition and click Activate.
