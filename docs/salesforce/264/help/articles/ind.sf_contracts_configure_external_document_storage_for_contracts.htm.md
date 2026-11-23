---
article_id: ind.sf_contracts_configure_external_document_storage_for_contracts.htm
title: Configure External Document Storage for Contracts Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_external_document_storage_for_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm
fetched_at: 2026-11-23
---

# Configure External Document Storage for Contracts Manually

Set up a shared drive for temporarily storing documents for online editing using Microsoft 365.

NOTE This step is part of manually integrating Microsoft 365 Azure with Salesforce. To refer to guided setup, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
USER PERMISSIONS NEEDED	 
To configure external document storage:	System Administrator with Azure Tenant Administrator access
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

From Setup, in the Quick Find box, enter External Document, and then select External Document Storage Configuration.
Click New.
Select Contract as the target object.
Select Contract Lifecycle Management as the record type.
NOTE Ensure that each contract record type has a corresponding entry in External Document Storage Configuration for storing the generated contract documents by using Microsoft 365.
In External Document Storage Identifier, paste the drive ID that you extracted while creating a SharePoint site.
For Document Path, specify the folder of the folder where you want to store the documents.
For example, Contracts/ContractLifecycleManagement.
NOTE The folder structure is created inside the site that you created earlier.
Select the named credential that you created earlier.
See Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually.
Select Microsoft OneDrive as the storage drive type.
Save your changes.

Create a SharePoint Site for Salesforce Contracts

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_external_document_storage_for_contracts.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
