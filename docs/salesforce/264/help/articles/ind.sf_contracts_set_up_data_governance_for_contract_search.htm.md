---
article_id: ind.sf_contracts_set_up_data_governance_for_contract_search.htm
title: Set Up Data Governance for Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_data_governance_for_contract_search.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_overview.htm
fetched_at: 2026-10-13
---

# Set Up Data Governance for Contract Search

Use Data Governance in Data Cloud to secure access to contract document chunks used in vector search. Configure a custom permission to make sure that only authorized access is granted to contract-related data. This setup is optional and required only if you want to replicate your object-level security configurations from the core to Data Cloud.

REQUIRED EDITIONS
NOTE Most of the setup steps for Contract Search data governance in home and companion orgs are the same whether you configure manually or through the prebuilt data kit. The only differences are in how you tag the data lake objects (DLOs) and data model objects (DMOs). Salesforce recommends setting up Contract Search by deploying the Contract Document data kit. See Set Up Contract Search By Using Prebuilt Data Kit.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To set up data governance:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

NOTE To use Data Governance features, grant permissions to the listed objects per your chosen policy according to Assign Data Access. If you have more than one data space, you must grant access to objects in each data space. Object names in non default data spaces follow the convention of <DataSpace Prefix>_<Object Name>.
Create a custom permission.
In Setup, find and select Custom Permissions.
Click New.
Enter AllowContractSearch as the label.
Leave the remaining fields blank.
Save your changes.
Create a custom permission set.
In Setup, find and select Permission Sets.
Click New.
Enter Label as AllowContractSearchPermSet.
Leave the remaining fields blank.
Save your changes.
Assign the custom permission to the permission set.
Open AllowContractSearchPermSet.
In the Apps section, click Custom Permissions.
Click Edit and move the AllowContractSearch permission from Available Custom Permissions to Enabled Custom Permissions.
Save your changes.
Assign the Contract Search permission set to the integration user.
In Setup, find and select Users.
Click Integration User.
In the Permission Set Assignments section, click Edit Assignments.
Move AllowContractSearchPermSet from Available Permission Sets to Enabled Permission Sets.
Save your changes.
NOTE Similarly, assign the permission set to other Data Cloud Architect users who need access to contract-related DLOs and DMOs.
Delete the default All Data Access policy.
NOTE This step is required for the existing orgs but not for the new orgs.
In App Launcher, find and select Data Governance.
From the left panel, click Policies.
Click the more actions icon, and then select Delete.
Click Delete.
Create a tag for Contract Search.
From the left panel, click Tags.
Click New.
Enter the tag name as Contract Search Tag.
Click Next and save your changes.
Assign the tag to Contract Search DLOs and DMOs.
In the Tags page, click Tagging Manager.
By default, Data Lake Objects is selected in the dropdown. Tag the required DLOs first, then switch to Data Model Objects and tag the required DMOs.
In the Data Space dropdown, select the appropriate data space.
In the object list, click the name of the object (for example, ContentDocument).
Click Attach New Tag.
In the search box, enter and select Contract_Search_Tag.
Select the Add these tags to <object name> checkbox.
Save your changes.
Similarly, assign the tag to each object.
The Contract Document chunk and index DLOs and DMOs that you tag for Contract Search differ slightly between manual and prebuilt data kit setups. You don't need to create DLOs for Companion orgs. Only tag the DMO tags as described for both Home and Companion org.
DATA LAKE OBJECT (DLO)	DATA MODEL OBJECT (DMO)
ContractDocVerContentDoc	Contract Doc Version Content Doc
ContractDocumentVersion	Contract Document Version

Data kit setup: Contract Document Search chunk
Manual setup: Contract Document Version chunk
	
Data kit setup: Contract Document Search chunk
Manual setup: Contract Document Version chunk


Data kit setup: Contract Document Search index
Manual setup: Contract Document Version index
	
Data kit setup: Contract Document Search index
Manual setup: Contract Document Version index

After tagging all required DLOs, switch the dropdown to Data Model Objects and tag the corresponding DMOs.

Click Done.
Create an access policy for the tagged DMOs
From the left panel, click Policies.
Click New, and then click Next.
In the new tab, enter the policy name as AllowContractSearchAccess.
Set the policy name: AllowContractSearchAccess.
Click Next.
Set these values:
FIELD	VALUE
Resource	Object
Action	Allow Access
Variable	Tag
Operator	Is In
Value	Contract Search Tag
From the left panel, click the Users icon.
Set these values:
FIELD	VALUE
Take Action On	All users who meet all conditions (AND)
Variable	Assigned Permission
Operator	Is In
Value	AllowContractSearch
Click Save and Activate.
