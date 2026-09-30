---
article_id: release-notes.rn_large_txn.htm
title: Large Transactions and Quote Processing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_large_txn.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Large Transactions and Quote Processing

Process quotes and orders with up to 15,000 line items without timeouts or performance bottlenecks. Asynchronous processing keeps sales reps and billing teams working while calculations, synchronization, and document generation run in the background. Configure products, apply pricing rules, and generate documents for complex transactions with thousands of lines, nested bundles, and multilevel grouping.

Sync Large Quotes to Opportunities Without Interruption
Sync quotes with up to 15,000 line items to opportunities asynchronously to prevent timeouts and maintain performance. Background processing keeps sales reps working without interruption. Enable this capability in Revenue Settings for both standard and large quotes.
Recover Faster from Quote and Order Calculation Errors
Process large quotes and orders faster with improved batching algorithms and support for nested line items. Use a REST API to manually change stuck calculation states to Failed so that your teams can quickly retry transactions.
Speed Up Large Quote Operations with Automatic Context Reuse
Edit large quotes and orders more efficiently with a single session context for each transaction. Reusing the context eliminates repeated context creation and keeps your data consistent and up to date as you make changes. Context reuse is enabled automatically for large transactions, so no setup is required.
Generate Documents for Quotes with 15,000 Line Items
Create PDFs that accurately capture complex product hierarchies in large quotes. CLM Document Generation supports quotes with up to 15,000 line items, 1,000 bundles, and 5 levels of nested grouping.
Transform Context Data in Large Transactions
Apply Data Processing Engine (DPE) transforms to context data in large transactions, so you can shape and localize high-volume data before it's merged into documents. Transformation definitions run against Revenue Management transactions, such as quotes and orders with thousands of line items. Previously, DPE-based transforms in the Context Service were available only for standard transactions.
Apply Configuration Rules Across 15,000 Line Items
Apply rules and constraints across quotes or orders with up to 15,000 line items. Run configurations accurately and efficiently for all products and bundles in the quote or order. Automate and validate demanding configurations at scale, so your sales reps can build large quotes and orders without reaching scale limits.
Price Quotes and Orders with Up to 15,000 Lines
Price quotes and orders with up to 15,000 lines, an increase from the previous 1,000-line limit. Your teams can process larger deals without splitting them into multiple transactions. Configure separate pricing procedures when large and standard transactions require different pricing capabilities.
