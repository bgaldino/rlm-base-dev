# Acceptance Chain: Quote to Renewal

Read this when writing the end-to-end verification part of a plan, or when judging whether
a built org meets the requirements. Each step names what to check, the owner section that
defines how, and the evidence tag the owner gives its behavior. The expected values come
from the customer's requirements, computed by hand or from the source before the run;
never accept a number because the org returned it.

## How to use

1. For each step, write the expected result per requirement id before running anything.
2. Run the owner's verification, not a paraphrase of it.
3. Record actual, expected, pass or fail, org, release and date.
4. A step whose owner marks the behavior open or measured on one org is a verification of
   that behavior, not an assumption. A fail there is a finding, not a defect in the plan.
5. Run the chain on a disposable org before the customer's. Keep verification orgs and
   their records until the owner agrees to delete them.

## The chain

| # | Step | Verify | Owner section |
|---|---|---|---|
| 0 | Catalog ready | Every sellable product has a selling model option, a price book entry, a category and is active `[inferred]`; each changed bundle passes product-definition validation `[inferred]`; one bundle configures with configuration rules on | [Check before and after](../product-catalog-modeling/catalogs-and-loading.md#check-before-and-after), [PCM load facts](../product-catalog-modeling/catalogs-and-loading.md#pcm-load-facts-264) (fact e), [pricing-setup Validation Checks](../pricing-setup/SKILL.md#validation-checks) |
| 1 | Lookups fresh | No decision table is stale after the last data change; refresh ran after loads | [Freshness](../decision-tables/SKILL.md#freshness--what-the-verdicts-mean), [Validation Checks](../decision-tables/SKILL.md#validation-checks) |
| 2 | Quote places | A quote placed with the intended route carries the intended lines, terms, billing frequencies and attributes | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis), [Billing frequency](../billing-setup/SKILL.md#billing-frequency) |
| 3 | Price | Each line price, discount, total and tax equals the hand-computed value; read the pricing log or waterfall for any difference | [runtime-and-observability.md](../pricing-procedures/runtime-and-observability.md), [pricing-setup Validation Checks](../pricing-setup/SKILL.md#validation-checks) |
| 4 | Multi-year and ramp | Each period's price and the uplift equal the expected schedule; read back the ramp schedule | [Validation Checks](../ramped-quotes/SKILL.md#validation-checks), [compound-uplift.md](../ramped-quotes/compound-uplift.md) |
| 5 | Rounds | Each round holds its own discounts; the internal round never reaches an order; the intended round becomes the order | [Validation Checks](../quote-negotiation-rounds/SKILL.md#validation-checks), [Final round to order](../quote-negotiation-rounds/SKILL.md#final-round-to-order) |
| 6 | Approve | A quote crossing each threshold routes to the intended approvers in the intended order; a quote below it does not; recall and resubmit behave as required | [matrix-modeling.md](../advanced-approvals/matrix-modeling.md) (routing by level; recall and resubmit rules), [Validation Checks](../advanced-approvals/SKILL.md#validation-checks) (headless test paths: single and multi-dimension, rejection, recall and resubmit, cancel; plus deploy idempotency); that the intended approvers act in the intended order needs a live run `[inferred]` |
| 7 | Order | The order carries the winning round's lines and amounts, and activates | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis) |
| 8 | Fulfill | Submission yields the expected plan: step list per order product matches the design table and the derived counts; read configuration and runtime separately | [Verify Configuration and Runtime Separately](../dro-plans/authoring-and-deployment.md#5-verify-configuration-and-runtime-separately), [updates-and-runtime.md](../dro-plans/updates-and-runtime.md) |
| 9 | Assets | The sale leaves the expected assets, and none for products marked not assetizable; asset terms, quantities and attributes match the order | [IsAssetizable](../product-catalog-modeling/selling-models-and-lifecycle.md#isassetizable), [verification.md](../asset-lifecycle-changes/verification.md) |
| 10 | Bill | Billing schedules carry the promised frequency, treatment and payment term; the first invoice has the expected period, amount and due date; milestone items fire as designed (who marks them: Marking an event milestone done in the billing-setup link; the trigger from fulfillment is open until verified) | [Validation Checks](../billing-setup/SKILL.md#validation-checks), [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) |
| 11 | Contract and documents | The contract exists at the intended point with the intended terms; each document generates with correct values | [setup-and-diagnostics.md](../salesforce-contracts/setup-and-diagnostics.md) (verify template and generated documents), [document-generation Before generation](../document-generation/SKILL.md#before-generation) (active mappers and template references), then generate to verify values |
| 12 | Usage and rating | Usage booked to a completed period rates to the expected amounts, including commitment drawdown and overage; rated summaries are non-zero where expected | [Live verification](../usage-consumption/verification.md#live-verification), [Reading a suspicious result](../usage-consumption/verification.md#reading-a-suspicious-result) |
| 13 | Amend | Each allowed change type (quantity add or remove, swap, cancel) shows the expected prices, attributes, credits and invoice values past the first placement, through activation to the asset | [verification.md](../asset-lifecycle-changes/verification.md), [Validation Checks](../asset-lifecycle-changes/SKILL.md#validation-checks) |
| 14 | Renew | The renewal quote prices per policy, including any uplift and ramp; values read before activation hold after it | [change-policy-mapping.md](../asset-lifecycle-changes/change-policy-mapping.md), [renewal-asset-creation](../renewal-asset-creation/SKILL.md) |
| 15 | Idempotency and rerun | Re-running any load or task creates no duplicates | [sfdmu-data-plans](../sfdmu-data-plans/SKILL.md), [AGENTS.md checklists](../../../AGENTS.md) |

## Binding steps to requirements

Each chain step lists the requirement ids it proves. Mark a step not applicable only when
the customer confirmed the capability is out of scope. A requirement with no step is a gap
in the chain; a step with no requirement is test data, so drop it or find the requirement.

## Test data

Build the transactions from the customer's catalog, with values you can compute by hand.
Generating them through the transaction harness requires a scenario for that catalog; see
[txn-data-harness](../txn-data-harness/SKILL.md) and check what it supports before
promising automation. Renewal tests need assets of the right age; see
[renewal-asset-creation](../renewal-asset-creation/SKILL.md) and its entry conditions.

## Report format

Per step: requirement ids, expected, actual, pass or fail, evidence tag from the owner, org
and release, date. List open items (behavior no skill establishes) separately with the
live check that would close each. Say plainly what was not run.
