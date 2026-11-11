# Limitations and Open Questions

Read this before relying on Smart Approvals, Preview, email, delegation or Slack, and
before telling anyone how approvals behave where the docs are unclear. Parent:
[advanced-approvals](SKILL.md).

## Setup

- **Settings:** Setup → Approval Settings: Use Flow Approval Process, Use Advanced
  Approvals, the email options, Use Advanced Approval Delegation, Use Dynamic Approval
  Notifications, and the Slack toggles. Email replies are a separate setting, under
  Process Automation Settings [Help: `ind.approvals_set_up_advanced_approvals`].
- **Repo coverage:** the repo ships no settings metadata for these toggles. On a
  QuantumBit build the shipped approval ran end to end with whatever the scratch org
  defaults to [Measured: 2026-11-10, 264].
- **Personas:**
    - Designer: Manage Flow, Approval Designer.
    - Submitter, reviewer, delegate: Run Flows plus Read on Approval Submission.
    - Administrator: also Approval Admin.

  [Help: `ind.approvals_personas`]. One quote walkthrough says approving needs Approval
  Admin [Help: `ind.approvals_use_advanced_approvals_in_a_quote`]; the personas table says
  otherwise. Test with a reviewer who has no admin permissions.
- **Supported objects:** the docs publish no list of supported objects. Quote, Order,
  Contract and custom objects appear in examples [Help: `ind.approvals_objects_considerations`].
- **Sandboxes:** run Match Production License after a release
  [Help: `ind.approvals_environment_setup`].

## Smart Approvals (auto-approval on resubmission)

A step is eligible only if all of these hold [Help: `ind.approvals_smart_approval_limitations`,
`ind.approvals_smart_approvals`, `ind.approvals_smart_or_rule_based_approvals`]:
- conditions are Number or Text, with at most 30 per step and no NOT operator;
- no evaluation-flow entry or exit condition (that makes the whole flow ineligible);
- no Decision before a stage whose steps start "when the stage starts";
- the earlier submission was Rejected or Recalled, reached at least 2 steps, and had at
  least 1 approved;
- the active flow version hasn't changed since;
- no work item was reassigned during the original submission.

After a full approval, the next submission is a new request, not a resubmission.

## Preview

- Works only with the Autolaunched Flow Approval Process (No Trigger) type.
- Skips steps whose entry conditions depend on asynchronous evaluations, such as subflows
  in background steps.
- Treats every referenced step as a required dependency, without telling AND from OR.
- Doesn't show dependencies across chains, and fails on approvers of type Resource.

[Help: `ind.approvals_preview_feature_limitations`]. A real submission is the test.

## Email and alerts

- Eight notification reasons. One template per flow, step and reason
  [Help: `ind.approvals_email_templates`, `ind.approvals_email_notification_behavior`].
- The template must be Available for Use, and its entity must match the record.
- Deselect "Don't send approver notifications" on the step to get emails.
- Queue emails go to at most 1,000 recipients.
- The repo's alert rows go in `datasets/sfdmu/qb/en-US/qb-approvals` (`sfdmu-data-plans`).

## Delegation, Slack, execution

- **Delegation:** one active delegation per reviewer; delegations can't overlap and
  can't be deleted (end them instead); delegates get no Slack notifications
  [Help: `ind.approvals_delegation_considerations`].
- **Errored runs:** usually two steps locking the same record, or a work-item screen that
  failed to render. Check Paused and Failed Interviews
  [Help: `ind.approvals_approval_process_execution`].
- **Concurrent reviews:** when two group members review at once, the first wins and the
  second is rejected.

## Open questions (not settled by the docs or a measured run)

- Where "First Response" vs "All Must Approve" is configured for a group or queue step.
- Whether approving needs Approval Admin, or only Run Flows plus Read (measured runs used
  an admin).
- Which Approval Settings a fresh scratch org has on, and whether Metadata API can set them.
- Whether a dynamic (Resource) approver works at runtime, and whether there is a
  manager-hierarchy approver.
- Whether Smart Approvals accepts roll-up summary, Percent, Currency or picklist
  conditions as Number or Text.
- Whether `ApprovalDelegation` appears once delegation is turned on.
