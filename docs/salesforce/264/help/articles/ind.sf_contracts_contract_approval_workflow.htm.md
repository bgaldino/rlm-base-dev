---
article_id: ind.sf_contracts_contract_approval_workflow.htm
title: Standard Approval Workflow for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_approval_workflow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_approvals_concept.htm
fetched_at: 2026-10-13
---

# Standard Approval Workflow for Salesforce Contracts

A contract approval workflow routes draft contracts to internal stakeholders for review. The workflow triggers when a user selects Submit for Approval and sends email notifications to the configured approvers.

This section details the sample configurations for a contract approval workflow to trigger and complete successfully.

To set up a contract approval process for your contract state model, you must create a contract approval process. You must then define the field update settings for final approval actions, final rejection actions, and recall actions. The contract approval process setup makes sure that the contract status reflects the defined action when the contract is approved, rejected, or recalled.

Here’s a list of minimum configurations that must be set up for a contract approval process:

Approval Steps
The approval steps define the approvers who all get the approval request.
Final Approval Actions
Once the contract is approved, you must define the next action. Here, the contract is set up to move to Negotiating status.
Final Rejection Actions
After the contract is rejected, you must define the next action. Here, the contract is set up to move to Rejected status.
Recall Actions
After the contract is sent for internal approval; you can recall the approval request to change the draft contract. Here, the contract is set up to move to Draft status.
Define a Contract Approval Process
Create a contract approval process that integrates with your contract state model. The approval process controls what happens to the contract status when a contract is approved, rejected, or recalled.
Set Up Approval Process Detail Page For Contracts
After you create a contract approval process, define at least one approval step before you can activate it. The approval step specifies who receives the approval request and how the contract status changes on approval, rejection, or recall.
