# Modeling a Sign-Off Matrix

Read this when turning an approval policy into Advanced Approvals. Parent:
[advanced-approvals](SKILL.md).

## 1. Write the matrix down as levels

List each dimension and its thresholds as levels 0–N, where 0 means no approval (the thresholds
below are illustrative, not a recommended policy):

| Dimension | Level 1 | Level 2 | Level 3 | Measured on |
|---|---|---|---|---|
| Discount (per line) | > 7% | > 15% | > 25% | each line |
| Blended margin | < 55% | < 50% | < 45% | the quote |
| Net value | — | > $2M | > $8M | the quote |
| Other triggers | a manually overridden line price; any non-catalog line | quote validity longer than 30 days | — | line or quote |

Two policy rules decide the shape:
- **If several levels trigger, the highest applies:** compute one level per dimension, then
  take the maximum.
- **A level usually also needs the levels below it:** the levels form a serial chain.

Every percentage also needs a base. "Discount > 15%" can be measured off list price, or off
a standard price that already includes contract, bundle or volume pricing; the same line can
land on different levels under each. That is a modeling decision the source must state; if
it doesn't, ask and record the answer. §2 shows what the shipped level measures.

A deal-size threshold needs a base too once amendments go through approval: the change, or
the contract value after it.
- **An amendment quote carries the change.** Its lines carry a delta quantity, and a
  negative delta is priced from prior sale prices [Help: `ind.qocal_amend_assets`]. A price
  amendment has a delta quantity of zero; its total is a prorated credit for the old price
  plus a charge for the new one, rolled up to the line and subtotal
  [Help: `ind.qocal_field_and_pricing_amendments`]. On a QuantumBit build, an amend +1 root
  line priced at +1 × net unit and an amend −1 line at −1 × net unit
  [Measured: 2026-11-05, 264, recorded in `asset-lifecycle-changes` → `verification.md`].
  So a threshold on the quote's own totals measures the change, and a reduction can be
  negative.
