---
article_id: ind.sf_contracts_define_a_contract_approval_process_name.htm
title: Define a Contract Approval Process
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_define_a_contract_approval_process_name.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_approval_workflow.htm
fetched_at: 2026-10-13
---

# Define a Contract Approval Process

Create a contract approval process that integrates with your contract state model. The approval process controls what happens to the contract status when a contract is approved, rejected, or recalled.

Before you begin, verify that these prerequisites are in place:

Permission Set License: Contract Lifecycle Management User
Permission Sets: CLM Admin User and CLM Runtime User
Update sharing setting for Object State Definition.

This procedure walks you through the minimum configuration to enable a contract approval process using the Standard Setup Wizard. You can refine the settings later to match your business requirements.

From Setup, in the Quick Find box, enter Approval Processes.
Click Approval Processes.
In the Manage Approval Processes For dropdown, select Contract.
Click Create New Approval Process, and then click Use Standard Setup Wizard.
In Step 1 (Enter Name and Description), enter a process name, unique name, and description for the approval process.

Use a descriptive name that identifies the contract type or scenario, such as "Contract Review and Approval".

Click Next.
In Step 2 (Specify Entry Criteria), accept the defaults and click Next.

Entry criteria determine which contracts can be submitted for approval. Leaving the criteria blank allows any contract to be submitted. You can add filter conditions later if you want to restrict approvals to specific contracts, such as those above a certain value or in a particular state.

In Step 3 (Specify Approver Field and Record Editability Properties), select Administrators ONLY can edit records during the approval process and click Next.

This setting prevents non-admin users from modifying the contract while it's awaiting approval.

In Step 4 (Select Notification Templates), accept the defaults and click Next.

Notification templates control the emails sent to approvers and submitters. Skipping this step uses Salesforce default notifications. You can assign custom email templates later.

In Step 5 (Select Fields to Display on Approval Page Layout), configure the approval page:
Add Contract Number and Contract Owner to the Selected Fields list.
Select Display approval history information in addition to the fields selected above.
Select Allow approvers to access the approval page only from within the Salesforce application. (Recommended).
Click Next.
In Step 6 (Specify Initial Submitters), configure who can submit contracts for approval:
In the Search dropdown, select Owner.
Add Contract Owner to the Allowed Submitters list.
Select Add the Submit for Approval button and Approval History related list to all Contract page layouts.
Select Allow submitters to recall approval requests.
Save your changes.
Select I'll do this later. Take me back to the listing of all approval processes for this object and click Go.
