---
article_id: ind.sf_contracts_configure_external_document_storage_for_document_templates.htm
title: Configure External Document Storage for Document Templates Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_external_document_storage_for_document_templates.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm
fetched_at: 2026-10-13
---

# Configure External Document Storage for Document Templates Manually

To store document template files in a single location, specify the Microsoft OneDrive location in External Document Storage Configuration.

NOTE This step is part of manually integrating Microsoft 365 Azure with Salesforce. To refer to guided setup, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
USER PERMISSIONS NEEDED	 
To configure external document storage:	System Administrator with Azure Tenant Administrator access
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
From Setup, in the Quick Find box, enter External Document, and then select External Document Storage Configuration.
Click New.
Select Document Templates as the target object.
For Record Type, select All.
In Enter Document Storage Identifier, paste the drive ID that you extracted while creating a SharePoint .
In Document Path, specify the path of the folder where you want to store the documents.
For example, DocumentTemplates.
NOTE The folder structure is created inside the SharePoint site that you created earlier.
Select the Name Credential that you created earlier.
See Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually.
Select Microsoft OneDrive as the storage drive type.
Save your changes.
After you save your changes, the record type field for the document template is blank.

See Also

Create a SharePoint Site for Salesforce Contracts
