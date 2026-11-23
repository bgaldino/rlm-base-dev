---
article_id: ind.product_catalog_index_troubleshooting.htm
title: Product Catalog Index Errors and Troubleshooting
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_index_troubleshooting.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_index_products.htm
fetched_at: 2026-11-23
---

# Product Catalog Index Errors and Troubleshooting

Updating the index can, at times, cause errors in products or even index failures. On the Indexes page of the Index and Search Configuration tile, review the different error scenarios and the corresponding actions you can take when updating the index.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud

Check out the different error scenarios and the corresponding actions you can take when updating the search index:

INDEX UPDATE STATUS	SCENARIO	MAPS TO	ACTION
Completed	Index completed without product errors	Completed status in Rebuild History	None
Index completed with product errors	Product error warning	Download the CSV file and resolve the product errors.
Failed	Index failed without product errors	Index failure banner	Use the information in the failure message to resolve the issue.
Index failed with product errors	
Index failure banner
Product error warning
	
Use the information in the failure message to resolve the issue.
To resolve the product errors, download the CSV file in the warning message.
NOTE

The ErrorAttributeDataSizeLimitExceeded code in the CSV file indicates that you have reached the data size limit for all localized and nonlocalized attributes of a product for a single locale. Review your products to see if you can reduce the data indexed for search. For additional help, contact Salesforce Customer Support.

In case of product errors or index failures, Salesforce recommends that you rebuild the index after resolving issues.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_index_troubleshooting.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
