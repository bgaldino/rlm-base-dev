---
article_id: ind.sf_contracts_approvals_concept.htm
title: Contract Approval Processes in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_approvals_concept.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Contract Approval Processes in Salesforce Contracts

Salesforce Contracts supports two approval mechanisms, the advanced approvals and the standard Salesforce approval process. The standard approval process is the default and runs when advanced approval isn’t configured.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

The standard approval process uses predefined rules and approval steps to route contracts for approval. When you submit a contract for approval, Salesforce selects the approval mechanism based on the configuration.

Advanced Approvals uses flows to manage contract approvals. When you map an approval flow in Contract Type Config, the system runs the flow on submission. The flow identifies approvers, routes approvals, and updates contract status based on defined logic.

If a flow is mapped in Contract Type Config, an advanced approvals process runs.
If no flow is configured, the standard approval process runs.
Standard Approval Workflow for Salesforce Contracts
A contract approval workflow routes draft contracts to internal stakeholders for review. The workflow triggers when a user selects Submit for Approval and sends email notifications to the configured approvers.
Advanced Approval Workflow for Salesforce Contracts
Use advanced approvals to manage contract review workflows by associating approval flows with contract types and controlling approval actions that update the contract lifecycle.
