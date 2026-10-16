---
article_id: ind.sf_contracts_docplaybook_sharing_rule.htm
title: Create a Document Playbook Sharing Rule
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_sharing_rule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_setup.htm
fetched_at: 2026-10-13
---

# Create a Document Playbook Sharing Rule

Only the owner can access a document playbook’s records. To give other users access to a playbook, create sharing rules to provide the appropriate access.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To create Document Playbook sharing rules:	Document Playbook Designer
From Setup, in the Quick Find box, enter Sharing Settings, and then select Sharing Settings.
From Manage sharing settings for, select Document Playbook.
In the Document Playbook Sharing Rules related list, click New.
Enter a label and rule name.
For example, DocumentPlaybookSharingRule.
For Owned by Member of, select All Internal Users.
Select who to share with, such as All Internal Users.
Select an access level.
USER TYPE	ACCESS LEVEL
Document Playbook Users	Read Only
Document Playbook Designers who maintain playbooks that other designers create	Read/Write
Save the rule.
Repeat these steps for Document Playbook Assignment to share these child records beyond the playbook owner.
