---
article_id: ind.qocal_set_up_price_amendments.htm
title: Set Up Price Amendments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_price_amendments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_asset_management_features_in_revenue_cloud.htm
fetched_at: 2026-09-04
---

# Set Up Price Amendments

Sales reps can set a new price when they amend an asset instead of applying only a discount amount or discount percent.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To update revenue settings:	

Customize Application

AND

Manage Revenue Cloud

The Sales Price Amendments setting controls price amendment behavior for quote and order lines. It's turned off by default in existing orgs and turned on by default in new orgs.

From Setup, in the Quick Find box, enter Revenue Settings, and then select Revenue Settings.
Turn on Sales Price Amendments.
Update the pricing procedure selected in Revenue Settings to set the amended price.
In Pricing Procedure Builder, open the procedure selected in Revenue Settings. For example, to set the net unit price when the pricing source is the last transaction, add a List Group element after the Assignment element that assigns the EffectiveFrom date to PricingDate.
In the List Group element, configure the List Operation with these conditions.
Filter Condition Requirements: All Conditions Are Met (AND)
Resource: ItemPricingSource, Operator: Is Not Null
Resource: ItemPricingSource, Operator: Equals, Value: LastTransaction
In the List Group element, add an Assignment element, and map these variables.
Input Variable: InputUnitPrice
Output Variable: NetUnitPrice

To know more about these pricing elements, see List Group and List Operation and Map Context Tag Data Using Assignment Element. To edit a pricing procedure, see Configure Your Pricing Procedure.
