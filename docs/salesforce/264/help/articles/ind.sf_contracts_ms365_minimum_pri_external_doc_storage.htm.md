---
article_id: ind.sf_contracts_ms365_minimum_pri_external_doc_storage.htm
title: Configure External Document Storage for Document Templates Manually Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_external_doc_storage.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_ms365_minimum_pri_overview.htm
fetched_at: 2026-10-13
---

# Configure External Document Storage for Document Templates Manually Through Minimum Privilege Setup

To store document template files in a single location, specify the Microsoft OneDrive location in External Document Storage Configuration.

REQUIRED EDITIONS
NOTE To use a guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To configure external document storage:	CLM Admin User
NOTE When you use external document storage with Microsoft 365 and a minimum-privilege access model, only the docgen designer who creates a Microsoft 365 document can edit the document by default. To enable shared editing when multiple designers work in the same org, create a dedicated folder in Microsoft SharePoint, grant access to the required designers, and configure a separate external document storage configuration in Salesforce that points to this folder. Thus, preserving the minimum-privilege security model while supporting collaboration.
From Setup, in the Quick Find box, enter External Document, and then select External Document Storage Configuration.
Click New.
Select Document Templates as the target object.
For record type, select All.
In Enter Document Storage Identifier, paste the drive ID that you extracted while creating a SharePoint .
In Document Path, specify the path of the folder where you want to store the documents.
For example, DocumentTemplates.
NOTE The folder structure is created inside the SharePoint site that you created earlier.
Select the named credential that you created earlier.
See Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually Through Minimum Privilege Setup.
Select Microsoft OneDrive as the storage drive type.
Save your changes.
