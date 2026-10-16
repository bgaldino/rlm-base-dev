---
article_id: ind.qocal_customize_transaction_summary.htm
title: Customize Transaction Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_customize_transaction_summary.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_customize_quote_and_order_capture.htm
fetched_at: 2026-09-04
---

# Customize Transaction Summary

The Transaction Summary component shows a snapshot of key financial details from quote and order records. It provides a scannable overview of pricing, discounts, and total amounts to help users verify transaction accuracy before processing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To customize the Transaction Summary:	Customize Application
To view Transaction Summary on the Orders page:	

Field-level security to these Order fields:

TotalRoundedLineAmount (Read-only)
DiscountPercent (Read-only)
TotalAmount (Read-only)
NOTE Use a custom permission set to provide read access for users who lack the Place Order API permission but require access to other order fields.
Open any quote or order record page.
From Setup, select Edit Page.
Select the Transaction Summary component to view its properties.
Select Expanded by Default to show all summary details automatically when the page loads.
Move the required fields to the Selected section for both the footer and body areas.
Drag fields within the list to arrange them in your preferred order.
Save your changes and activate the page.

Review these requirements to ensure that your components appear and function correctly in your quote document templates.

Vertical Positioning: Place the Transaction Summary component in the same tab as the Sales Transaction Line Editor or the Transaction Line Editor. Its vertical position within that tab doesn't affect functionality.
Rendering Behavior: The component always renders at the bottom of the page in the live view, regardless of where you drop it in the Lightning App Builder.
Field Limitations: Avoid adding fields with the Address data type, such as Ship To or Bill To, as the component doesn’t support them.
Component Selection: If other components hide the component box in the Lightning App Builder, confirm your selection by checking for Transaction Summary in the properties panel.
