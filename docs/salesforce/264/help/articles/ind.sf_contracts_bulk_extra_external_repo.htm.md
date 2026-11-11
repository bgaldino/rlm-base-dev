---
article_id: ind.sf_contracts_bulk_extra_external_repo.htm
title: Connect an External Repository for Bulk Contract Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_external_repo.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_bulk_extra_overview.htm
fetched_at: 2026-10-13
---

# Connect an External Repository for Bulk Contract Extraction

Connect an external document repository to Data Cloud so that bulk extraction can access your contract files without uploading them to Salesforce storage.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To connect an external repository for bulk extraction:	

CLM Admin User

AND

Data Cloud Architect

AND

Access credentials to the external repository

Make sure that Data Cloud is provisioned in your org.
NOTE Creating the unstructured data lake object (UDLO and UDMO) in Data Cloud doesn’t require you to Enable Semantic Search with System Defaults. For Amazon S3 and Google Cloud Storage (GCS), the source file downloads automatically and is available when you review the extraction result. For other connector types, you need to download the source from the external system and attach it to complete review. Confirm source-file behavior for your connector.
From Setup, in the Quick Find box, enter Data Cloud, and then select Data Cloud Setup.
Click Other Connectors.
Click New to create a connector for your repository type.

The supported repository types are SharePoint, Google Drive, Amazon S3, Azure Blob Storage, and Google Cloud Storage. For connector-specific setup steps, open the topic in see also that matches your repository type.

Enter the authentication details, and test the connection.
Create an unstructured data lake object (UDLO) to reference your contract documents in your external repository.
The exact steps depend on your repository and connector. Open the topic in see also that matches your repository type. Your external repository connects, and Data Cloud ingests the contract documents. You can now create a bulk extraction configuration.
SEE ALSO
Amazon S3 Connector
Google Cloud Storage Connector
Google Drive Connector
Microsoft SharePoint Connector
Microsoft Azure Blob Storage Connector
