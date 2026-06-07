---
article_id: ind.qocal_set_up_flow_for_managing_assets.htm
title: Set Up Asset Lifecycle Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_flow_for_managing_assets.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Asset Lifecycle Flows

To streamline asset management through their lifecycle and optimize revenue, select a default flow for your assets from the Revenue Settings page. Adding an amend, renew, and cancel flow saves time and money by automating the transition of products through different lifecycle stages.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To update the Revenue Settings in Agentforce Revenue Management:	Customize Application

Create a custom flow by using the default flow as a guide or starting point. The default output type is Quote, but you can change it to Order.

IMPORTANT The flow times out after 10 seconds. Users interacting with the user interface can’t create an Amendment, Renewal, or Cancellation quote with 1,000 line items. Users create the initial quote with fewer line items and then update it to include up to 1,000 items by using APIs or the Add Assets button in the Quote Viewer.
From Setup, in the Quick Find box, search for and select Revenue Settings.
In the Quote, Order, and Configuration Settings section, find Set Up Flow for Managing Assets.
Enter the name of the Amend, Renew, and Cancel Salesforce Flow for the system to use when users select the Amend, Renew, or Cancel buttons in the Managed Assets Viewer.
Save your changes.
EXAMPLE
