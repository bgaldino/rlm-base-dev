---
article_id: ind.sf_contracts_set_up_microsoft_365_and_azure_integration_using_guided_setup.htm
title: Set Up Microsoft 365 and Azure Integration Using Guided Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_microsoft_365_and_azure_integration_using_guided_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integration_ms365_overview.htm
fetched_at: 2026-10-13
---

# Set Up Microsoft 365 and Azure Integration Using Guided Setup

Use the guided setup to integrate Microsoft 365 and Azure with Salesforce Contracts for document storage, online editing, and sharing. Pause and resume the setup at any time without losing saved configurations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.

The Guided Setup is designed to simplify the earlier manual process for Microsoft integration. Many steps that previously had to be done manually are now automated or reduced. Keep in mind that some backend details have changed, for example, the Guided Setup uses Managed Named Credentials instead of the Legacy Named Credentials used in the manual setup.

Before you begin

Review the prerequisites for Integrating Microsoft 365 and Azure with Salesforce Contracts. The prerequisites cover the Microsoft Azure account and Office 365 license requirements for Azure, and the requirements to use the Microsoft Add-in. See Ways to Set Up Microsoft 365 and Azure Integration with Salesforce.

Prepare for Microsoft 365 and Azure Integration Using Guided Setup
Before integrating Microsoft 365 and Azure with Salesforce, complete these prerequisites for a smooth setup process.
Configure a Microsoft Azure App and Create a SharePoint Site Using Guided Setup
Set up a Microsoft Azure app and create a SharePoint site to prepare for integration with Salesforce. This includes generating a client secret, configuring the necessary permissions, and creating a SharePoint site to enable document storage and sharing.
Configure an Auth Provider for Salesforce Contracts Using Guided Setup
Set up an Auth Provider in Salesforce to establish a secure connection with Microsoft 365 and Azure. This process includes creating or selecting an auth provider, configuring the callback URL, managing email notificatinos, and testing the connection to ensure successful integration.
Set Up a Named Credential for Salesforce Contracts Using Guided Setup
A named credential is used to securely connect Salesforce with Microsoft 365 and Azure. Named credentials store authentication details.
Select a SharePoint Site and Drive Using Guided Setup
Select a SharePoint site and drive to securely store and manage contract documents in Salesforce. This step ensures seamless integration with Microsoft SharePoint, enabling document storage, sharing and version control.
Set Up External Document Storage for Salesforce Contracts Using Guided Setup
Set up external document storage for Salesforce contract records and templates, which is used for online editing in Microsoft 365. Specify the target object and record type to determine which records use external storage. Doing this ensures proper organization and access to the documents. A target object and record type combination must be unique and can’t be repeated.
Deploy Salesforce Contracts Connector for Microsoft Word Using Guided Setup
Help users manage contract documents directly in Microsoft Word. You can manually deploy the connector either centrally for all users or for specific users.
