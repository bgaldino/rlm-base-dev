---
article_id: ind.sf_contracts_ms365_minimum_pri_existing_customers.htm
title: Update Microsoft App Registration to Use Minimum-Privilege Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_existing_customers.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm
fetched_at: 2026-10-13
---

# Update Microsoft App Registration to Use Minimum-Privilege Permissions

If you previously set up the Microsoft Add-in by using advanced permissions such as Files.ReadWrite.All and User.ReadWrite.All, you can update your app registration to use Sites.Selected, User.Read, and User.ReadBasic.All. This reduces security risks, limits access to specific SharePoint sites, and supports simplified access management without impacting document generation.

REQUIRED EDITIONS
NOTE To use the guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To modify API permissions and grant site access via Graph Explorer and update authentication scopes and app properties:	

CLM Admin User

OR

Microsoft 365 Admin

AND

Azure App Registration Owner

Prerequisites:

Set up your Microsoft app registration to support Salesforce integration for document storage.
Identify the SharePoint site configured in ExternalDocStorageConfig for document storage.
Make sure you have access to Microsoft Graph Explorer.
Remove write permissions from App Registration.
Log in to Microsoft Azure.
To go to App registrations, search for Azure AD B2C, click Manage, and select App registrations.
Select your Salesforce app.
Go to API permissions and remove Files.ReadWrite.All.
Repeat the steps to remove User.ReadWrite.All.
Add read permissions.
In API permissions, select Add a permission > Microsoft Graph > Application permissions.
Search for and add Sites.Selected, User.Read, and User.ReadBasic.All permissions.
Click Grant admin consent.
Retrieve your SharePoint site ID.
Go to Graph Explorer and log in with your Microsoft credentials.
Set the method to GET, API version to v1.0, and URL to: https://graph.microsoft.com/v1.0/me/followedSites
Run the query and copy the id of the SharePoint site used for document storage.
Grant the Microsoft Azure app access to your SharePoint site.
In Graph Explorer, set the method to POST and the URL to: https://graph.microsoft.com/v1.0/sites/<site_id>/permissions.
Replace <site_id> with the Share Point site ID.
Go to the Modify permissions tab and ensure Sites.FullControl.All consent is provided.
Paste this code in the request body:
{
  "roles": ["write"],
  "grantedToIdentities": [{
    "application": {
      "id": "<Application_Id>",
      "displayName": "Salesforce App"
    }
  }]
}

Replace <Application_Id> with the Client ID from the Azure App Registration's Overview tab.
Go to the Headers tab and add: Content-Type: application/json.
Run the query to assign the permissions.
Update the scope in Salesforce Auth Provider.
From Setup, in the Quick Find box, enter Auth. Providers, and then select Auth. Providers.
Edit the relevant Microsoft provider.
Update the scope to: offline_access openid User.Read User.ReadBasic.All Sites.Selected.
Save the changes.

After updating the scopes, verify that document generation from Salesforce to the SharePoint site works as expected. Optionally, revoke Sites.FullControl.All from Graph Explorer permissions after site access is confirmed.

SEE ALSO
Microsoft Graph API: Site Permissions
Microsoft Graph Explorer
