---
article_id: ind.collections_setup_service_cloud_voice_amazon_connect.htm
title: Set Up Salesforce Voice with Amazon Connect
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_service_cloud_voice_amazon_connect.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_outbound_dialer.htm
fetched_at: 2026-06-21
---

# Set Up Salesforce Voice with Amazon Connect

Salesforce Voice with Amazon Connect (formerly Service Cloud Voice with Amazon Connect) integrates Amazon's cloud contact center directly into the Service Cloud Console. This creates a unified rep workspace that combines phone, digital channels, and customer data, and prevents Collections reps from switching between separate phone systems and the Salesforce app. Turn On Salesforce Voice with Amazon Connect, set up contact center, update root-email address, turn on Service Setup Assistant, configure Omni-Channel unified routing and after conversation work time.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To set up Omni-Channel:	Customize Application
To set up Identity Provider:	Manage Identity Provider
To view the Amazon Contact Centers page:	Customize Application AND Manage Call Centers
To create and manage a contact center:	Salesforce Voice Contact Center Admin
To run the Service Setup Assistant:	Customize Application
To create a service channel:	Customize Application
To create and save Lightning pages in the Lightning App Builder:	Customize Application

Before you set up Salesforce Voice, complete these prerequisites.

Before you begin setting up your Voice contact center, take care of essential planning steps.
Choose your Salesforce Voice telephony model to set up Salesforce Voice with Amazon Connect.
Prepare your network for Salesforce Voice.
Enable Omni-Channel.
Set up Identity Provider.
Before setting up Salesforce Voice, review its limitations.
Turn On Salesforce Voice with Amazon Connect.
After you create Amazon Web Services subaccount, confirm your company’s tax registration number for the subaccount.
Set up your contact center for Salesforce Voice with Amazon Connect.
To access the Service Console features, turn on Service Console.
From Setup, in the Quick Find box, find, and select Service Setup Assistant.
Turn on Service Setup Assistant.
To manage reps, queues, routing logic, rep statuses, and Omni-Channel Supervisor directly in Salesforce, configure Omni-Channel Unified routing.
Make sure that you enable Omni-Channel and Enhanced Omni-Channel Routing.

The Update and Route Collection Campaign Call prebuilt flow doesn't include logic for Skills-Based and Direct-to-Agent Routing. If you plan to implement this, enable Skills-Based and Direct-to-Agent Routing, and clone and customize the prebuilt flow, Update and Route Collection Campaign Call.

Clone the prebuilt flow, Update and Route Collection Campaign Call, and note the label and API name of the cloned flow. When creating a Contact Center Channel, go to the Contact Center Channels section, and select the cloned flow's API name in the Call Routing Type field, and then enter the cloned flow label name and fallback queue name. This configuration makes sure that phone channel calls are routed according to the business logic specified in the flow.

To give collections reps a set amount of time after a customer conversation to wrap up their work before they start a new conversation, configure After Conversation Work (ACW) time, and add the After Conversation Work component to your voice call record details page.
