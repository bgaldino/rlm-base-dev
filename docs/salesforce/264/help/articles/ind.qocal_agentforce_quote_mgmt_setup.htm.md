---
article_id: ind.qocal_agentforce_quote_mgmt_setup.htm
title: Set Up Revenue Quote Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_agentforce_quote_mgmt_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_agentforce_quote_mgmt.htm
fetched_at: 2026-09-04
---

# Set Up Revenue Quote Management

To use additional features relevant to quotes, turn on the required features and assign permissions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management with the Revenue Cloud Advanced license with the Agentforce Employee Agent add-on.
Set Up Agentforce for Revenue Management.
To improve the accuracy and relevance of product search results, configure indexing. You can also turn on semantic search for broader matching. If semantic search doesn’t return the results you expect, turn it off and continue using indexed search.
Configure multiple currencies.
Set up multiple currencies for transactions.
From Setup, in the Quick Find box, find and select Flows.
Under Flow Definitions, open the Add QuoteLineItem to Quote flow.
Add a condition to the Get Product element that verifies whether the Currency ISO Code field is available on the product record.
Open the Get Price Book Entry element.
In the Filter Price Book Entry Records section, set the Condition Requirements field to All Conditions Are Met (AND).
Click + Add Condition.
Set the Product ID field to productId and the Currency ISO Code field to the currency you want to support.
Specify the currency by using its ISO code.
To access the Consumption Management topic within the Revenue Quote Management template, turn on rate management and usage management.
