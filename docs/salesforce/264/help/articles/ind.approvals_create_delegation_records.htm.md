---
article_id: ind.approvals_create_delegation_records.htm
title: Create Approval Delegation Records
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_create_delegation_records.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_approval_delegation.htm
fetched_at: 2026-09-07
---

# Create Approval Delegation Records

Set up approval coverage by specifying who handles your approval responsibilities and for how long.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS NEEDED
To create delegation records:	Create, Edit, and Delete on Approval Delegation
From the App Launcher, find and select Approvals.
Open Manage Approval Delegations.
Click New.
In the Delegated From User field, select the user delegating their approvals.
In the Delegated To field, select the user, group, or queue that manages approvals on the reviewer's behalf.
In the Start Date field, enter the date and time when the delegation is active.
The start date must be in the future.
In the End Date field, enter the date and time when the delegation expires.
The end date must be later than the start date. If left blank, the delegation remains active indefinitely.
Enter your comments.
Save your changes.
NOTE A reviewer can have only 1 active delegation at a time. To assign different delegates for different periods, create non-overlapping approval delegation records.
SEE ALSO
Considerations for Advanced Approval Delegations
