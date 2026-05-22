---
article_id: ind.qocal_limitations_for_using_quote_and_order_capture.htm
title: Transaction Management Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_limitations_for_using_quote_and_order_capture.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Transaction Management Considerations

Review essential requirements and behaviors before using Transaction Management to manage your quotes and orders. Understanding these configurations, including page layout updates, pricing synchronization, and field permissions, ensures accurate transaction processing and data integrity.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
UI and Button Configurations
Revenue Management excludes support for Add Products and Edit Products buttons on quote and order related lists.
Turn off these buttons on quote and order page layouts.
Sales reps use the Add Product search field or the Browse Catalog button to find and add products.
To use the Browse Catalogs quick action on quote and account record pages, set up Product Discovery.
Pricing and Data Synchronization
Product updates and price changes require decision table refreshes, price syncing, and updates to context definitions.
If you add a new product, update product pricing, or create contract pricing, refresh all decision tables in your org.
If you define a qualification rule for a new product in Product Catalog Management, update the decision table for that specific rule.
Sync pricing data after changing information in Salesforce Pricing to make sure that reps see accurate prices.
Salesforce Pricing automatically populates Net Unit Price, Net Total Price, Total Adjustment Amount, Pricing Term Count, and Total Line Amount for order products.
Make these fields "read only" on the order product page layout to prevent manual edits when a pricing engine is active.
API and Integration Rules
Use the Place Order API to create, edit, and price orders for custom user interfaces.
Salesforce Pricing doesn’t trigger when you use other mechanisms, such as sObject APIs.
The Asset object doesn’t support the Quote Action related list because Revenue Management creates assets from finalized orders rather than quotes.
To view amendments, renewals, or cancellations, use the associated order records.
Feature Compatibility and Permissions
Users with Subscription Management permissions use existing standalone products, bundles, and generate assets in both Subscription Management and Revenue Management.
Revenue Management shows these fields after enablement: Include component by default (set to true for static bundles), Allow qty changes, Min qty, Max qty, and Group.
Contact Salesforce Customer Support to resolve validation errors resulting from modifications to an existing bundle.
Subscription Management users manage standalone products, bundles, and assets in both Subscription Management and Revenue Management.
More Resources
Customize Related Lists
Refresh a Decision Table
Product Discovery Setup
Customize Page Layouts with the Enhanced Page Layout Editor
Field Permissions
Sync Pricing Data
