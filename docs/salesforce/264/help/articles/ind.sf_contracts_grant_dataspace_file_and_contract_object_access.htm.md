---
article_id: ind.sf_contracts_grant_dataspace_file_and_contract_object_access.htm
title: Grant Dataspace, File, and Contract Object Access
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_grant_dataspace_file_and_contract_object_access.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_overview.htm
fetched_at: 2026-10-13
---

# Grant Dataspace, File, and Contract Object Access

Update permission sets to allow users to access contract data in the default dataspace, query non-vetoed contract documents using Fileforce, and read CLM contract entities. These permissions are required to ingest, index, and search contract files in Data Cloud for contract search.

REQUIRED EDITIONS
NOTE These configurations apply to both Data Kit deployment and manual setup for Contract Search. The steps are largely the same in both approaches, with minor differences such as tagging for Data Lake Objects (DLOs) and Data Model Objects (DMOs) has been called out where applicable. See Set Up Contract Search By Using Prebuilt Data Kit.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To grant access for dataspace, file, and contract object:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

SEE ALSO
Manage Data Spaces
Associate a Permission Set with a Data Spaces
Assign Dataspace Access to Data Cloud Architect, and One Users
To configure Home orgs.
From Setup, enter Permission Sets in the Quick Find box, and select Permission Sets.
Select the Data Cloud Architect permission set.
In the Apps section, select Data Cloud Data Space Management.
Select Edit.
Select the required dataspaces.
Save your changes.
From Setup, enter Permission Sets in the Quick Find box, and select Permission Sets.
Select the Data Cloud User permission set.
In the Apps section, select Data Cloud Data Space Management.
Select Edit.
Select the required dataspaces.
Save your changes.
To configure Companion orgs.
For information on Companion orgs, see Data Cloud One.
From Setup, enter Permission Sets in the Quick Find box, and select Permission Sets.
Select the Data Cloud One permission set.
In the Apps section, select Data Cloud Data Space Management.
Select Edit.
Select the required dataspaces.
Save your changes.
Enable File Access for Contract Documents
Return to Permission Sets, and select Data Cloud Salesforce Connector.
In the Apps section, select App Permissions.
Select Edit.
Under Content, select Query Non Vetoed Files.
Save your changes.
Allow Data Cloud to Read Contract Objects
In the same Data Cloud Salesforce Connector permission set, go to System Permissions.
Select Edit.
Select the following permissions:
Allows users to generate contract documents and execute contract lifecycles
Allows users to generate contract documents and manage contract lifecycles in Digital Experience Partner sites
Allows admin users to monitor and manage contract lifecycles
Save your changes.
Grant Object-Level Access to Contracts
In the same Data Cloud Salesforce Connector permission set, go to the Object Settings section.
Select Contracts.
Verify that the Read and View All Records checkboxes are selected. If not, select Edit and enable the checkboxes.
Save your changes.
