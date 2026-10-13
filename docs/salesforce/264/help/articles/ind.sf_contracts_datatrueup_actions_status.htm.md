---
article_id: ind.sf_contracts_datatrueup_actions_status.htm
title: Data True-Up Actions and Statuses
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_actions_status.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Data True-Up Actions and Statuses

Understand the status indicators and available actions in the Data True-Up panel. Learn how each status reflects the state of your token data and what each button does during the Data True-up sync process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
Token Sync Statuses in Data True-Up
STATUS	DESCRIPTION
In Sync	The token value in the document matches the corresponding record field value in Salesforce.
Out of Sync	The token value in the document differs from the corresponding record field value in Salesforce.
Fetch Failed	The system couldn't fetch the field value from the Salesforce record for the token. This issue can happen due to missing permissions, deleted fields, or temporary API failures. Check if the record still contains the mapped field.
Data True-Up Button Labels and Actions
NOTE All actions depend on the user's permissions for the respective records.
LABEL IN UI	FUNCTION
Fetch Values	Retrieves values from Salesforce into the document tokens.
Update Record	

Writes updated token values from the document back to Salesforce.

At the Data True-Up panel level, this option updates all token changes in the document. At the token level, this option updates only the individual token value.


Refetch Value	Refetches the specific token value from the record.
Edit Value	Manually modify the document token value.
Delete Token	Removes the token reference from your document.
Delete Line Item	Removes all the associated tokens in the line item from your document.
