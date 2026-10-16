---
article_id: ind.qocal_set_up_quote_and_order_features_in_revenue_cloud.htm
title: Set Up Quote and Order Features in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_quote_and_order_features_in_revenue_cloud.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_foundational_setup_for_quotes_and_orders.htm
fetched_at: 2026-09-04
---

# Set Up Quote and Order Features in Revenue Management

Set up features that provide your sales reps, partners, and customers with the capabilities required to efficiently manage quotes and orders.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Add and Customize the Transaction Line Editor or Sales Transaction Line Editor
To help sales reps to view and manage quote and order line items efficiently, add the Transaction Line Editor or Sales Transaction Line Editor (STLE) to the page layout and customize the fields that the editor shows. We strongly recommend using STLE because its streamlined, single-grid layout improves performance at scale and provides access to the latest capabilities in Transaction Management. The Transaction Line Editor remains available, but it’s no longer being enhanced.
Set Up the Transaction Processing Type for Quotes and Orders
Define how Revenue Management processes transactions by selecting a default Transaction Processing Type (TPT).
Set Up Delta Pricing
Improve large transaction performance by enabling Delta Pricing to recalculate only modified quote or order lines and their dependencies.
Invoke the Place Sales Transaction API in a Flow
Invoke the Place Sales Transaction (PST) API to create, update, and delete quotes and orders and price their related products and services. Before you can invoke the action, create and set the values of an Apex-defined variable to use as the graph input for the action. You can use the other inputs to configure how Salesforce prices and validates the quote or order. The action returns the ID of the sales transaction as well as status information.
Reprice All for Quotes and Orders
Refresh and validate prices across an entire transaction by recalculating all quote or order lines.
Secure Data Access for Pricing with Elevated Permissions
Protect sensitive data from unauthorized access and have business continuity during sales transaction pricing. This feature helps sales users to price quotes and orders without needing field-level security (FLS) to query, view, or modify the underlying sensitive fields.
