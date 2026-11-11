---
article_id: ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm
title: Integrate Microsoft 365 and Azure with Salesforce Contracts Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integration_ms365_overview.htm
fetched_at: 2026-10-13
---

# Integrate Microsoft 365 and Azure with Salesforce Contracts Manually

Use the Salesforce Contracts Connector for Word add-in to design and maintain document templates, and create and edit contract documents using Word in Microsoft 365.

IMPORTANT If you are a new customer, Salesforce recommends using guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
NOTE If you’re an existing customer who set up the integration with admin privileges, you can update to use minimum privileges for setup, see Update Microsoft App Registration to Use Minimum-Privilege Permissions.
Prerequisites
Access to log in to Azure.
An active Microsoft Azure account.
An Office 365 license, such as E1 or Microsoft 365 Business Premium, assigned to your users.
Assign Personas and Permission Set Licenses for Salesforce Contracts
Ensure that the user that authenticates the named credential after creating a named credential is the same user who creates the Microsoft Azure app and has User Administrator permissions in Azure.
Configure a Microsoft Azure App for Salesforce Contracts
Configure a Microsoft Azure app to establish a connection between Salesforce Contracts and Microsoft 365. To connect Microsoft 365 with other Salesforce products, refer to the Salesforce documentation for that product.
Configure an Auth Provider for Salesforce Contracts Microsoft Integration
Add an Auth Provider credential to establish a secure connection between Salesforce Contracts and Microsoft 365.
Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually
Create a named credential to connect Salesforce Contracts to External Document Storage. The authenticating user is required to be the same user who created the Microsoft Azure app and to have User Administrator permissions in Azure.
Create a SharePoint Site for Salesforce Contracts
Create a site in SharePoint to store Salesforce Contracts document templates and contract documents.
Configure External Document Storage for Contracts Manually
Set up a shared drive for temporarily storing documents for online editing using Microsoft 365.
Configure External Document Storage for Document Templates Manually
To store document template files in a single location, specify the Microsoft OneDrive location in External Document Storage Configuration.
Deploy Salesforce Contracts Connector for Word Add-In App to Users Manually
Through a centralized deployment, Salesforce Admins can deploy and assign the app to all or specific users. Users can then insert the add-in into their Microsoft 365 Word.
Update Microsoft App Registration to Use Minimum-Privilege Permissions
If you previously set up the Microsoft Add-in by using advanced permissions such as Files.ReadWrite.All and User.ReadWrite.All, you can update your app registration to use Sites.Selected, User.Read, and User.ReadBasic.All. This reduces security risks, limits access to specific SharePoint sites, and supports simplified access management without impacting document generation.
