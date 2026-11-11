---
article_id: ind.sf_contracts_riskanalysis_setup.htm
title: Set Up Contract Risk Analysis
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_riskanalysis_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_riskanalysis_how.htm
fetched_at: 2026-10-13
---

# Set Up Contract Risk Analysis

Contract Risk Analysis compares each modified clause in a contract against your approved playbook. After a reviewer makes changes to a version of the contract, the author runs the analysis using the Microsoft 365 Word add-in. A generative AI model scores each modified clause, explains the risk, and recommends the mitigation content to add to the contract.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To set up contract risk analysis:	CLM Admin User

Contract authors run risk analysis after internal or external review, on the updated version returned with reviewer or counterparty edits. See How Contract Risk Analysis Works for the end-to-end flow.

Before you begin, confirm that these prerequisites are in place.

Salesforce Contracts is turned on and contract authors can create Contract Document Version (CDV) records. See Enable Salesforce Contracts.
The Contracts AI add-on is provisioned for your org.
A grounding playbook has an approved Active version. A playbook assignment exists for each contract object and record type combination that contract authors work with. See How Document Playbook Works.
The Salesforce Contracts Connector for Word is installed for contract authors in Microsoft Word (Microsoft 365). See Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Data 360 is provisioned for playbook indexing and hybrid (vector plus keyword) search over section-aware chunks.
Data 360 is turned on. See Turn On Data Cloud.
Turn on Einstein.
From Setup, in the Quick Find box, enter Einstein Setup, and then select Einstein Setup.
Turn on Einstein.
Turn on Contract Risk Analysis.
From Setup, in the Quick Find box, enter Contracts AI, and then select Risk Analysis.
Turn on Contract Risk Analysis.
Assign the permission sets to each contract author who runs risk analysis on the contract document.
From Setup, in the Quick Find box, enter Permission Sets, and then select Permission Sets.
Select these permission sets.
PERMISSION SET	GRANTS ACCESS TO
Contracts AI User	Contract Risk Analysis runtime, including the Risk Analysis panel and the Run Risk Analysis action.
Playbook User	Applying the assigned document playbooks used to score clauses and recommend content.
Prompt Template User	The prompt templates that generate risk explanations and playbook recommendations.
CLM Runtime User	Contract Document Version lifecycle actions.
Microsoft 365 User	The Microsoft 365 Word add-in and the ability to open a contract document version (CDV) from Microsoft 365 Word.
Select Manage Assignments > Add Assignments.
Select the contract author users, and then click Assign.
Confirm that you have an assigned playbook.
Open the grounding document playbook record for the contract object and record type that your contract authors work with, and confirm that there’s a playbook.
Without an assignment, risk analysis has no playbook to score against.
Make sure that the playbook has only one Active version and that it’s indexed.
Test the setup.
Check in an updated contract document version with a status of either InReview or InExternalReview.
In the Microsoft 365 Word add-in, open the contract document.
Open the editor's side panel, and check that the Risk Analysis icon appears and that Run Risk Analysis is available.
Run Risk Analysis appears only when the user is the contract author for the contract document version (CDV), the CDV status is InReview or InExternalReview, and the user has the permission sets listed in step 3.
