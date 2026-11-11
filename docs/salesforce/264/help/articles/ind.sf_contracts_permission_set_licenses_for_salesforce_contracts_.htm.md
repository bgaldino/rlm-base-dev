---
article_id: ind.sf_contracts_permission_set_licenses_for_salesforce_contracts_.htm
title: Personas and Permission Set Licenses for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_permission_set_licenses_for_salesforce_contracts_.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_licenses.htm
fetched_at: 2026-10-13
---

# Personas and Permission Set Licenses for Salesforce Contracts

Permission set licenses give users incremental access to features that aren't included in their user licenses. Users can be assigned any number of permission set licenses. Personas define what different types of users can do in Salesforce Contracts. Each persona is mapped to specific responsibilities and permission sets that determine the level of access a user has.

There are a number of permission set licenses available for Salesforce Contracts, Omnistudio, and Document Generation users. You need a combination of licenses:

Omnistudio licenses (Omnistudio or Omnistudio User) to use Document Generation application with Data Mappers.
DocGen licenses (DocGen Designer, DocGen User, DocGen Runtime for Community Users) to generate to generate contracts documents.
Platform Licenses
PLATFORM LICENSE	DESCRIPTION
ContractManagement	Enables Salesforce Contracts features in the org.
DocGen	Enables Document Generation features in the org.
Create Users and Profiles

To begin, create users for Salesforce Contracts. Then assign users the appropriate permission sets. To help you plan, refer to the personas table. When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce. Remember, users can have only one profile, but can have many permission sets assigned to them.

Before you being creating users and profiles, and assigning them, we recommend checking out these resources.

View and Manage Users
Create or Clone Profiles
View and Manage Your Permission Set Licenses
Salesforce Contracts Licenses

Use this table to understand the available personas and choose the right permission sets for your users.

PERSONA	ADDON LICENSE	PERMISSION SET LICENSE	INCLUDED PERMISSION SET	DESCRIPTION

CLM Admin User
CLM User
	ContractManagementAddOn	Contract Lifecycle Management User	
CLM Admin User
CLM Runtime User
	
Allows admin users to monitor, maintain, configure, and manage contract lifecycles.
Allow users to generate contract documents and execute contract lifecycles.


Clause Designer User
Clause User
	ContractManagementAddOn	Clause Management User	
Clause Designer User
Clause User
	
Allows clause designers to create and manage clauses.

Allows users to use clauses within documents.



Microsoft 365 Word Designer

Microsoft 365 Word User

	ContractManagementAddOn	Microsoft Word 365	
Microsoft 365 Word Designer

Microsoft 365 Word User

	
Allows admin users to configure and modify Microsoft 365 Word integration settings.

Allows users to insert Salesforce data such as clauses into documents and templates.



Obligation Manager

Obligation Assignee

Obligation User

	ContractManagementAddOn	Obligation Management User	
Obligation Manager

Obligation Assignee

Obligation User

	
Allows obligation managers to create and define obligations in a parent object. For example, in the Contract object, extract and define obligations, and assign obligations to an assignee.

Allows the obligation assignees to manage obligations within a parent object. For example, in the Contract object, monitor tasks and compliance status.

Allows users to only view obligations.


CLM Digital Experience Partner User	ContractManagementPCAddOn	Contract Lifecycle Management for Digital Experience Partner User	CLM Digital Experience Partner User	

Allows users to generate contract documents and manage contract lifecycles in Digital Experience Partner sites.

For new customers, starting in Winter ’26, Partner Community users get Contract Management access as part of the base license. No separate community add-on SKU is required.

For existing customers, orgs that already provisioned this add-on retain full access, and Partner Community users continue to generate and manage contract documents. In industry clouds where the add-on is bundled, it remains available.


Clause Digital Experience User	ContractManagementPCAddOn	Clause Management Digital Experience User	Clause Digital Experience User	Allows users to use clauses in Digital Experience sites.
Microsoft 365 Word Digital Experience User	ContractManagementPCAddOn	Microsoft 365 Word Digital Experience User	Microsoft 365 Word Digital Experience User	Allows Digital Experience users to insert Salesforce data such as clauses into documents and templates in Digital Experience sites.

Obligation Digital Experience Manager

Obligation Digital Experience Assignee

Obligation Digital Experience User

	ContractManagementPCAddOn	Obligation Management Digital Experience User	
Obligation Digital Experience Manager

Obligation Digital Experience Assignee

Obligation Digital Experience User

	
Allows obligation managers to create and define obligations in a parent object on Digital Experience sites. For example, in the Contract object, extract and define obligations, and assign obligations to an assignee.

Allows the obligation assignees to manage obligations in a parent object on Digital Experience sites. For example, in the Contract object, monitor tasks and compliance status.

Allows users to only view obligations in a parent object on Digital Experience sites. For example, Contract.


Contract Management Customer Community Plus Digital Experience User	ContractManagementCCPlusDEAddOn	Contract Management Customer Community Plus Digital Experience User	Contract Management Customer Community Plus Digital Experience User	

Allows Customer Community Plus users to view the latest generated contract documents in Digital Experience sites.

For new customers, starting in Winter ’26, Customer Community Plus users get Contract Management access as part of the base license. No separate community add-on SKU is required.

For existing customers, orgs that already provisioned this add-on retain full access, and Customer Community Plus users continue to view contract documents, and perform actions such as redlining and e-signature. In industry clouds where the add-on is bundled, it remains available.

DocGen and Omnistudio Licenses

Salesforce Contracts is dependent on DocGen and Omnistudio licenses. These licenses aren’t bundled with Salesforce Contracts. See Personas and Permission Set Licenses for Salesforce Document Generation, and Omnistudio Permission Sets.

Additional Notes

Contract Management and DocGen access updates for Digital Experience users starting Winter ’26.

Partner Community and Customer Community Plus base licenses now include Contract Management access. No separate community add-on SKUs are required for RCA and other non-industry SKUs.
Existing Salesforce Contracts customers with Partner Community or Customer Community Plus Industry add-on SKUs retain full entitlements.
Context Services support removes the hard dependency on Omnistudio for document generation. An Omnistudio license can still be used if already provisioned.