- **The quote holds no contract-value field.** Its fields in the repo's ERD include
  `ContractId` but no contract value [Repo: `python scripts/ai/query_erd.py describe Quote`];
  `OriginalActionType` says which action created it (`Amend`, `Cancel`, `Renew`, `Transfer`)
  [Dev guide: `quote_and_order_capture_fields_on_quote`]. Swap, upgrade and downgrade quotes
  leave it blank [Repo: `.cursor/skills/rlm-business-apis/backdated-asset-lifecycle.md`], so
  a threshold keyed on `OriginalActionType = Amend` misses them. A threshold on the value after the
  change has to be computed in the approval data flow; which records to compute it from is
  open ([limitations.md](limitations.md)).
  When it sums prior orders by account, read the account the action wrote. With quotes
  without an opportunity allowed (this repo's scratch org definitions enable it), amendment
  and renewal quotes had `AccountId` null and `QuoteAccountId` set, and an `AccountId`
  filter returned a prior value of 0 on an amendment [Measured: 2026-11-12, 264, scratch];
  amend, renew and cancel write the account only to `QuoteAccountId` when that setting is on
  [Platform behaviour, traced]. With it off, they get an opportunity and `AccountId` comes
  from it [Platform behaviour, traced; not measured], so a filter that must work on both
  kinds of org reads `QuoteAccountId` and falls back to `AccountId`.
- **The shipped approval has no deal-size dimension.** Its conditions read the discount
  level and payment terms. `RLM_Quote_Approval_Data` also returns `OriginalActionType`, but
  the `QueryApprovalData` step doesn't declare it as an output and no condition reads it
  [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Approval_Data.flow-meta.xml`,
  `RLM_Quote_Smart_Approval.flow-meta.xml`]. No amendment submission is recorded.

## 2. Compute each level as a Number

Conditions test the outputs of background steps and other steps, or flow formulas; the docs
never show a condition reading quote-line fields directly
[Help: `ind.approvals_example_configure_an_approval_workflow`]. Smart Approvals compares the single
value each condition resolved to, in a supported datatype
(Number and Text are the documented-safe types)
([limitations.md](limitations.md) → Smart Approvals). So reduce line data to quote-level numbers before
the approval stage. Choose
where each level is computed:

| Where | Use for | Repo precedent |
|---|---|---|
| Pricing procedure → line field → roll-up on the quote | Line-based levels (discount per line, a non-catalog line) | `approval_flags.json` writes `RLM_Approval_Level_Calc__c`; `Quote.RLM_Approval_Level__c` is MAX of it |
| Approval data flow (background step) | Quote-level values (margin, net value, quote validity, payment terms), and the MAX across dimensions | `RLM_Quote_Approval_Data` returns `DiscountApprovalLevel`, `PaymentTerms` |
| Roll-up summary field | A MAX, MIN or count over lines | `Quote.RLM_Approval_Level__c` (MAX of `QuoteLineItem.RLM_Approval_Level_Calc__c`) |
| A loop over the lines in the approval data flow | Line conditions on the line's product (family, a custom product flag), which a roll-up summary's filter can't reach | None shipped; measured below |

- **Line conditions in a loop:** get the quote's lines (Get Records on `QuoteLineItem` by
  `QuoteId`, all records), loop over them, and count or take the maximum in assignments;
  turn the results into levels after the loop. In a measured run [Measured: 2026-11-12, 264]:
    - a flow formula read `Product2.Family` and a custom `Product2` field through the loop
      variable (`{!<loop>.Product2.Family}`) over the Get Records collection;
    - Percent fields come in percent units: a line `Discount` of 24% reads as 24, so test
      `> 15`, not `> 0.15`;
    - a line-floor count (line `Margin` below a floor) and a below-cost count
      (`NetUnitPrice < UnitCost`) each raised the level on the lines they should, and not on
      the others.

  The loop reads the lines' stored values, so reprice first all the same.
- **"Any line below X":** express it as a count of lines that break the rule, then test
  "count > 0". Smart Approvals rejects the NOT operator, so don't write it as "NOT all lines
  pass" [Help: `ind.approvals_smart_approval_limitations`].
- **Freshness:** a level stored on lines comes from the last reprice, with no staleness
  guard. Make reprice part of submission [Repo: `datasets/expression_set_overlays/README.md`].
- **Security:** keep stored levels read-only for submitters
  [Repo: `docs/references/revenue-cloud-permissions.md`].

**What the shipped discount level measures.** "The procedure" below is
`force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`.
- The approval-flags overlay bands only `ItemDiscountPercentage`
  [Repo: `datasets/expression_set_overlays/approval_flags.json`], the line's own manual
  discount percent (the `Discount` attribute of `SalesTransactionItem`)
  [Repo: `docs/references/context-definitions/RLM_SalesTransactionContext.contextDefinition-meta.xml`].
- The procedure applies that percentage in `Applyamountbasedandpercentagebaseddiscounts`,
  after the bundle and volume steps, the contract discount and the line's amount discount.
  So its base is the net unit price those left, not list [Repo: the procedure; `pricing-procedures` →
  [elements/manual-discount.md](../pricing-procedures/elements/manual-discount.md)].
- The overlay runs after `Calculatecostandmarginforpricedlines` and before the header
  discount steps and `DiscountDistributionService` [Repo: overlay placement, procedure step
  order]. So bundle, volume and contract pricing, a line amount discount, and a header
  discount spread to lines don't raise the level.
- A source that measures discount off list needs its own percentage, for example a formula
  step at the same point that computes it from `ListPrice` and `NetUnitPrice`, banded the
  same way.

**Line guards (below floor margin, below cost).**
- The shipped procedure computes line margin (`ItemMargin__std`, net total less unit cost
  times quantity, over net total) only for lines with a unit cost, before the header discount
  steps [Repo: the procedure, `Filterlineswithunitcost` and `Calculatetotalcostandmargin`].
  A guard placed where the flags sit can read it; decide what a line with no cost means. A
  guard can also be counted in the data flow's line loop (above).
- A guard sees only the line's resulting values. A round's bulk discount (the same discount
  set on every line) and a rep's override on one line end up in the same fields, and nothing
  in the shipped model records which set them. If the source treats them differently,
  give the guard a marker it can read: a line field the bulk step sets, mapped into the
  pricing context like the shipped approval fields
  [Repo: `datasets/context_plans/Approvals`], and tested in the guard's filter. This is a
  modeling recommendation, not platform behavior.
- Nothing documented sets such a marker. Bulk edit applies one value to the same field on
  every selected line, and the STLE does the same on groups
  [Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_customize_transaction_line_editor`];
  neither article says the result is recorded as a bulk edit. The repo's custom
  `QuoteLineItem` fields include no such marker
  [Repo: `force-app/**/objects/QuoteLineItem/fields/`, `unpackaged/**/objects/QuoteLineItem/fields/`,
  including `unpackaged/pre/6_fields`].
  Whatever applies the round's discount (a second bulk edit on the marker's column, or an
  API call or flow that writes the discount) would have to set the marker too, and
  something would have to clear it when a rep later overrides a marked line. None of this
  is measured ([limitations.md](limitations.md)).
