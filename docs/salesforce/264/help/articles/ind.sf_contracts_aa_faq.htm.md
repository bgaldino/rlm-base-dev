---
article_id: ind.sf_contracts_aa_faq.htm
title: Advanced Approvals Troubleshooting and FAQ for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_aa_faq.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_aa_overview.htm
fetched_at: 2026-10-13
---

# Advanced Approvals Troubleshooting and FAQ for Salesforce Contracts

Review common challenges related to setup, visibility, and contract lifecycle behavior in advanced approvals. Also, review the specific persona-based permissions and configuration requirements needed to ensure correct contract status updates during recall or cancel actions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Edition
CATEGORY	ISSUE	SOLUTION
Setup	Why are contracts still using the basic approvals after I created an advanced approval flow?	Make sure that the Flow API name is correctly linked to the specific contract type within the Contract Type Config. If this setting is missing, the system defaults to basic platform behavior.
Visibility	The Submit for Approval button is missing.	Confirm that you have Run Flow access and Advanced Approval platform licenses are active.
Flow Actions	Why didn’t the contract status return to the draft after a recall?	

Define a Recall Path in the Flow that specifically updates the contract record status to draft.


Visibility	Why can’t I see the cancel button on the contract page?	By design, Advanced Approval action buttons such as cancel and override are hidden on the Contract record page. They’re only accessible from the Approval Work Item record.
Smart Approvals	Why did a step skip when I wanted a manual rereview?	Smart Approvals skip steps if configured conditions are met. To force a review, specify condition numbers to skip in the Smart Approval settings or turn it off for that step.
Email	I replied to the approval email, but the status didn’t update.	Place the keyword Approved or Reject in the first line of the email response for processing.
Email	Why are the approval emails generic and missing contract data?	Use text templates in the Flow to define dynamic content, mapping fields like Contract ID and Total Price into the message.
Permissions	Can an approval designer also reject a request?	Yes. Consolidate designer and admin roles under the CLM Admin profile in this integration. Grant full administrative control to users with this profile.
