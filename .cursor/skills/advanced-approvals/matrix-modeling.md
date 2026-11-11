# Modeling a Sign-Off Matrix

Read this when turning an approval policy into Advanced Approvals. Parent:
[advanced-approvals](SKILL.md).

## 1. Write the matrix down as levels

List each dimension and its thresholds as levels 0–N, where 0 means no approval:

| Dimension | Level 1 | Level 2 | Level 3 | Measured on |
|---|---|---|---|---|
| Discount (any line or product line) | > 10% | > 20% | > 30% | each line, or each product-line total |
| Blended margin | < 70% | < 65% | < 60% | the quote |
| Net value | — | — | > $5M | the quote |
| Other triggers | non-standard billing frequency | term < 12 months; custom payment terms; any line below floor margin | any line below cost | line or quote |

Two policy rules decide the shape:
- **"The highest level triggered applies":** compute one level per dimension, then take
  the maximum.
- **"Each level also needs every level below":** the levels form a serial chain.

## 2. Compute each level as a Number

Step conditions can only test what a background step returns, and Smart Approvals needs
Number or Text values [Help: `ind.approvals_smart_approvals`,
`ind.approvals_smart_approval_limitations`]. The docs never show a condition reading
quote-line fields directly [Help: `ind.approvals_example_configure_an_approval_workflow`]. Choose
where each level is computed:

| Where | Use for | Repo precedent |
|---|---|---|
| Pricing procedure → line field → roll-up on the quote | Line-based levels (discount per line, a line below floor or cost) | `approval_flags.json` writes `RLM_Approval_Level_Calc__c`; `Quote.RLM_Approval_Level__c` is MAX of it |
| Approval data flow (background step) | Quote-level values (margin, net value, term, billing frequency, payment terms), and the MAX across dimensions | `RLM_Quote_Approval_Data` returns `DiscountApprovalLevel`, `PaymentTerms` |
| Formula or roll-up field | A simple count or MIN over lines | `Quote.RLM_Discount_Percent__c` (formula) |

- **"Any line below X":** express it as a count of lines that break the rule, then test
  "count > 0". Smart Approvals rejects the NOT operator, so don't write it as "NOT all lines
  pass" [Help: `ind.approvals_smart_approval_limitations`].
- **Freshness:** a level stored on lines comes from the last reprice, with no staleness
  guard. Make reprice part of submission [Repo: `datasets/expression_set_overlays/README.md`].
- **Security:** keep stored levels read-only for submitters
  [Repo: `docs/references/revenue-cloud-permissions.md`].

## 3. Lay out chains and steps

- **Cumulative levels:** one chain (for example `Discount`) with one step per level. Step N
  has the entry condition `Level >= N AND step N−1 outcome = Approve`; step 1 has
  `Level > 0`. The shipped flow does this for Manager, Director and VP
  [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`].
- **Several dimensions, one approver ladder:** take the MAX of the dimension levels into one
  `ApprovalLevel` and drive the single chain from it. The approvers are the same people, so
  one chain avoids duplicate work items.
- **Several dimensions, different approvers:** give each its own `ApprovalChainName`. Chains
  in one stage run in parallel [Help: `ind.approvals_types_of_approvals`]. The shipped
  `Finance` chain is an example.
- **Level 0:** route around the approval stage with a Decision, as the repo does. Its steps
  use explicit entry conditions, not "when the stage starts", so the Decision doesn't cost
  Smart Approvals eligibility.
- **Exit:** for each step, "completed OR not triggered", plus the rejection shortcut
  [Repo: `docs/features/composable-quote-approvals.md` → Exit Condition Pattern].
- **Rejection:** route any rejected step to a "Rejected" stage. In the shipped flow,
  rejecting one chain withdrew the other chain's open item and rejected the submission
  [Measured: 2026-11-10, 264].
- **Recall:** add a path that resets the record's status on recall. The shipped flow has
  none, and recall left the quote at Pending [Measured: 2026-11-10, 264]. For contracts the
  docs say to build it [Help: `ind.sf_contracts_aa_configure`].

## 4. Approvers

- Assign by group or queue name rather than by ID. The shipped flow assigns to groups
  `Manager`, `Director` and `VP`.
- In a fresh scratch org those groups have no members. An org admin with the approval
  admin permission could still review those items [Measured: 2026-11-10, 264].
- Documented approver types: user, group and queue. A "Resource" type exists, but Preview
  doesn't support it [Help: `ind.approvals_preview_feature_limitations`].
- The docs don't describe a manager or role-hierarchy approver type ([limitations.md](limitations.md)).

## 5. Worked example (fictional)

The policy: discount levels as in §1, margin below 65% needs a Director, and net value
over $5M needs the VP. One approver ladder.
1. The pricing procedure keeps writing the line discount level (the shipped overlay,
   thresholds edited).
2. `RLM_Quote_Approval_Data` reads the quote and returns:
    - `DiscountApprovalLevel`, from the roll-up;
    - `MarginApprovalLevel`, from the quote's margin;
    - `ValueApprovalLevel`, 3 when net value is over 5,000,000;
    - `ApprovalLevel`, the maximum of the three.
3. The Discount chain's three steps test `ApprovalLevel` instead of `DiscountApprovalLevel`.
4. Nothing else changes: exits, rejection and alerts are per step.
5. Test cases:
    - a 22% discount at 72% margin → Manager, Director;
    - a 5% discount at 63% margin → Manager, Director;
    - $6M at 75% margin → Manager, Director, VP;
    - nothing triggered → Approved at once.
