---
article_id: ind.qocal_considerations_syncing_quotes_and_opportunities_in_revenue_cloud.htm
title: Considerations for Syncing Quotes and Opportunities
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_syncing_quotes_and_opportunities_in_revenue_cloud.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Syncing Quotes and Opportunities

Understand how the system handles bundle products, attributes, and term-defined items before you sync quote line items to an opportunity. Reviewing these behaviors ensures data consistency between your quotes and related opportunities.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

Starting the sync process makes sure that any changes you make to quote line items automatically update the associated opportunity.

Product and Attribute Mapping
Opportunities don’t support bundle structures, so the system adds all products within a bundle as separate, individual products in the opportunity.
Products appear as separate quote line items rather than a bundle when you create a subsequent quote from an opportunity.
The system doesn’t copy the selected quote line item’s attributes to the opportunity because opportunities don’t support product attributes.
Manually select attribute values when creating another quote from that opportunity.
Field Visibility and Term-Defined Products
Users syncing Quote Line Items with Opportunity Line Items see the HasRevenueSchedule and HasQuantitySchedule fields.
Opportunity Line Items don’t include term-definition fields, such as period boundaries.
The system transfers only one-time products and excludes term-defined products when you create a quote from an opportunity.
Manage the Sync Process
Use the Start Sync quick action on the quote page to begin the process.
Use the Stop Sync quick action on the quote page to terminate the automatic update process.
