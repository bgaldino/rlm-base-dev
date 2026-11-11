---
article_id: ind.sf_contracts_set_up_approval_process_for_clause.htm
title: Set Up Approval Process Detail Page For Clause
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_approval_process_for_clause.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_clause_approval_workflow.htm
fetched_at: 2026-10-13
---

# Set Up Approval Process Detail Page For Clause

Define at least one approval step and configure the field update settings for approval, rejection, and recall actions to activate the clause approval process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED
To configure the approval process for clauses:	Clause Designer User
From Setup, in the Quick Find box, enter Approval Process, and then select Approval Processes.
In Manage Approval Processes For, select Document Clause.
Click the approval process that you defined earlier.
In the Approval Steps section, verify that the Assigned Approver is set to Manager.
You assigned Manager as the approver in earlier steps.
In the Final Approval Actions section, add a field update.
Click Add New, and select Field Update.
Enter these details on the New Field Update window:

Name: DraftToActive

Unique Name: DraftToActive

Description: Add a description.

Default object: Document Clause.

Field to Update: Status

A specific value: Active

Save your changes.
In the Final Rejection Actions section, add a field update.
Click Add New, and select Field Update.
Enter these details on the New Field Update window:

Name: RejectClause

Unique Name: Rejected

Description: Add a description.

Default object: Document Clause.

Field to Update: Status

A specific value: Rejected

Save your changes.
In the Recall Actions section, add a field update.
Click Add New, and select Field Update.
Enter these details on the New Field Update window:

Name: RecallClause

Unique Name: RecallClause

Description: Add a description.

Default object: Document Clause

Field to Update: Status

A specific value: Draft

Save your changes.
Add an email alert for clause approval, rejection, and recall actions.
Go to the Final Approval Actions section.
Click Add New, and select Email Alert.
In Description, enter Approve Email.
The system automatically fills the Unique name field.
Select the email template that you want to use when you send a clause approval email.
The mail template was created as part of the prerequisites.
In Recipient Type, select User.
From Available Recipients, move the users that you want to receive the approval email to Selected Recipients.
Save your changes.
In the Final Rejection Actions section, repeat steps from b to g.
In the Recall Actions section, repeat steps from b to g.
Activate the clause approval process.
Click OK.

See Also

Define a Clause Approval Process Name
