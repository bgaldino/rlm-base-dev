---
article_id: ind.product_configurator_flow_summary.htm
title: Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_summary.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Summary

Summary is a UI display component that renders the pricing summary section in Product Configurator. The component displays the current product's pricing information, including one-time, monthly, and annual totals, along with a hierarchical breakdown of child products and their prices. Summary has no output properties, and doesn’t listen to or fire any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Summary Responsibilities
Display prices, including one-time, monthly, and annual
Display nested product pricing structure
Update pricing data based on the user’s current navigation route
Calculate and display subtotals for product groups
Support custom fields in pricing footer and pane
Handle Asset Renewal Configuration (ARC), also called delta pricing
Switch between standard and custom layouts
Summary API Name

S01_Summary

Input Properties

Summary accepts data from these parent and flow component properties, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
summary	Object	Yes	Summary data from DataManager (merged transaction tree)
salesTransactionItems	Array	No	Transaction items data
navigationRoute	Array	No	Current navigation route (breadcrumb path)
currencyCode	String	No	Currency code for price display
isDesignTime	Boolean	No	Whether in design or preview mode
layoutMode	String	No	

Layout mode (standard or compact)
