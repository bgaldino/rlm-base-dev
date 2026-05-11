---
article_id: ind.billing_set_up_billing_service_assistance_agent_for_experience_cloud.htm
title: Set Up Billing Service Assistance Agent for Experience Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_set_up_billing_service_assistance_agent_for_experience_cloud.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Billing Service Assistance Agent for Experience Cloud

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Set Up Billing Service Assistance Agent for Experience Cloud

Configure service access, security, and data sharing so that external users can securely interact with Billing Service Assistance Agent through Embedded Messaging in an Experience Cloud site.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license and Agentforce Revenue Management Billing license with the Agentforce Employee Agent add-on
USER PERMISSIONS NEEDED
To create an agent:	

Manage AI Agents

OR

Customize Application

Before you begin, make sure you've completed these tasks.

Create an Experience Cloud site by using the Self-Service Billing Portal template
Set Up Community and Partner Access for Agentforce in Revenue Management

These settings establish the trust boundaries that securely loads messages, scripts, and billing data while maintaining controlled access for community users.

After you complete this setup, customers can view billing information and engage with agents in a single Experience Cloud site, reducing support handoffs and administrative overhead.

Enable Service Cloud Admin User Access
In Setup, find and select Users.
Open the admin user record.
Click Edit.
Select Service Cloud User.
Click Save.
If the Service Cloud User option isn’t available:
Update the user’s licenses to include Service Cloud access.
Save your changes.
Reopen the user record and select Service Cloud User.
Update the Embedded Messaging Deployment
Set business hours in enhanced chat to default.
Click Install Code Snippet.
From the Chat Code Snippet, copy the scrt2URL.
Add the SCRT URL as a CSP Trusted Site
In Setup, find and select Trusted URLs.
Click New Trusted URL.
Complete these fields:
OPTION	VALUE
API Name	Embedded_Messaging_SCRT
Trusted Site URL	Paste the SCRT URL you copied earlier
Active	Select
CSP Context	All
Under CSP Directives, select:
connect-src (scripts)
frame-src (iframe content)
Save your changes.
Configure Security and Trusted URLs for the Site
Open your Experience Cloud site in Experience Builder.
Click Settings, and then select Security & Privacy.
Under Trusted Sites for Scripts, click Add Trusted Site.
Add the SCRT script entry:
OPTION	VALUE
Name	SCRT
URL	SCRT URL from the Embedded Messaging JavaScript snippet
Click Add Site.
Click Add Trusted Site again and add the Bootstrap script entry:
OPTION	VALUE
Name	Bootstrap
URL	<site-domain>/assets/js/bootstrap.min.js
Click Add Site.
Configure CORS and Trusted URLs
Configure Salesforce CORS Allowlist.
Add the same domains listed in the CORS configuration to trusted URLs.
Grant Community Users Access to Billing Data
Create a sharing set with read-only access for these objects.
Invoice
Billing Schedule Group
Billing Milestone Plan
Liable Summary
In Setup, find and select Sharing Settings.
Click Edit.
Locate Unit of Measure.
Set the default external acess to Public Read Only.
Save your changes.
