---
article_id: ind.sf_contracts_aa_reference.htm
title: Advanced Approvals for Salesforce Contracts Components
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_aa_reference.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_aa_overview.htm
fetched_at: 2026-10-13
---

# Advanced Approvals for Salesforce Contracts Components

Review contract-specific components, roles, and behaviors used in advanced approval workflows.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

For general Advanced Approvals concepts such as approval stages, routing logic, and Flow configuration, see Advanced Approvals in Revenue Cloud.

Core Components
PROPERTY	DESCRIPTION
Contract Type Config	Maps contract types to approval flows and controls which flow runs during submission. If no configuration exists, contracts use standard approval behavior.
Approval Flow	Runs contract approval logic based on defined conditions
Apex Logic	Evaluates complex conditions within the approval flow
Approval Submission Record	Stores approval state and tracks approval actions
Contract Record	Stores contract status and lifecycle stage
Approval Actions by Persona
PERSONA	AVAILABLE ACTIONS	DESCRIPTION
Administrator	
Review
Recall
Cancel
Override
Reassign
	

Manages the approval process, including modifying assignments, stopping approvals, and handling exceptions


Submitter	Recall	Calls back a submitted contract to make updates before resubmitting
Approver	
Approve
Reject
	Reviews the contract and either approves or rejects it
Contract Lifecycle Behavior
ACTION	CONTRACT BEHAVIOR
Submit for Approval	Starts the approval process by invoking the approval flow mapped through Contract Type Config
Recall	Ends the approval process and returns the contract for updates. Configure a recall path in the approval flow to update contract status.
Cancel	Ends the approval process. Create a record-triggered flow on the Approval Submission record to update contract status.
Approve	Moves the contract to the next approval stage or completes the approval process. When all required approvals are complete, the contract advances to the next lifecycle stage based on the Flow configuration.
Reject	Sends the contract back for updates
Email Approval Behavior
CAPABILITY	DESCRIPTION
Email Response	Replies with “approved” or “reject” in the first line of the email
Templates	Configures notification content by using text templates
Dynamic Data	Includes contract fields such as ID and pricing in notifications.

Smart Approval Behavior

Smart approvals skip previously approved steps during resubmission based on configured conditions defined in the approval flow. This behavior reduces redundant approvals and improves processing efficiency.
