---
article_id: ind.sf_contracts_integration_ms365_overview.htm
title: Ways to Set Up Microsoft 365 and Azure Integration with Salesforce
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_integration_ms365_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Ways to Set Up Microsoft 365 and Azure Integration with Salesforce

Salesforce recommends using guided setup to integrate Microsoft 365 and Azure. Guided Setup provides a step-by-step, automated process that simplifies configuration and reduces errors. If you want to set up the integration manually, use the manual setup to configure each step with minimum privileges.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
Comparison of Microsoft 365 and Azure Integration Setups
SETUP METHOD	KEY BENEFITS


Salesforce recommends this guided setup method

Set Up Microsoft 365 and Azure Integration Using Guided Setup

	
Step-by-step configuration
Automates many manual tasks
Uses Managed Named Credentials
Can pause and resume setup

Manual Integration of Microsoft 365 Azure with Salesforce Through Minimum Privilege Setup	
Eliminates Global or User Admin roles
Uses only least-privilege, approved permissions
Reduces compliance overhead
Speeds up IT approval and shortens implementation time
Prerequisites for Azure
Access to log in to Azure.
An active Microsoft Azure account.
An Office 365 license, such as E1, assigned to your users.
Prerequisites for the Microsoft add-in
Make sure the required Microsoft 365 licenses are assigned to your users. See Personas and Permission Set Licenses for Salesforce Contracts
The integration user who authenticates the named credential, or the user who creates the Microsoft Azure app, doesn’t need Global Administrator or User Administrator roles. Only minimum privileges are required.
Make sure, the third-party cookies are enabled in your browser for the add-in to function.
In Google Chrome, go to Settings | Privacy and security | Third-party cookies, and select Allow third-party cookies.
In Safari, go to Settings | Privacy. Under Website tracking, select Prevent cross-site tracking.
In Firefox, go to Settings | Privacy & Security. Select the Custom radio button, and under Tracking content, select In all windows.
Set Up Microsoft 365 and Azure Integration Using Guided Setup
Use the guided setup to integrate Microsoft 365 and Azure with Salesforce Contracts for document storage, online editing, and sharing. Pause and resume the setup at any time without losing saved configurations.
Manual Integration of Microsoft 365 Azure with Salesforce Through Minimum Privilege Setup
Use the Salesforce Contracts Connector for Word add-in to design templates and edit contract documents in Microsoft 365 Word. With manual integration, you control access to specific files or sites, avoiding Global Admin roles and broad write permissions. This approach strengthens security, reduces compliance overhead, and speeds IT approvals.
Integrate Microsoft 365 and Azure with Salesforce Contracts Manually
Use the Salesforce Contracts Connector for Word add-in to design and maintain document templates, and create and edit contract documents using Word in Microsoft 365.
Insert Salesforce Contracts Connector for Word Add-In App Into Microsoft 365 Word
After your Salesforce admin deploys the Salesforce Contracts Connector for Word add-in, you can insert the app from Admin Managed.
Supported Browsers and Devices for Salesforce Contracts Connector for Word Add-In
The add-in supports the Android, Microsoft Windows, and iOS operating systems, and the latest stable browser versions of Apple® Safari®, Mozilla Firefox, and Google Chrome™.
Microsoft 365 Frequently Asked Questions (FAQs)
This document provides answers to the common questions about integrating Salesforce Contracts with Microsoft 365 and Azure.
Configure Private Online External Review
CLM admin must complete a few configurations so that contract authors can initiate private online external reviews. It includes creating a Digital Experience site, setting up a contract-type config setting for external review, and enabling the external review feature from the Microsoft 365 and Azure Integration guided setup.
Considerations When Migrating Microsoft 365 Word Templates Across Environments
When you move Microsoft 365 document templates between Salesforce orgs, such as from a sandbox to a production org, the structure, clause relationships, and section-level access controls are preserved. Before migrating a template, keep these considerations in mind.
