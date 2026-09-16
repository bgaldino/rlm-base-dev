---
article_id: ind.qocal_considerations_syncing_quotes_and_opportunities_in_revenue_cloud.htm
title: Considerations for Syncing Quotes and Opportunities
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_syncing_quotes_and_opportunities_in_revenue_cloud.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_quote_management_lifecyle.htm
fetched_at: 2026-09-04
---

# Considerations for Syncing Quotes and Opportunities

Get to know the data differences between quotes and opportunities before you sync quote line items to an opportunity. These differences determine how the quote to opportunity sync handles bundle products, attributes, and term-defined items. Review these behaviors to ensure data consistency between your quotes and related opportunities.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

Starting the sync process makes sure that any changes you make to quote line items automatically update the associated opportunity.

Syncing occurs only from quote line item to opportunity product. You can't update the opportunity products while the sync is in process.

If the out-of-the-box sync process is running, you can’t use a custom automation to update quote line item fields to opportunity product fields as the fields lock.

Product and Attribute Mapping
Opportunities don’t support bundle structures, so the system adds all products within a bundle as separate, individual products in the opportunity.
Products appear as separate quote line items rather than a bundle when you create a subsequent quote from an opportunity.
The system doesn’t copy the selected quote line item’s attributes to the opportunity because opportunities don’t support product attributes. If needed, you can manually select attribute values when creating another quote from that opportunity.
Field Visibility and Term-Defined Products
Opportunity line items don’t include term-definition fields, such as period boundaries.
The system transfers only one-time products and excludes term-defined products when you create a quote from an opportunity.
Manage the Sync Process
Use the Start Sync quick action on the quote page to begin the process.
Use the Stop Sync quick action on the quote page to terminate the automatic update process.
