---
article_id: ind.rev_agent_set_up_community_and_partner_access_for_agentforce_in_revenue_cloud.htm
title: Set Up Community and Partner Access for Agentforce in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_set_up_community_and_partner_access_for_agentforce_in_revenue_cloud.htm&type=5&release=262
release: 262
release_name: Summer '26
area: agents
fetched_at: 2026-05-12
---

# Set Up Community and Partner Access for Agentforce in Revenue Management

Make an Agentforce for Revenue agent available to customers or partners by configuring community or partner sites and enabling Embedded Messaging. You can create a community site for the Billing Service Assistance agent and a partner site for the Revenue Quote Management agent.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license with the Agentforce Employee Agent add-on
USER PERMISSIONS NEEDED
To create Customer and Partner Community users and profiles:	

Manage External Users

Manage Profiles and Permission Sets

Edit on Accounts


To use the Revenue Quote Management agent in the partner site:	

CalculatePrices API

CalculateTaxes API

InitiateAmendment API

InitiateRenewal API

Price and Tax Calculations on Quotes for Partner Community License

ProductAndPriceConfiguration API


To create and customize an Experience Cloud site by using the Self-Service Billing Portal template:	

Billing Admin permission set


To access Experience Cloud site created by using the Self-Service Billing Portal template:	

Billing Experience Cloud User permission set

Before you begin, Set Up Agentforce for Revenue Management.

Prepare Community and Partner Users

Create and configure users who can access the agent in a community or partner site.

Verify that these standard profiles exist:
Customer Community User
Customer Community Plus User
Partner Community User
Clone the required profile to create a custom community or partner profile.
From the App Launcher, open Accounts.
Create a new account or open an existing account.
From the account menu:
OPTION	VALUE
For community users	Enable Customer User
For partner users	Enable As Partner
Open the account’s Contacts related list.
From a contact record:
OPTION	VALUE
For community users	Enable Customer User
For partner users	Enable Partner User
Edit the user record and assign the Customer Community or the Partner Community license.
Select the custom profile and role for the user.
Save your changes.
Grant Community or Partner Users Access to the Site and Agent

Grant site and agent access so community or partner users can interact with the agent from the Experience Cloud site.

In Setup, find and select All Sites.
Open your site workspace.
Click Administration, and then select Members.
Add the custom community or partner profiles.
Save your changes.
Assign the custom Agentforce permission set to your community or partner users.
Configure Embedded Messaging for the Site

With embedded messaging customers and partners can chat with the agent from your Experience Cloud site.

Turn on Messaging.
Set Up Omni Channel
From Setup, find and select Omni-Channel Settings.
Turn on Enable Omni-Channel and then select Enable Skills-Based and Direct-to-Agent Routing.
Configure Routing and Queues

Create a fallback queue so conversations can route to service reps when the agent can’t resolve a request.

Create routing configurations for your queues.
Create your queues.
NOTE This queue acts as a fallback. If the Omni-Channel flow can’t route a conversation to the agent, the conversation is sent to this queue and assigned to a service rep.
In the Routing Configuration field, select the routing configuration you created.
Under Supported Objects, add Messaging Session.
Add supported objects based on the user type:
OPTION	VALUE
For community users:	
Billing Account
Billing Milestone Plan
Billing Schedule Group
Invoice
Messaging User
Messaging Session

For partner users:	
Messaging Session
In the Queue Members section, add your service reps to Selected Users.
Save your changes.
Create an Omni-Channel Flow

Use an Omni-Channel flow to route messages to the agent and send unresolved requests to a fallback queue.

Create an Omni-Channel flow with a Route Work element.
Specify these details:
OPTION	VALUE
Record ID	The recordId variable that you created.
Service Channel	Messaging
Route To	Agentforce <Employee/Service> Agent
Agentforce <employee/service> Agent	<your agent name>
Fallback Queue	The messaging queue that you previously created.
Create and Add an Enhanced Chat Channel

Create an Enhanced Chat channel to connect your Experience Cloud site to Omni-Channel routing and the agent experience.

Create an Enhanced Chat messaging channel.
Add these to your messaging channel:
Your Experience Cloud site domain
The Omni-Channel flow
The messaging queue
Activate the channel.
Add Embedded Messaging to the Site

Enable messaging on your Experience Cloud site so customers or partners can chat with the agent in context.

From Setup, find Digital Experiences, and then select All Sites.
Open your site in Builder.
Drag the Embedded Messaging component to the canvas.
Configure the component and select credential-based user verification.
Publish the site.
After publishing, users can open the chat window and interact with the agent from the site.

If you’re setting up the Billing Service Assistance agent for community users, complete Set Up the Billing Service Assistance Agent for Experience Cloud.
