# Acceptance Chain: Quote to Renewal

Read this when writing the end-to-end verification part of a plan, or when judging whether
a built org meets the requirements. Each step names what to check and the owner section that
defines how to check it. When reporting, record the evidence tag the owner gives that behavior. The expected values come
from the customer's requirements, computed by hand or from the source before the run;
never accept a number because the org returned it.

## How to use

1. For each step, write the expected result per rule ID before running anything (the
   build checks, steps 0, 1 and 15, have no rule ID; write their expected state).
   In a plan, those expected results are its golden tests
   ([plan-template.md](plan-template.md) section 4): cite the golden ids per step.
2. Run the owner's verification, not a paraphrase of it.
3. Record actual, expected, pass or fail, org, release and date.
4. A step whose owner marks the behavior open or measured on one org is a verification of
   that behavior, not an assumption. A fail there is a finding, not a defect in the plan.
5. Run the chain on a disposable org before the customer's. Keep verification orgs and
   their records until the user agrees to delete them.

## The chain

| # | Step | Verify | Owner section |
|---|---|---|---|
| 0 | Catalog ready | Every sellable product has a selling model option, a price book entry, a category (except a product sold only with others, which the platform refuses in a category) and is active (this list is `[inferred]`); each changed bundle passes Validate Product Definition; one bundle configures with configuration rules on | [Check before and after](../product-catalog-modeling/catalogs-and-loading.md#check-before-and-after), [product-catalog-modeling Validation Checks](../product-catalog-modeling/SKILL.md#validation-checks), [IsSoldOnlyWithOtherProds](../product-catalog-modeling/selling-models-and-lifecycle.md#issoldonlywithotherprods), [Validate Product Definition](../product-catalog-modeling/bundles-and-cardinality.md#mistakes-validate-product-definition-catches), [PCM load facts](../product-catalog-modeling/catalogs-and-loading.md#pcm-load-facts-264) (fact e), [pricing-setup Validation Checks](../pricing-setup/SKILL.md#validation-checks) |
| 1 | Lookups fresh | No decision table is stale after the last data change; refresh ran after loads | [Freshness](../decision-tables/SKILL.md#freshness--what-the-verdicts-mean), [Validation Checks](../decision-tables/SKILL.md#validation-checks) |
| 2 | Quote places and configures | A quote placed with the intended route carries the intended lines, terms, billing frequencies and attributes; with configuration rules on, each line the source sizes from configuration answers takes the expected quantity, and each refusal or warning shows its message where the platform raises it | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis), [Billing frequency](../billing-setup/SKILL.md#billing-frequency), [quantities-from-attributes.md](../constraint-models/quantities-from-attributes.md), [prediction-checks.md](prediction-checks.md) check 13 |
| 3 | Price | Each line price, discount, total, cost and margin where in scope, and tax (estimated tax, where in scope; it needs a tax engine and tax policy set up first, [build-order.md](build-order.md)) equals the hand-computed value; read the pricing log or waterfall for any difference. After a change to a header field that pricing reads, reprice with Reprice All before reading: a header-only Place PATCH was not priced until Reprice All (a Force Place is expected to do the same `[inferred]`: Reprice All sends Force pricing, traced; not measured) | [runtime-and-observability.md](../pricing-procedures/runtime-and-observability.md), [pricing-setup Validation Checks](../pricing-setup/SKILL.md#validation-checks), [transaction-line-editor Quick Rules](../transaction-line-editor/SKILL.md#quick-rules) (5) |
| 4 | Multi-year and ramp | Each period's price and the uplift equal the expected schedule; read back the ramp schedule. A line edit re-applied a compound uplift to the net unit prices of untouched ramp lines, with totals unchanged (a Place PATCH, and a System PATCH with delta pricing on, measured on one org each, Compound ramp). So after any ramp line edit, reprice the whole quote and read each segment's net unit prices, not its totals `[inferred]`: Reprice All restored them after the Place PATCH, and a whole-quote Place with Force pricing restored them after the System PATCH (one org, delta pricing on, quote only); Force wasn't tried after the Place PATCH | [Validation Checks](../ramped-quotes/SKILL.md#validation-checks), [compound-uplift.md](../ramped-quotes/compound-uplift.md), [ramped-quotes Quick Rules](../ramped-quotes/SKILL.md#quick-rules) (10), [ramped-quotes DO NOT](../ramped-quotes/SKILL.md#do-not) |
| 5 | Rounds | Each round holds its own discounts; the internal round never reaches an order; the intended round becomes the order. The standard order creation traced doesn't check the quote's status (traced in part; not run against a Draft or Rejected quote), so the internal round's guard is a validation or flow the build adds; verify that it refuses | [Validation Checks](../quote-negotiation-rounds/SKILL.md#validation-checks), [Final round to order](../quote-negotiation-rounds/SKILL.md#final-round-to-order) |
| 6 | Approve | A quote crossing each threshold routes to the intended approvers in the intended order; a quote below it does not; recall and resubmit behave as required | [matrix-modeling.md](../advanced-approvals/matrix-modeling.md) (routing by level; recall and resubmit rules), [Validation Checks](../advanced-approvals/SKILL.md#validation-checks) (headless test paths: no-approval, single and multi-dimension, rejection, recall and resubmit, cancel; plus deploy idempotency); the headless test checks assignment and chain order; that the named approvers can act in that order needs a run as those users `[inferred]` |
| 7 | Order | The order carries the winning round's lines and amounts, and activates | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis) |
| 8 | Fulfill | Submission yields the expected plan: step list per order product matches the design table and the derived counts ([prediction-checks.md](prediction-checks.md) check 16); read configuration and runtime separately | [Verify Configuration and Runtime Separately](../dro-plans/authoring-and-deployment.md#5-verify-configuration-and-runtime-separately), [updates-and-runtime.md](../dro-plans/updates-and-runtime.md) |
| 9 | Assets | The sale leaves the expected assets, and none for standalone products marked not assetizable (a non-assetizable child of an assetizable root still becomes an asset, traced in part); asset terms, quantities and attributes match the order | [IsAssetizable](../product-catalog-modeling/selling-models-and-lifecycle.md#isassetizable), [verification.md](../asset-lifecycle-changes/verification.md) |
| 10 | Bill | Activation leaves billing schedules with the promised frequency, treatment and payment term; an invoice run to a target date gives the first invoice with the expected period, amount and due date (estimated tax on a draft, actual tax once posted); on a future-dated replay, check at schedule level and leave invoice values to the replay-dates decision ([plan-template.md](plan-template.md) section 4); milestone items fire as designed (who marks them: see Marking an event milestone done under the Milestone billing link; the trigger from fulfillment is open until verified) | [Validation Checks](../billing-setup/SKILL.md#validation-checks), [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services), [billing-operations Quick Rules](../billing-operations/SKILL.md#quick-rules) (1 to 3), [billing-operations Validation Checks](../billing-operations/SKILL.md#validation-checks) |
| 11 | Contract and documents | The contract exists at the intended point with the intended terms (creation from the sale is decided by Help, `ind.sf_contracts_configure_context_services_to_create_and_update_contracts`, not measured: this step's gate proves it, and on failure follow troubleshooting step 7 in setup-and-diagnostics.md); each document generates with correct values | [setup-and-diagnostics.md](../salesforce-contracts/setup-and-diagnostics.md) (verify template and generated documents), [document-generation Before generation](../document-generation/SKILL.md#before-generation) (active mappers and template references), then generate to verify values |
| 12 | Usage and rating | Usage booked to a completed period rates to the expected amounts, including commitment drawdown and overage; rated summaries are non-zero where expected; the rate cards and rating procedure read back as designed. The usage-consumption live tools are scoped to the QuantumBit catalog: for another catalog, use the rate-management Validation Checks (simulate to the hand-computed rate, freshness, product validator) and read back the customer's rated summaries for the period, and log adapting `validateRatedUsage.apex` (QuantumBit SKUs only) as a skill gap | [Live verification](../usage-consumption/verification.md#live-verification), [Reading a suspicious result](../usage-consumption/verification.md#reading-a-suspicious-result), [rate-management Validation Checks](../rate-management/SKILL.md#validation-checks) |
| 13 | Amend | Each allowed change type (quantity add or remove, swap, cancel) shows the expected prices, attributes, credits and invoice values on each lifecycle quote, through order, activation, the asset and its billing schedules and invoices (on a future-dated replay, as in step 10); refusals show their messages on these paths, and on a bundle sized by configuration answers the unchanged answers carry across two answer changes in a row. Read each lifecycle quote's values before its order activates, and don't reprice it afterwards: a full reprice after activation set a renewal's totals to 0 (measured once, on a renewal; for amendments and cancellations traced in part, not measured) | [verification.md](../asset-lifecycle-changes/verification.md), [Validation Checks](../asset-lifecycle-changes/SKILL.md#validation-checks), [transaction-line-editor Quick Rules](../transaction-line-editor/SKILL.md#quick-rules) (5), [prediction-checks.md](prediction-checks.md) checks 13 and 14 |
| 14 | Renew | The renewal quote prices per policy, including any uplift and ramp; the renewal order and assets carry the values read from the quote before activation; don't reprice the quote afterwards (step 13) | [change-policy-mapping.md](../asset-lifecycle-changes/change-policy-mapping.md), [renewal-asset-creation](../renewal-asset-creation/SKILL.md) |
| 15 | Idempotency and rerun | Re-running any load or task creates no duplicates | [sfdmu-data-plans](../sfdmu-data-plans/SKILL.md), [AGENTS.md checklists](../../../AGENTS.md) |

## Binding steps to rules

Each chain step lists the rule IDs it proves ([SKILL.md](SKILL.md) step 2 numbers them)
and the golden ids that check them. Mark a step not applicable only when the source or a recorded decision
excludes the capability, citing which; where the source is silent on a capability, record
a scope decision first. A rule with no step is a gap in the chain. A test case with no
rule is test data, so drop it or find the rule. The build checks (steps 0, 1 and 15)
need neither a rule nor a golden id. The Reprice and
Attributes golden sets ([plan-template.md](plan-template.md) section 4) need no rule ID; they are always
included and attach to the steps they exercise (pricing, ordering, amending, renewing).

## Test data

Build the transactions from the customer's catalog, with values you can compute by hand.
Generating them through the transaction harness requires a scenario for that catalog; see
[txn-data-harness](../txn-data-harness/SKILL.md) and check what it supports before
promising automation. Renewal tests need assets of the right age; see
[renewal-asset-creation](../renewal-asset-creation/SKILL.md) and its entry conditions.

## Report format

Per step: rule IDs and golden ids, expected, actual, pass or fail, evidence tag from the owner, org
and release, date. List open items (behavior no skill establishes) separately with the
live check that would close each. Say plainly what was not run.
