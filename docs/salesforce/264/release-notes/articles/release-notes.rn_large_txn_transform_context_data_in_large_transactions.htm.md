---
article_id: release-notes.rn_large_txn_transform_context_data_in_large_transactions.htm
title: Transform Context Data in Large Transactions
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_large_txn_transform_context_data_in_large_transactions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_large_txn.htm
fetched_at: 2026-09-30
---

# Transform Context Data in Large Transactions

Apply Data Processing Engine (DPE) transforms to context data in large transactions, so you can shape and localize high-volume data before it's merged into documents. Transformation definitions run against Revenue Management transactions, such as quotes and orders with thousands of line items. Previously, DPE-based transforms in the Context Service were available only for standard transactions.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced or Revenue Cloud Billing license.

How: On the Transform tab of a context definition, create a transformation definition in the Data Processing Engine. You can then use the definition in Salesforce Document Generation for standard and large transactions.
