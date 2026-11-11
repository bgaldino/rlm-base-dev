---
article_id: ind.sf_contracts_define_a_clause_approval_process_name.htm
title: Define a Clause Approval Process Name
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_define_a_clause_approval_process_name.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_clause_approval_workflow.htm
fetched_at: 2026-10-13
---

# Define a Clause Approval Process Name

Create a clause approval process and define the final approval, final rejection, and recall actions. The clause approval process setup ensures that the clause status reflects the defined action when a clause is approved, rejected, or recalled.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED
To configure the approval process for clauses:	Clause Designer User

To enable a clause approval process, here are the minimum configuration requirement steps.

From Setup, in the Quick Find box, enter Approval Process, and then select Approval Processes.
In Manage Approval Processes For, select Document Clause.
Click Create New Approval Process | Use Jump Start Wizard.
In the Approval Process Information section, add the approval details.
Enter a process name.
For example, Clause Approval.
Select the email template that you configured as part of the prerequisite steps.
Select Add the Submit for Approval button and Approval History related list to all Document Clause page layouts.
In the Specify Entry Criteria section enter these details:
In Use this approval process if the following, select formula evaluates to true.
Paste this code in the blank space.
AND(ISPICKVAL(DocumentClauseSet.Category, '0zMxxxxxxxxxxxx'), ISPICKVAL(Status, 'Draft'))
Replace 0zMxxxxxxxxxxxx' with the clause category ID that you extracted earlier.
To ensure that there are no errors, click Check Syntax.
In the Select Approver section, select an approver:
Select Automatically assign an approver using a standard or custom hierarchy field:.
Select Manager .
Save your changes.
Click OK.

See Also

Extract the Clause Category ID for Clause Approval
