---
article_id: ind.sf_contracts_clause_approval_workflow.htm
title: Clause Approval Workflow
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_clause_approval_workflow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause_library.htm
fetched_at: 2026-10-13
---

# Clause Approval Workflow

Set up a clause approval workflow to send your draft clause for approval to your internal stakeholders, such as managers, and the legal team. The Submit for Approval action triggers the approval workflow. Salesforce verifies the list of approvers and automatically initiates the approval request notification via email, based on configuration.

To successfully trigger and complete the approval workflow for a clause, consider this sample configuration.

Approval Steps: Specifies the individual approvers who receive the request for clause approval.

Final Approval Actions: Defines the subsequent action after the clause is approved.

In the sample Set Up Approval Process Detail Page For Clause, the clause is set to move to the Active status.

Final Rejection Actions: Defines the subsequent action after the clause is rejected.

In the sample Set Up Approval Process Detail Page For Clause, the clause is set to move to the Draft status.

Recall Actions: Defines the subsequent action after you recall a clause that was sent for internal approval. You can recall the approval request if you want to modify the draft clause.

In the sample Set Up Approval Process Detail Page For Clause, the clause is set to move back to the Draft status.

Prerequisite for creating a clause approval workflow

Enable the Clause Management User permission set license in the company.

Assign Clause Designer User permission sets to your admin users.

Share clause records to the internal and digital experience users based on Share Settings. See Share Settings.

Configure email templates for clause approval actions. See:

Create Text Email Templates in Salesforce Classic

Creating the Email Template
Extract the Clause Category ID for Clause Approval
Use the clause category ID to define the clause approval process for a clause category.
Define a Clause Approval Process Name
Create a clause approval process and define the final approval, final rejection, and recall actions. The clause approval process setup ensures that the clause status reflects the defined action when a clause is approved, rejected, or recalled.
Set Up Approval Process Detail Page For Clause
Define at least one approval step and configure the field update settings for approval, rejection, and recall actions to activate the clause approval process.
