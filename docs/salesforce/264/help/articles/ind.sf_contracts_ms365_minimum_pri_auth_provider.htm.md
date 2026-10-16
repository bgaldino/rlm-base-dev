---
article_id: ind.sf_contracts_ms365_minimum_pri_auth_provider.htm
title: Configure an Auth Provider for Microsoft App Manually Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_auth_provider.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_ms365_minimum_pri_overview.htm
fetched_at: 2026-10-13
---

# Configure an Auth Provider for Microsoft App Manually Through Minimum Privilege Setup

Add an Auth. Provider credential to establish a secure connection between Salesforce and Microsoft.

NOTE To use a guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To configure Auth. Provider:	CLM Admin User

Ensure that Application (client) ID and Client Secret Value correspond to your Azure account. If the ID and value don't match with your Azure account, the add-in fails to function correctly or doesn't load as expected, and can result in graph API issues.

From Setup, in the Quick Find box, enter Auth. Providers, and then select Auth. Providers.
Click New, and select Open ID Connect as the provider type.
Enter MicrosoftApp as the Auth Provider name.
The URL automatically gets suffixed with MicrosoftApp.
In Consumer Key, enter your Azure App's Application (client) ID.
In Consumer Secret, enter your Azure App's Client Secret Value.
In Authorize Endpoint URL, enter https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize
In Token Endpoint URL, enter https://login.microsoftonline.com/organizations/oauth2/v2.0/token
In User Info Endpoint URL, enter https://graph.microsoft.com/oidc/userinfo
In Default Scopes, enter Sites.Selected offline_access openid User.Read User.ReadBasic.All.
NOTE Ensure that Default Scopes matches the API permissions that you added to your Microsoft Azure account. See Configure a Microsoft Azure App Manually Through Minimum Privilege Setup.
Ensure Send client credentials in header is unselected.
Select Send access token in header and Include Consumer Secret in SOAP API Responses.
For Registration Handler, click Automatically create a registration handler template.
In Execute Registration As, select your Salesforce admin account.
Save your changes.
Your auth provider details are saved, and Salesforce Configuration URLs are generated.
In Salesforce Configurations, verify that these URLs are generated.

Test-Only Initialization URL

Single Sign-On Initialization URL

Existing User Linking URL

OAuth-Only Initialization URL

Callback URL

Single Logout URL

If an experience cloud site is available in your Salesforce instance, expand Experience Cloud Sites and verify that these URLs are generated.

Test-Only Initialization URL

Single Sign-On Initialization URL

Existing User Linking URL

OAuth-Only Initialization URL

Callback URL

Save your changes.

After you save the Auth. Provider details, a Registration Handler Apex Class gets created. For example, AutocreatedRegHandler1234567890123.
Disable automatic synchronization of username and email address.
When you link Salesforce to Microsoft Azure, the system automatically updates your Salesforce username and email address with your Microsoft Azure account details. You can turn off this automatic update.
Click the Registration Handler Apex Class link.
Click Edit.
Search for the updateUser method and remove or comment out this code:
//u.email = data.email;
        //u.lastName = data.lastName;
        //u.firstName = data.firstName;
Save your changes.
Add the Callback URL.
Go back to your auth provider.
In the Salesforce Configuration section, copy the callback URL.
Open your Microsoft Azure account, and click Overview.
Next to Redirect URLs, click Add a Redirect URL.
Select Add a platform | Web.
Paste the callback URL in Redirect URIs.
If available, select Access tokens (used for implicit flows) and ID tokens (used for implicit and hybrid flows).
Click Configure.
If you have a partner community set up, go to the Auth. Provider in your Salesforce org.
From the Experience Cloud Sites section, copy the callback URL.
Open your Microsoft Azure account, and click Authentication.
Go to Web | Redirect URLs , and click Add URL.
Paste the Experience Cloud Site callback URL, and save your changes.
Test if your Auth. Provider authentication was successful.
From the Salesforce Configuration section, copy the Test-Only Initialization URL.
Paste the URL in the address bar, and press Enter.

This is a sample text that appears:
