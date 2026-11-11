---
article_id: ind.sf_contracts_set_up_external_document_storage.htm
title: Set Up External Document Storage for Salesforce Contracts Using Guided Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_external_document_storage.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_microsoft_365_and_azure_integration_using_guided_setup.htm
fetched_at: 2026-10-13
---

# Set Up External Document Storage for Salesforce Contracts Using Guided Setup

Set up external document storage for Salesforce contract records and templates, which is used for online editing in Microsoft 365. Specify the target object and record type to determine which records use external storage. Doing this ensures proper organization and access to the documents. A target object and record type combination must be unique and can’t be repeated.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To access the Microsoft 365 and Azure Integration guided setup	CLM Admin User
NOTE When you use external document storage with Microsoft 365 and a minimum-privilege access model, only the docgen designer who creates a Microsoft 365 document can edit the document by default. To enable shared editing when multiple designers work in the same org, create a dedicated folder in Microsoft SharePoint, grant access to the required designers, and configure a separate external document storage configuration in Salesforce that points to this folder. Thus, preserving the minimum-privilege security model while supporting collaboration.
In the guided setup, click Set Up External Document Storage to expand the step.
Select a target object, and then select a corresponding record type.
In the Document Path field, enter the storage path starting from the root directory (for example, salesforce/contracts). If the field is left blank, the root directory is considered as the storage path.
Click Add and save your changes.
