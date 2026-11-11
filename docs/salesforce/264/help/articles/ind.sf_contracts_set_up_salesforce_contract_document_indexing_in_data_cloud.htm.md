---
article_id: ind.sf_contracts_set_up_salesforce_contract_document_indexing_in_data_cloud.htm
title: Set Up Salesforce Contract Document Indexing in Data Cloud for Manual Contract Search Set Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_salesforce_contract_document_indexing_in_data_cloud.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_manual_overview.htm
fetched_at: 2026-10-13
---

# Set Up Salesforce Contract Document Indexing in Data Cloud for Manual Contract Search Set Up

Configure Salesforce CRM connector to stream contract documents and metadata into Data Cloud. This configuration enables AI-powered semantic search through vector embeddings that interpret natural language queries and return relevant results.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To set up contract document indexing:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

SEE ALSO
Map Data Model Objects
Ingest File Attachments from All Salesforce Objects to Data Cloud
Create a Data Stream
In Data Cloud, go to Data Streams, and click New.
Select Salesforce CRM, and click Next.
Click View Objects.
Select Content Document, Content Version, Contract Document Version, and Contract Document Version Content Document objects.
Click Next.
For each object, set Other as the object category.
Some field labels exceed the 40-character limit and aren’t supported during data stream creation. You can replace the recommended labels with custom labels that are under 40 characters.
Update field labels to keep them to less than 40 characters.
OBJECT	ORIGINAL FIELD LABEL	RECOMMENDED FIELD LABEL
ContentDocument	Prevent others from sharing and unsharing	Stop others from sharing and unsharing
ContentVersion	Prevent others from sharing and unsharing	Stop others from sharing and unsharing
ContractDocumentVersion	N/A	N/A
ContractDocVerContentDoc	Contract Document Version Content Document ID	CDV Content Document ID
Related Contract Document Version Content Document ID	Related CDV Content Document ID

To move between objects and update field labels, click the object names in the left panel.

Click the Edit icon next to the field name, change the label, and click Apply.
Click Next, and then click Deploy.
Review and Configure Data Streams
Click a data stream.
Each stream corresponds to one Data Lake Object (DLO).
In the Data Mapping section, click Start.
In the Data Model entities section, click Select Objects.
Search for the corresponding Data Model Object (DMO), and click the Add icon next to it.
DATA LAKE OBJECT (DLO)	DATA MODEL OBJECT (DMO)
ContentDocument	Content Document
ContractDocumentVersion	Contract Document Version
ContractDocVerContentDoc	Contract Doc Version Content Doc
Click Done.
The source DLO fields appear on the left, and the target DMO fields appear on the right.
Search for the field in the DLO.
Search for the corresponding field in the DMO.
To create the mapping, click the DLO field, and then click the matching DMO field.
Map these fields between each DLO and its corresponding DMO.

ContentDocument to Content Document:

DLO FIELD	DMO FIELD
Latest Published Version ID	Latest Published Version
Publish Status	Content Document Publish Status
Size	Content Size

ContractDocumentVersion to Contract Document Version:

DLO FIELD	DMO FIELD
Contract ID	Contract
Status	Contract Document Version Status
Version Number	Version Number

ContractDocVerContentDoc to Contract Doc Version Content Doc:

DLO FIELD	DMO FIELD
ContentDocument ID	Content Document
Contract Document Version ID	Contract Document Version
CDV Content Document ID	Contract Doc Version Content Doc ID

For ContentVersion DLO and Content Document Version DMO, mapping happens automatically.

Click Save & Close.
Similarly, configure the other data streams.
