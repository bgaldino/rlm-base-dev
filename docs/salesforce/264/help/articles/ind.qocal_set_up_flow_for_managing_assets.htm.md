---
article_id: ind.qocal_set_up_flow_for_managing_assets.htm
title: Set Up Asset Lifecycle Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_flow_for_managing_assets.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_asset_management_features_in_revenue_cloud.htm
fetched_at: 2026-11-23
---

# Set Up Asset Lifecycle Flows

To streamline asset management through their lifecycle and optimize revenue, select a default flow for your assets from the Revenue Settings page. Adding an amend, renew, and cancel flow saves time and money by automating the transition of products through different lifecycle stages.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To update the Revenue Settings in Revenue Cloud:	Customize Application

Create a custom flow by using the default flow as a guide or starting point. The default output type is Quote, but you can change it to Order.

IMPORTANT The flow times out after 10 seconds. Users interacting with the user interface can’t create an Amendment, Renewal, or Cancellation quote with 1,000 line items. Users create the initial quote with fewer line items and then update it to include up to 1,000 items by using APIs or the Add Assets button in the Quote Viewer.
From Setup, in the Quick Find box, search for and select Revenue Settings.
In the Quote, Order, and Configuration Settings section, find Set Up Flow for Managing Assets.
Enter the name of the Amend, Renew, and Cancel Salesforce Flow for the system to use when users select the Amend, Renew, or Cancel buttons in the Managed Assets Viewer.
Save your changes.
EXAMPLE

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_flow_for_managing_assets.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