- A round-wide header discount stays out of the level: `DiscountDistributionService` spreads
  it to lines after the level is set (above). A discount on a group row is unsettled. Help
  applies one to all the lines of a group [Help: `ind.qocal_basic_example_ramp_deals_for_groups`]
  but doesn't say whether it stays on the group's `Discount` field
  [Dev guide: `sforce_api_objects_quotelinegroup`] or is written to each line's `Discount`,
  which the shipped level reads. Don't count on a group discount to keep a round's discount
  out of the level until that is measured ([limitations.md](limitations.md)).
- A pass-through line priced at or near cost trips a below-cost or
  floor-margin guard on every quote. Exclude it by a marker the filter tests, such as a
  product attribute or line field, not by product name. The source must also say whether
  excluded lines still count in a blended margin.

## 3. Lay out chains and steps

- **Cumulative levels:** one chain (for example `Discount`) with one step per level. Step N
  has the entry condition `Level >= N AND step N−1 outcome = Approve`; step 1 has
  `Level > 0`. The shipped flow does this for Manager, Director and VP
  [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`].
- **Several dimensions, one approver ladder:** take the MAX of the dimension levels into one
  `ApprovalLevel` and drive the single chain from it. The approvers are the same people, so
  one chain avoids duplicate work items. With a modified copy of the shipped flows that folds
  every dimension, payment terms included, into `ApprovalLevel`, no level → Approved with no
  work items; level 1 → the first approver; a non-standard payment term mapped to a middle
  level → the approvers up to that level, in turn; level 3 → all three in turn. Each submission and its quote
  ended Approved [Measured: 2026-11-12, 264].
- **Several dimensions, separate sign-offs:** give each its own `ApprovalChainName` when a
  dimension needs its own sign-off, usually from different approvers. Chains in one stage
  run in parallel [Help: `ind.approvals_types_of_approvals`]. The shipped `Finance` chain is
  a separate sign-off, but it routes to the same `Manager` group as the first Discount step,
  so a quote that triggers both gives that group two items.
- **Payment terms: in the ladder or in a Finance chain.** The shipped flow keeps terms out of
  the ladder: one `Payment_Terms` step in the `Finance` chain, entry
  `PaymentTerms != "Net 30"`, with its own alert and email template
  [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`,
  `datasets/sfdmu/qb/en-US/qb-approvals/README.md`]. A source that puts custom terms at a
  ladder level maps terms to a level number in the approval data flow and
  folds it into `ApprovalLevel`. The trade-off:
    - One ladder: terms pass every level up to theirs, in order, with one item per approver.
      Alerts link a template to a step [Help: `ind.approvals_email_templates`], so the
      approver isn't told whether discount or terms raised the level unless the template
      shows both.
    - A Finance chain: runs in parallel and can go to its own approver and template. The
      shipped `rejectedQuote` formula includes `Payment_Terms`, so a terms rejection also
      routes the flow to Rejected (not yet run; see Rejection below).
    - Either way, `Requires_Approval` and the stage exit conditions must cover terms.
- **Level 0:** route around the approval stage with a Decision, as the repo does
  (`Requires_Approval`). The Decision must test **every** dimension: a dimension it leaves
  out never gets approval when it is the only one triggered. The steps use explicit entry
  conditions, not "when the stage starts", so the Decision doesn't cost Smart Approvals
  eligibility.
- **Exit:** for each step, "completed OR not triggered", plus the rejection shortcut
  [Repo: `docs/features/composable-quote-approvals.md` → Exit Condition Pattern].
- **Rejection:** route any rejected step to a "Rejected" stage. In the shipped flow,
  rejecting the Discount item withdrew the open Finance item and rejected the submission
  [Measured: 2026-11-10, 264]; the reverse direction hasn't been run.
- **Recall and cancel:** a status the approval flow set (Pending) stays unless something
  resets it. The docs give a recall path in the approval flow for recall, and a
  record-triggered flow on `ApprovalSubmission` for cancel
  [Help: `ind.sf_contracts_aa_configure`]. The shipped flow has no recall path; the repo
  uses one record-triggered flow for both, `RLM_AA_Reset_Quote_Status`, which leaves the
  orchestration unchanged
  [Repo: `docs/features/composable-quote-approvals.md` → Quote approval status].
