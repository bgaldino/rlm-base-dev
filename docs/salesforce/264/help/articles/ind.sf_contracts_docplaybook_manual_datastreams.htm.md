---
article_id: ind.sf_contracts_docplaybook_manual_datastreams.htm
title: Manually Configure Document Playbook Data Streams
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_manual_datastreams.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_manual_index.htm
fetched_at: 2026-10-13
---

# Manually Configure Document Playbook Data Streams

Create and map the data streams that ingest Document Playbook content and file metadata into Data 360 (Data Cloud). Complete this task after you give the Data Cloud Salesforce Connector the required permissions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To manually configure Document Playbook data streams:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

Document Playbook Designer, CLM Admin User, and Contracts AI User

Before you begin, configure the Data Cloud Salesforce Connector. See Manually Configure Document Playbook Data Streams and Search Index.

Create data streams to ingest Document Playbook content and file metadata into Data 360 (Data Cloud).
In Data Cloud, go to Data Streams, and click New.
Select Salesforce CRM, and click Next.
Click View Objects.
Select these objects, and then click Next.
ContentDocument
ContentVersion
ContentDocumentLink
DocumentPlaybook
DocumentPlaybookVersion
For each object, select Other as the object category.
If a field label exceeds 40 characters, you must shorten it. Click the Edit icon next to the field name, update the label, and click Apply.
Click Next, and then click Deploy.
Configure the data streams.
Repeat these substeps for each data stream you created. Each stream corresponds to a data lake object (DLO) that you map to a data model object (DMO). Use the field mapping tables in the substeps below to pair each DLO field with its DMO field.
Click a data stream.
A data stream name has the "_Home" suffix appended to the object name. For example, ContentDocument is ContentDocument_Home.
In the Data Mapping section, click Start.
In the Data Model entities section, click Select Objects.
Search for the corresponding DMO, and click the Add icon to map the objects.
DATA LAKE OBJECT (DLO)	DATA MODEL OBJECT (DMO)
ContentDocument	Content Document
ContentVersion	Content Document Version
ContentDocumentLink	Content Document Relationship
DocumentPlaybook	Document Playbook
DocumentPlaybookVersion	Document Playbook Version
Click Done.
The source DLO fields appear on the left, and the target DMO fields appear on the right.
Map each DLO field to its corresponding DMO for Content Document.
DATA LAKE OBJECT (DLO)	DATA MODEL OBJECT (DMO)
Latest Published Version ID	Latest Published Version
Publish Status	Content Document Publish Status
Size	Content Size
Content Modified Date	Content Modified DateTime
Map each DocumentPlaybook DLO field to the Document Playbook DMO fields.
DATA LAKE OBJECT (DLO) FIELD	DATA MODEL OBJECT (DMO) FIELD
CreatedById	CreatedById
CreatedDate	CreatedDateTime
Description	Description
Id	Id
LastModifiedById	LastModifiedById
LastModifiedDate	LastModifiedDateTime
Name	DocumentPlaybookName
Status	Status
NOTE The DLO type for ContentVersion is Directory Table. For ContentVersion (DLO) to Content Document Version (DMO), mapping happens automatically on the user's behalf.
Click Save & Close.
Map DocumentPlaybookVersion DLO to the Document Playbook Version DMO.
DATA LAKE OBJECT (DLO) FIELD	DATA MODEL OBJECT (DMO) FIELD
CreatedById	CreatedById
CreatedDate	CreatedDateTime
Description	Description
DocumentPlaybookId	DocumentPlaybookId
Id	Id
LastModifiedById	LastModifiedById
LastModifiedDate	LastModifiedDateTime
Name	DocumentPlaybookVersionName
Status	Status
VersionNumber	VersionNumber
Map each ContentDocumentLink DLO field to the Content Document Relationship DMO.
DATA LAKE OBJECT (DLO) FIELD	DATA MODEL OBJECT (DMO) FIELD	NOTES
ContentDocument : Content Document Id	Content Document Relationship Id	Primary Key
LinkedEntity	Related Item	 
SystemModStamp	Last Modified Date	 

Next, create the hybrid search index that risk analysis uses. See Manually Create a Document Playbook Search Index.
