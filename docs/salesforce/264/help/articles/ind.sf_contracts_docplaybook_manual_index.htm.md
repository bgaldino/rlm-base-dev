---
article_id: ind.sf_contracts_docplaybook_manual_index.htm
title: Manually Configure Document Playbook Data Streams and Search Index
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_manual_index.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_setup.htm
fetched_at: 2026-10-13
---

# Manually Configure Document Playbook Data Streams and Search Index

If you don't want to use the index that the Document Playbook Data Kit creates, manually set up the data streams and search index that ingest and index playbook content in Data 360. Start here to give the Data Cloud Salesforce Connector the required permissions, and then complete the data streams and search index child tasks. The Document Playbook Data Kit deployment remains the recommended configuration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To manually configure Document Playbook indexing:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

Document Playbook Designer, CLM Admin User, and Contracts AI User

Before you begin:

Turn on Document Playbook Management from Document Playbook Settings. See Turn On Document Playbook Management.
Set up Data 360 and provide access to the data space that stores Document Playbook data. See Turn On Data Cloud.
Turn on Einstein Generative AI. See Set Up Einstein Generative AI.
From Setup, in the Quick Find box, enter Permission Sets, select Permission Sets, and then click Data Cloud Salesforce Connector.
Give the Data Cloud Salesforce Connector the permissions required to ingest, index, and search document playbook content in Data 360. With this access, Data 360 can read Document Playbook records and files. The Document Playbook Data Kit configures this access automatically when you use the recommended setup.
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

Next, create and map the data streams that ingest Document Playbook content into Data 360. See Manually Configure Document Playbook Data Streams.

Then, create the hybrid search index that risk analysis uses. See Manually Create a Document Playbook Search Index.

Manually Configure Document Playbook Data Streams
Create and map the data streams that ingest Document Playbook content and file metadata into Data 360 (Data Cloud). Complete this task after you give the Data Cloud Salesforce Connector the required permissions.
Manually Create a Document Playbook Search Index
Create the hybrid search index that Salesforce uses to match contract sections against document playbook content during risk analysis. Complete this task after you configure the Document Playbook data streams.
