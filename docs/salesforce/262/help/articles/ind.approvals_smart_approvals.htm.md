---
article_id: ind.approvals_smart_approvals.htm
title: Smart Approvals in Approval Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_smart_approvals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Smart Approvals in Approval Flows

To eliminate approval bottlenecks, Smart Approvals routes requests by auto-approving pre-qualified data changes and not reviewing unchanged data. When a record is resubmitted for approval, Smart Approvals compares the new conditions against the previous submission. If the values remain within the defined range, it skips re-approval.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS
NEEDED
To turn on smart approvals:	

Approval Designer

OR

Manage Flow

Before we introduce the steps to be followed to implement Smart Approvals, familiarize yourself with how to create an approval flow.

Review these considerations for how smart approvals work for different step entry conditions in your flow.

APPROVAL STEP ENTRY CONDITION	SMART APPROVAL CONSIDERATIONS
When the stage starts, the step starts	If the approval stage that contains the step has a decision element before it, the smart approval evaluation fails.
When another step is marked Complete, the step starts	None.
When the specified requirements are met, the step starts	You can specify up to 30 conditions. Apex and Record data types aren’t eligible for smart approval evaluation.
When the specified evaluation flow returns True, the step starts	Not eligible for smart approval evaluation.
EXAMPLE A company uses Smart Approvals for its multistep discount workflow. John can approve discounts up to 40%, James approves 41–50%, and the CFO, Jenny, must approve anything over 50%. A sales rep submits a quote with a 55% discount. After John and James approve the quote, Jenny rejects it and asks for a lower discount. The rep adjusts the quote to 52% and resubmits. Instead of restarting the entire process, Smart Approvals compares the new submission to the previous one and sees that John and James’s conditions are still met, so it routes the request only to Jenny for the final sign-off. This process eliminates redundant approvals.
Turn On Smart Approvals
To skip reviewing previously approved steps in an approval resubmission, turn on Smart Approvals.
