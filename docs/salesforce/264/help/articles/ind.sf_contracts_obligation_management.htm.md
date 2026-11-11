---
article_id: ind.sf_contracts_obligation_management.htm
title: Obligation Management
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_obligation_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_documnet_actions_overview.htm
fetched_at: 2026-10-13
---

# Obligation Management

Associate obligations with contracts to track contractual commitments. Assign each obligation to an owner, monitor compliance status, and receive automated notifications when deadlines approach.

The permissible actions for an obligation are dependent on the user’s persona. The obligation user can only view obligations. The obligation manager and assignee can track obligations by status: compliant, non-compliant, or at risk and filter obligations by state and party. Obligation Management also sends emails and in-app notifications. The notifications trigger when an obligation is assigned or deleted or the obligation status or metadata is updated.

You can easily associate Salesforce tasks for upcoming obligations within contracts, to meet obligations within defined time frames. For example, enable obligation assignees to stay on top of their contractual obligations and reduce potential risks by tracking payment due dates, contract terms, and renewals.

Obligation Actions
The permissible actions for an obligation depend on the persona. You can use the obligation actions on the Obligations tab on a contract record page.
View Obligations Associated with a Contract
Preview the obligations associated with a contract from the contract’s record page. The default obligation statuses are Compliant, Non-Compliant, and At Risk. The obligation manager can also configure additional custom obligation statuses.
Obligation Creation
The obligation manager can create an obligation from the Obligations object and then associate it with a contract, or create an obligation directly from the contract's record page. You can create obligations for a contract with any status; however, the obligation state remains as On Hold until the contract is in the status defined in the Activate Obligations Based on Contract Status config value.
Edit an Obligation
The obligation manager and obligation assignee assigned to an obligation can update the obligation. The obligation assignee can only update the status and the status change reason.
Delete an Obligation
Only the obligation manager assigned to an obligation can delete the obligation.
Change Obligation Owner
Only the obligation manager who created the obligation or the current obligation manager assigned to the obligation can change the ownership of the obligation to another obligation manager.
Create a Salesforce Task for an Obligation
The obligation manager can easily create and associate Salesforce tasks for upcoming obligations within contracts, to track and meet obligations within defined time frames. They can then assign these specific tasks to an obligation assignee. The tasks can be recurring tasks, reminders, or one-time tasks.
Obligation Management Personas and Supported Actions
Obligation personas that support obligation management are obligation manager, obligation assignee, obligation user, digital experience manager, digital experience assignee and digital experience user.
Relation Between Contract Status and Obligation State
The default state of an obligation is On Hold. The state of the obligations associated with a contract is updated to Active, Inactive, or Expired based on any change in the contract's status and the start and end dates of the obligation.
Default Obligation Values
The default obligation management includes predefined states, status and supported obligation parties for obligations.
