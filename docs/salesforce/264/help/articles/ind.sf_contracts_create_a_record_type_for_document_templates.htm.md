---
article_id: ind.sf_contracts_create_a_record_type_for_document_templates.htm
title: Create a Record Type for Salesforce Contracts Document Templates
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_record_type_for_document_templates.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-10-13
---

# Create a Record Type for Salesforce Contracts Document Templates

Create a corresponding record type for the document template object, if you have integrated Microsoft 365 Azure account with Salesforce and want to use Microsoft 365 editor to create document templates.

Create a sample Microsoft Word (.docx) template.
See Create a Microsoft Word or Microsoft PowerPoint Template for Omnistudio Document Generation.
Go to Setup, then click Object Manager.
In the Quick Find box, search for Document Template.
Click Document Template and then Record Types.
Enter these details:
Record Type Label: Enter a label for the record type.
For example, CLM.
Record Type Name: Enter a name for the record type.
For example, CLM.
Select Active.
Select Make Available for the user profiles that you want to provide the ability to create and clone records of the record type, or assign the record type to existing records.
Click Next.
Select Document Template Layout in Apply one layout to all profiles.
Save your changes.
