---
article_id: ind.sf_contracts_aa_overview.htm
title: Advanced Approval Workflow for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_aa_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_approvals_concept.htm
fetched_at: 2026-10-13
---

# Advanced Approval Workflow for Salesforce Contracts

Use advanced approvals to manage contract review workflows by associating approval flows with contract types and controlling approval actions that update the contract lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

Salesforce Contracts uses advanced approvals to manage contract approval workflows through flow-based orchestration. This capability integrates with Revenue Cloud and routes contract approvals through approval flows instead of standard Salesforce approval processes when configured. If no configuration exists, contracts continue to use standard approval behavior. Advanced Approvals provide greater flexibility than standard approval processes by supporting multilevel serial and parallel approval chains, condition-based routing, and automated notifications.

When you submit a contract for approval, the approval flow runs if it’s mapped through Contract Type Config. The approval flow evaluates contract data based on defined conditions, identifies approvers, and routes the contract through approval stages. Submitting a contract for approval updates the contract status to In Approval. For all other actions, such as recall, cancel, approve, and reject, configure the Approval Flow to update the contract status. For details about approval stages, routing logic, and Flow design, see Advanced Approvals in Revenue Cloud.

Key Capabilities
Contract Type—Driven Approval Execution: Associate approval flows with contract types by using the Contract Type Config setting to align logic with business rules.
Multilevel Serial and Parallel Approvals: Define approval stages within an autolaunched flow to run in order or simultaneously based on contract conditions.
Smart Approvals for Resubmission: Skip previously approved steps during resubmission when configured conditions, such as total price or key terms, remain unchanged or meet defined thresholds. Define evaluation conditions in the approval flow to control which steps are skipped during resubmission.
Apex-Based Conditional Logic: Call Apex classes within the approval flow to evaluate complex conditions, such as aggregating line item values or validating thresholds.
Lifecycle-Aware Approval Actions: Approval actions update the contract lifecycle based on the configured flow logic. Recall returns the contract to draft status when the approval flow includes a recall path that updates the contract status. Cancel acts as a terminal action and requires flow logic to update the contract status.
Condition-Based Approval Routing: Configure approval steps to run only when defined conditions are met, such as contract value thresholds or specific terms.
Email-Based Approval Interaction: Approvers can respond directly to approval emails by entering approved or reject. The response is processed only when the keyword appears in the first line of the email. Configure notifications by using text templates with dynamic contract data.
How Advanced Approvals Work
The contract author submits a contract for approval.
Submitting a contract for approval runs the approval flow when it’s mapped through Contract Type Config.
The flow evaluates contract data based on defined conditions and executes Apex logic when configured.
The contract routes through sequential or parallel approval stages.
Smart approval logic skips previously approved steps during resubmission when configured conditions are met.
Approvers act based on their role. Approval actions update the contract status and lifecycle stage based on flow configuration.
How Users Interact with Advanced Approvals

Advanced Approvals permissions are bundled with Contract Management add-on licenses. Permission set licenses (PSLs) are mapped to Salesforce Contracts personas to simplify setup and access.

CLM Admin users perform approval administration and design tasks, including configuring approval workflows.
CLM Runtime and CLM Digital Experience Partner User permissions support approval execution, including submitting contracts for approval and reviewing approval requests.
Configure Advanced Approvals for Salesforce Contracts
Set up contract approval workflows by associating approval flows with contract types, configuring approver resolution, and defining lifecycle actions.
Submit a Contract for Approval by Using Advanced Approvals for Salesforce Contracts
Generate a contract document, submit it for approval, and manage the approval request.
Review and Approve a Contract
Review assigned approval requests, and advance or return the contract.
Advanced Approvals for Salesforce Contracts Components
Review contract-specific components, roles, and behaviors used in advanced approval workflows.
Advanced Approvals Troubleshooting and FAQ for Salesforce Contracts
Review common challenges related to setup, visibility, and contract lifecycle behavior in advanced approvals. Also, review the specific persona-based permissions and configuration requirements needed to ensure correct contract status updates during recall or cancel actions.
SEE ALSO
Advanced Approvals
