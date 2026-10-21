---
article_id: ind.sf_contracts_ms365_minimum_pri_overview.htm
title: Manual Integration of Microsoft 365 Azure with Salesforce Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integration_ms365_overview.htm
fetched_at: 2026-10-13
---

# Manual Integration of Microsoft 365 Azure with Salesforce Through Minimum Privilege Setup

Use the Salesforce Contracts Connector for Word add-in to design templates and edit contract documents in Microsoft 365 Word. With manual integration, you control access to specific files or sites, avoiding Global Admin roles and broad write permissions. This approach strengthens security, reduces compliance overhead, and speeds IT approvals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
NOTE You can use guided setup to integrate Microsoft 365 and Azure. See Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Before you begin

Review the prerequisites for Integrating Microsoft 365 and Azure with Salesforce Contracts. The prerequisites cover the Microsoft Azure account and Office 365 license requirements for Azure, and the requirements to use the Microsoft Add-in. See Ways to Set Up Microsoft 365 and Azure Integration with Salesforce.

Configure a Microsoft Azure App Manually Through Minimum Privilege Setup
Configure a Microsoft Azure app to establish a connection between Salesforce and Microsoft.
Configure an Auth Provider for Microsoft App Manually Through Minimum Privilege Setup
Add an Auth. Provider credential to establish a secure connection between Salesforce and Microsoft.
Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually Through Minimum Privilege Setup
Use a Named Credential with External Document Storage Configuration to ensure all generated contract documents and templates are stored in a single, centralized Microsoft OneDrive location without requiring elevated privileges. Only an Office 365 license needs to be assigned to the integration user.
Create a SharePoint Site Manually Through Minimum Privilege Setup
Create a SharePoint site to store document templates and contract documents. When you create a SharePoint site, use the same user details that you used for creating the Azure app. To use an existing site, make sure you’re following it in SharePoint so it appears in the site list.
Configure External Document Storage for Document Templates Manually Through Minimum Privilege Setup
To store document template files in a single location, specify the Microsoft OneDrive location in External Document Storage Configuration.
Configure External Document Storage for Contracts Manually Through Minimum Privilege Setup
Set up a shared drive for temporarily storing documents for online editing by using Microsoft 365.
Deploy and Configure the Microsoft 365 Word Add-In for Salesforce Contracts
Salesforce admins can centrally deploy the Contracts Connector for Word to all or selected users. After it's deployed, users can access and start using the add-in in Microsoft 365 Word.