- **Resubmission: restart or Smart Approvals.** Smart Approvals is set per approval step
  (Use Smart Approval) [Help: `ind.approvals_turn_on_smart_approvals`]. On a resubmission
  after a rejection or recall, it re-evaluates each step's entry conditions against the
  previous submission and skips manual review where they are still met
  [Help: `ind.approvals_smart_or_rule_based_approvals`]; eligibility rules are in
  [limitations.md](limitations.md). All four shipped steps pass
  `ActionInput__CanUseSmartApproval = true` [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`].
    - With level conditions (`Level >= N`), a value that moved within its band still meets
      them, so that step is skipped. The Help example skips two approvers whose ranges were
      still met and routes only to the third [Help: `ind.approvals_smart_approvals`]. A
      re-review that depends on how much a value changed is Rule-Based Auto-Approvals
      [Help: `ind.approvals_smart_or_rule_based_approvals`].
    - A source that says "a resubmission restarts the chain" wants every approver to review
      again: turn Smart Approval off on that chain's steps. Left on, it skips approvers on a
      rejected or recalled resubmission. With `ActionInput__CanUseSmartApproval` `false` on
      every step, a resubmission after the second step rejected (the first approved) opened
      a new first-step work item, `Assigned`, `IsEligibleForSmartApproval` false
      [Measured: 2026-11-12, 264]. With it `true`, the direction rule for which resubmissions
      auto-approve is in [limitations.md](limitations.md) → Smart Approvals.
    - After a full approval, any later submission is a new request, so the chain restarts
      whatever the setting [Help: `ind.approvals_smart_or_rule_based_approvals`].

## 4. Approvers

- Assign by group or queue name rather than by ID. The shipped flow assigns to groups
  `Manager`, `Director` and `VP`, which ship in `force-app/main/default/groups/`. A new
  approver tier needs its own group there.
- In a fresh scratch org those groups have no members. An org admin who wasn't a member
  could still review those items with `reviewApprovalWorkItem` [Measured: 2026-11-10, 264].
  The dev guide requires the reviewer to be the assignee, a group or queue member, a delegate
  or above in the role hierarchy [Dev guide: `actions_obj_review_approval_work_item`], and
  the Help gives an approval administrator the right to "review or override any work item"
  [Help: `ind.approvals_personas`]. The admin held Approval Admin (through its profile and the
  `RLM_CLM` permission set group) [Measured: 2026-11-10, 264], which fits the Help. Don't rely on it for ordinary reviewers: give the groups members.
- Documented approver types: user, group and queue. A "Resource" type exists, but Preview
  doesn't support it [Help: `ind.approvals_preview_feature_limitations`].
- The docs don't describe a manager or role-hierarchy approver type ([limitations.md](limitations.md)).

## 5. Worked example (fictional)

The policy: discount levels as in §1, margin below 50% needs a Director, net value over
$2M needs a Director, and net value over $8M needs the VP. One approver ladder.

Prerequisite: margin and net value are dimensions beyond Discount and Finance, and the
design doc requires threshold policy to be externalized before adding one
[Repo: `docs/features/composable-quote-approvals.md`]. Do that first, or agree and record the
exception. The steps below keep thresholds hard-coded (edited to the §1 bands) and don't show it.

1. The pricing procedure keeps writing the line discount level (the shipped overlay,
   thresholds edited in its `addSteps`; for an org that already has it, see the design
   doc's Verification Checklist [Repo: `docs/features/composable-quote-approvals.md`]).
2. `RLM_Quote_Approval_Data` reads the quote and returns:
    - `DiscountApprovalLevel`, from the roll-up;
    - `MarginApprovalLevel`, from the quote's margin;
    - `ValueApprovalLevel`, 2 when net value is over 2,000,000 and 3 when it is over 8,000,000;
    - `ApprovalLevel`, the maximum of the three.

   Declare each new output on the `QueryApprovalData` background step
   (`outputConfigParams`), as the shipped `DiscountApprovalLevel` and `PaymentTerms` are.
3. Switch everything that reads `DiscountApprovalLevel` to `ApprovalLevel`:
    - the three step entry conditions;
    - the `Requires_Approval` decision;
    - the stage's "not triggered" exit conditions (2, 4 and 6 in the shipped flow).

   The rejection formula and alerts are per step and don't change.
4. Test cases:
    - a 20% discount at 60% margin → Manager, Director;
    - a 5% discount at 48% margin → Manager, Director;
    - $9M at 75% margin and a 5% discount → Manager, Director, VP;
    - $3M at 75% margin and a 5% discount → Manager, Director;
    - nothing triggered → Approved at once.
