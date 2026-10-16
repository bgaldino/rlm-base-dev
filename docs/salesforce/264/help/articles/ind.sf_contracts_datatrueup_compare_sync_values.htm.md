---
article_id: ind.sf_contracts_datatrueup_compare_sync_values.htm
title: Compare and Sync Token Values in a Document
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_compare_sync_values.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Compare and Sync Token Values in a Document

View the data true-up token values from the document and the Salesforce record side by side, and decide if the values need to be updated to ensure data accuracy.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create Document Template with Data True-Up tokens:	

CLM Admin

OR

CLM Runtime

AND

DocGen Designer


To use Document Template with Data True-Up tokens in contract authoring:	DocGen Designer

Prerequisites:

Make sure that the document is generated from a template that includes Data True-Up tokens.
Configure the Microsoft 365 Word add-in.
Open the document in Microsoft 365 Word add-in.
Select Data True-Up from the drop-down menu.
In the Tokens tab, review each token value and their sync status.
Make sure each token shows a document value and the corresponding record value.
Make sure the sync status appears as In Sync, Out of Sync, or Fetch Failed.
To pull the current record values from Salesforce, click Fetch Values.
To update the document value for any token, click Edit Value.
Modify the document value and save your change.
You can update the repetitive tokens in the document template only collectively. You can update all instances or cancel the change.
To push the updated document values back to Salesforce record fields, click Update Fields.
Review the validation summary.
To proceed with the update, click Update Values.
To confirm the update, under Update Record Summary, click OK.

After you update the fields, the document is automatically checked in with a new version. You can continue editing or return to Salesforce for further actions.

SEE ALSO
Set Up Microsoft 365 and Azure Integration Using Guided Setup
Design Document Templates in Microsoft 365 Editor
Contract Authoring in Microsoft 365 Editor
