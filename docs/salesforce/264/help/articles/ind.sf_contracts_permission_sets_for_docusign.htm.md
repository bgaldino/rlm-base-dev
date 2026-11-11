---
article_id: ind.sf_contracts_permission_sets_for_docusign.htm
title: Permission Sets For DocuSign
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_permission_sets_for_docusign.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
fetched_at: 2026-10-13
---

# Permission Sets For DocuSign

The system admin must assign either the Contract Management (Salesforce Contracts) or DocGen permission set licenses to your user to send documents for e-signature. Non-Salesforce Contracts users must be assigned a DocGen license.

NOTE To assign permission sets to your users, you need CLM Admin User permissions.
PLATFORM LICENSE	PERMISSION SET LICENSE LABEL	PERMISSION SETS	DESCRIPTION
ContractManagement	Contract Lifecycle Management User	CLM Runtime User	Allows users to generate contract documents and send the document for e-signature.
DocGen	DocGen Designer	DocGen Designer	Allows users to create document templates, generate documents, and send the document for e-signature.

You can configure users who must have access to Omnistudio Document Generation business processes such as generating contracts without additional privileges associated with the DocGen Designer license. For more information, see Personas and Permission Set Licenses for Salesforce Document Generation.
