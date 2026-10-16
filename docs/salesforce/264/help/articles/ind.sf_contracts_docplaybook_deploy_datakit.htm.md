---
article_id: ind.sf_contracts_docplaybook_deploy_datakit.htm
title: Deploy the Document Playbook Data Kit
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_deploy_datakit.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_setup.htm
fetched_at: 2026-10-13
---

# Deploy the Document Playbook Data Kit

Use the Document Playbook Data Kit to create the data streams and hybrid search index that ingest and index playbook content in Data 360. The data kit is a single deployable bundle and is the recommended setup path.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To deploy the Document Playbook Data Kit:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

Document Playbook Designer, CLM Admin User, and Contracts AI User

Before you begin:

Assign a Data Cloud Architect to the admin who deploys the data kit.
Turn On Document Playbook Management.
Turn On Data Cloud.
Turn on Einstein Generative AI. See Set Up Einstein Generative AI.
On the Document Playbook Settings page, go to the Document Playbook Data Kit section.
Give the applicable users and the connector the permissions required to ingest, index, and search document playbook content in Data 360. With this access, Data 360 can read Document Playbook records and files.
From Setup, in the Quick Find box, enter Permission Sets, select Permission Sets, and then click Data Cloud Salesforce Connector.
Provide app permissions.
Under Data Cloud Salesforce Connector, click App Permissions.
Click Edit, and select Query Non Vetoed Files.
Save your changes.
Provide system permissions.
Under Data Cloud Salesforce Connector, click System Permissions.
Click Edit.
Select Create and manage document playbooks.
Select Access the document playbooks.
Save your changes.
Provide object permissions.
Under Data Cloud Salesforce Connector, click Object Permissions.
Click Document Playbook, and then click Edit.
Select Read and View All Records.
Add the same permissions to Document Playbook Version.
Provide data space permissions.
Under Data Cloud Salesforce Connector, click Data Cloud Data Space Management.
Click Edit, and select the required data spaces.
Save your changes.
From the permission sets, click Data Cloud Architect, and then click Data Cloud Data Space Management.
Click Edit, and select the required data spaces.
Save your changes.
Click Deploy the Document Playbook Data Kit to your org.
Deploy the data kit once per data space.
In the Deploy document playbook data kit window, select a data space, and then click Deploy.
The data kit creates batch upsert data streams for the Salesforce CRM objects.
In Data Kit Deployment History, refresh the page after a few minutes to check the deployment status.
The deployment runs asynchronously and can take a few minutes. You can track the progress in the Data Kit Deployment History table.

If the row shows failed, review the reason in Deployment Error, resolve the issue, and rerun the deployment.

To point Document Playbook at the deployed index, see Configure Document Playbook Indexing.
