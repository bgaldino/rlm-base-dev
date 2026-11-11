---
article_id: ind.sf_contracts_ms365_minimum_pri_azure_app.htm
title: Configure a Microsoft Azure App Manually Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_azure_app.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_ms365_minimum_pri_overview.htm
fetched_at: 2026-10-13
---

# Configure a Microsoft Azure App Manually Through Minimum Privilege Setup

Configure a Microsoft Azure app to establish a connection between Salesforce and Microsoft.

REQUIRED EDITIONS
NOTE To use a guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To configure a Microsoft Azure App:	User without admin privileges in Azure
Open Microsoft Azure.
Log in to your Microsoft Azure account.
To go to App registrations, search for Azure AD B2C, click Manage, and select App registrations.
Click New Registrations.
Enter the details.
Enter a name for the app.
For example, MicrosoftApp.
For supported account types, select Accounts in this organizational directory only (Salesforce -SFDC-CLM only - Single tenant).
Click Register.
Note the Application (client) ID.
Add permissions.
Click API permissions.
Click Add a permission | Microsoft Graph Delegated permissions.
In Select permissions, enter Sites.Selected.
Select Sites.Selected permission, and click Add permissions.
Similarly, add these permissions.
openId
Offline_access
User.Read
User.Read Basic.All
Request your Global Administrator to grant consent for the permissions you added, by clicking Grant admin consent for {TenantName}.
When the Global Administrator clicks Yes, the status changes to Granted for Salesforce - {TenantName} for all permissions.
Verify that the status has changed to Granted for Salesforce - {TenantName} for all permissions.
Add the new client secret.
Click Certificates & secrets.
Click New client secret.
The Add a client secret window opens.
Enter a description for the client secret.
For example, MicrosoftApp.
Specify an expiration timeframe.
Click Add.
A client secret value gets created.
Immediately copy and save the Client Secret value.
If you don't save the client secret value immediately, you need to create a new value. You need this copied client secret value while configuring Auth. Provider. Automatic encryption prevents retrieval of the client secret value.
