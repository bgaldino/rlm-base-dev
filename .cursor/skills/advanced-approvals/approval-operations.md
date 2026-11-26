# Operating and Extending Approvals

Read this when configuring approver steps, delegation, notifications and the approval
screens, or when running day-two questions (who can act, who can see, what an edit in Flow
Builder does to the source). Parent: [advanced-approvals](SKILL.md). Measured results come
from fresh ent-sb0 harness builds on 264; the tag on each fact says which.

## Approver and step settings

- **Approver types** in the step editor: User, Group, Queue, Resource. The `FlowStageStepAssigneeType`
  enum accepts those four and rejected Manager, RoleHierarchy, Role, RelatedUser, UserManager and
  Hierarchy [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
- **Resource** takes "a resource containing the username of the approver, or the API name of a
  public group or queue. Any member of that group or queue can approve" [Measured: same; step editor
  help text]. A step whose Resource was a text constant holding a group's API name assigned its work
  item to that group, the same target as a Group-type step; stored as `<assigneeType>Resource</assigneeType>`
  with an `elementReference`. A Resource pointing at a user **Id** (a step output or input variable)
  faulted at submission with "Invalid Resource reference" [Measured: same].
- **Packaging:** Flow Builder warns on every step whose assignee type is User, Group or Queue that an
  orchestration with such a step can't be packaged. A Resource step has no warning [Measured: same].
  Use Resource when the flow ships in a package.
- **All must approve:** the checkbox "Require unanimous approval" in the step's approver section.
  Unchecked (default), the first response completes the step: one group item, approved by one member.
  Checked, it stores `requiresMultiMemberApproval` 100 and the input
  `ActionInput__RequiredMultiMemberApprovalPercentage` 100 (a percentage, not a Boolean). A group step
  then produced three items (one for the group, one per member); one member approving left the step
  holding, and the second member's approval approved all three [Measured: same].
- **Automated Process email:** on a fresh build Flow Builder warns that the Automated Process User has
  no valid email address, so the orchestration can't send step emails; set one under Process Automation
  Settings [Measured: same; candidate build-configuration follow-up].
- **Builder saves rewrite XML.** Saving an approval flow in Flow Builder dropped `<conditionType>ExitCondition</conditionType>`
  lines and added `END_ELEMENT_*` connectors in the stored flow; saving a page in App Builder added
  `isAutoAdvanceToNextWorkItem=false` to the Work Guide component. Diff a builder save before committing
  it back to source [Measured: same].

## Who can act and who can see

- **Reviewer actions need no Approval Admin:** review from the Review button, `reviewApprovalWorkItem`, and
  recall by the submitter. A submitter without the admin permission started an approval from the quote and
  recalled it from the Approval Submission record (Recall, then comments; submission, work item and the quote's
  `RLM_Approval_Status__c` went Recalled; the dialog warns a recall can't be undone). The quote's Approvals tab
  showed that submitter no work items and offered no recall; the submission record did
  [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]. Details of the reviewer grants are in
  [matrix-modeling.md](matrix-modeling.md) §4.
- **Sharing:** `ApprovalWorkItem` and `ApprovalSubmission` default to Private for internal and external
  access, and both are Apex-triggerable [Measured: 2026-11-26, 264, ent-sb0 harness build]. A queue member
  seeing work items for records they can't read, and a before-save record-access check to block action on
  records the approver can't read, are [Open: needs a queue with two members, one without Read on the quote;
  the Help says an approver "must have access to the record's related object to perform actions" while a field
  repro showed approval succeeding without it].
- **Automation on work items:** Apex triggers are allowed on `ApprovalWorkItem` and `ApprovalSubmission`
  [Measured: same]. Which record-triggered flows fire on them, and how to resolve the polymorphic `AssignedToId`
  for display, are [Open: not run].

## Delegation

Setup > Approval Settings lists "Advanced Approval Delegation" (Off on a fresh build): "Turning this on
overrides any prior delegation set on the user record." It has no Metadata API field, so turning it on is a
Setup step: a toast confirms, with no dialog, and the audit trail records `approvalsDelegationEnabledOffOn`.
Before, `ApprovalDelegation` was not describable; after, `ApprovalDelegation` and `ApprovalDelegationHistory`
appear, with `DelegatedFromUserId`, `DelegatedToId`, `StartDate`, `EndDate` and `Comments` (createable) and an
`AD-` autonumber name; an admin created one over the API. The toggle stays enabled after saving On, so Setup
offers Off (not exercised). [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build.] [Open: whether a live
work item routes to the delegate.]

## Approval screens, notifications and extras

These come from the release's Help; none was run on a build unless tagged.

- **Request Approval component, comment prefill:** a copied submit screen flow can prefill the Comments box from
  a Text Template, and it goes through `RLM_AA_Submit_Approval`; the template must be plain text, since a rich-text
  template leaks HTML [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]. The standard Request Approval
  component's own properties: [Open: not run].
- **Approval Trace, Work Guide and related lists:** the Quote page's approval UI options, the trace's limits and
  filtered work-item related lists on Quote are [Open: not run; read the release's Approval Help and the Quote
  record page in the target org].
- **Alert templates** render against the recipient and target record, not the work item id; a failed render
  silently sends the default email; the step screen flow is where to require comments [Open: from field reports;
  verify with a deliberately broken template].
- **First submissions:** Smart and Rule-Based auto-approval never fire on a first submission. For a policy that
  must skip a step on the first pass, stamp a role or flag on the quote in the submit screen flow (it runs as the
  submitter), skip the step with an entry condition, and give the stage an exit that treats "not triggered" as done.
  Inside the orchestration `$User` is Automated Process and `$UserRole` is blank, so a quote formula on the submitter
  fails silently. Submitters, and any test user who stamps the quote, need the RLM user permission set license, or
  the flow faults with "can't edit quotes with the Revenue Lifecycle Management ... application usage assignment"
  [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
- **Approval accelerators** (follow-up, auto-escalation) and **mass approval:** [Open: Help names scheduled sample
  flows for follow-up and auto-escalation; mass approval is not in the 264 build; confirm on the target release before promising either].
- **Recall:** recall accepts In Progress submissions (the dev guide adds Suspended); a one-click recall quick action is a
  quick action calling `recallApprovalSubmission` [Dev guide: `actions-obj-recall-approval-submission`; Open: quick action not built].
- **Charge-type dimension:** to approve by one-time versus recurring value, compute a level per charge type in the
  approval data flow and treat it as its own chain ([matrix-modeling.md](matrix-modeling.md) §2) [Open: pattern, not run].
