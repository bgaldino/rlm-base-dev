---
article_id: ind.approvals_smart_or_rule_based_approvals.htm
title: Smart Approvals and Rule-Based Auto-Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_smart_or_rule_based_approvals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_building_blocks_of_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Smart Approvals and Rule-Based Auto-Approvals

Smart Approvals and Rule-Based Auto-Approvals speed up resubmissions by auto-approving steps that don’t need another manual review. They differ in how the auto-approval decision is made and the level of control you have over that decision.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Considerations for Auto-Approvals

Smart or Rule-Based Auto-Approvals trigger only when a user resubmits a previously recalled or rejected record. Also, the previous submission must have reached at least 2 steps, with at least 1 of those steps approved.

A completely approved submission can't be recalled. Any subsequent submission is a new request rather than a resubmission, making it ineligible for auto-approval.

Understanding Smart Approvals

Smart Approvals uses each approval step’s existing entry conditions to decide whether the step can be auto-approved on resubmission. If the values that satisfied a step in the previous submission still satisfy it on resubmission, Smart Approvals skips the manual review for that step.

Use Smart Approvals when your approval steps already rely on entry conditions and the resubmission decision depends on whether those same conditions are still met.

Understanding Rule-Based Auto-Approvals

With Rule-Based Auto-Approvals, you can define custom logic such as flows or Apex to determine whether a step is automatically approved on resubmission. Optionally, use the Get Previous Related Record Details invocable action to compare the current submission with a prior submission. Define any business logic that you need, and pass a boolean value as the final auto-approval decision.

Use Rule-Based Auto-Approvals when your auto-approval decision depends on logic that step entry conditions can’t express, such as cross-field comparisons.

Smart Approvals vs. Rule-Based Auto-Approvals

Here’s how Smart Approvals and Rule-Based Auto-Approvals differ.

CAPABILITY	SMART APPROVALS	RULE-BASED AUTO-APPROVALS
Setup	In the approval step’s properties, select Use Smart Approval.	
In the approval step’s properties, select Set custom logic for auto-approvals.
In the Approve Step field, enter a boolean value.

Comparison logic	Reevaluates the step’s existing entry conditions against the previous submission.	Uses any logic that you define, including cross-field or cross-submission rules.
Skip conditions support	Supported. Use the Smart Approval Skip Conditions field to exclude specific conditions from evaluation.	Not applicable
Sample use case	A discount or quantity stays within an approver’s tier on resubmission.	The discount delta between submissions is below a threshold.
Smart Approvals
To eliminate approval bottlenecks, Smart Approvals routes requests by auto-approving pre-qualified data changes and not reviewing unchanged data. When a record is resubmitted for approval, Smart Approvals compares the new conditions against the previous submission. If the values remain within the defined range, it skips re-approval.
Rule-Based Auto-Approvals
Set your own rules and conditions on specific fields for auto-approving resubmissions. Compare the current submission’s record details against the previously submitted record so that only significant changes require manual review.
