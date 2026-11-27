# Rule-Based Auto-Approvals

Read this when a step should auto-approve on a rule you control (not on the earlier
approved range, which is Smart Approvals), or when a "true" flag still sends a step to
review. Parent: [advanced-approvals](SKILL.md). Smart Approvals:
[limitations.md](limitations.md) → Smart Approvals.

## What it is

A step can be told to auto-approve from a Boolean the flow computes. The step reads two
inputs, set in Flow Builder under "Set custom logic for auto-approvals" on the 264 editor
[Help: `ind.approvals_define_custom_logic_auto_approvals`]:

| Step input | Value |
|---|---|
| `ActionInput__CanUseRuleBasedAutoApprovals` | `true` |
| `ActionInput__ApprovalOverrideDecision` | a Boolean resource, for example a background step's Boolean output |

An element reference to a Boolean output deploys into this String input, and the work item
gets `IsEligibleForAutoApproval` true [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
The background step that computes the Boolean sat in the same stage as the target step and worked; one in an
earlier stage also worked, because its output is read when the step is created [Measured: same]. The Help describes
the background step as one that precedes the target approval step
[Help: `ind.approvals_define_custom_logic_auto_approvals`].

## Rules that decide the outcome

1. **Only "true" auto-approves.** The step auto-approves when the override value equals `true`
   ignoring case. "Approve", "Yes" or any other text goes to review, silently
   [Platform behaviour, traced]. A
   static override of "Approve" is therefore always false and tests nothing.
2. **It needs the Smart Approval basis.** Rule-based and Smart Approvals share one basis: an
   earlier Recalled or Rejected submission of the same record and flow version, with a basis
   item for the same step and an active reviewer (`ApprovalSubmission.SmartApprvlBasisSubmissionId`)
   [Platform behaviour, traced]. So it never fires on a first submission
   [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
3. **After a full approval there is no basis.** Flag true still went to review
   [Measured: same].
4. **After a rejection the flag decides.** After a Director rejection, flag true auto-approved
   the Manager step (`IsAutoReviewed` true, reviewer = the basis reviewer, basis item set); flag
   false on the same basis went to review [Measured: same].
5. **The basis chains.** A submission after an auto-approved one used the auto-approved item as
   its basis [Measured: same].
6. **Mutual exclusions.** The editor makes an Auto Approval Evaluation Flow exclusive with Use
   Smart Approval and with the Auto-Approve Step, and with an evaluation flow set the override
   path is skipped [Platform behaviour, traced]. When measuring, turn Smart Approval off on the measured steps,
   or you cannot tell which path approved.

## How to test it

1. Give the step the two inputs and a Boolean from a background step (a quote field compared with a limit works).
2. Submit once, reject at a later step, fix the data, resubmit: the earlier steps should show
   `IsAutoReviewed` true when the Boolean is true and `Assigned` when false.
3. Control: submit again after a full approval and confirm the flag has no effect.

```sql
SELECT Id, Status, ApprovalChainName, IsEligibleForAutoApproval, IsAutoReviewed, ReviewedById
FROM ApprovalWorkItem WHERE RelatedRecordId = '<quote>' ORDER BY CreatedDate
```

## Not covered

[Open: the Auto Approval Evaluation Flow path is
undocumented in the 264 Help; do not build on it as a workaround.]
