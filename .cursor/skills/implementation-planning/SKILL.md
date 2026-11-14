---
name: implementation-planning
description: >-
  Turn a customer's written requirements into a staged Revenue Cloud build plan across
  domains, routing each decision and build item to the owning skill. Covers requirement
  intake with the questions to ask when the source is silent, a decision log, a
  cross-domain build order, plan self-review checks and a chained acceptance checklist
  from quote to invoice, usage and renewal. Use when given a requirements document,
  statement of work or RFP, when asked to plan or scope a build, when a plan must say what
  to build in what order, or before presenting any multi-domain plan. Domain mechanics
  stay in the domain skills; this one only sequences and routes.
---

# Implementation Planning — Requirements to a Staged Build Plan

Use this skill to turn a customer's written requirements into a plan an implementer can
execute and a reviewer can check. It does not restate domain rules. It tells you what to
extract, what to decide and record, what must exist before what, how to self-review the
plan, and how to verify the result end to end. Every rule it summarizes is owned by a
linked skill section; read that section before relying on the summary. Any agent that can
read repository files can use it.

## Quick Rules

1. **Extract before you design.** Walk the source through the
   [intake categories](intake-and-decisions.md#intake-categories). Record each requirement
   as stated, quoted or cited. A category the source does not mention is a question, not a
   blank to fill with a default.
2. **Ask or flag; never assume.** Where the source is silent, use that category's
   questions. If nobody can answer yet, log an assumption with the owner who must confirm
   it, and mark every plan item that depends on it.
3. **Log every decision with the choice and why.** Use the
   [decision log](intake-and-decisions.md#decision-log); each row links the skill section
   that explains the options. A decision with no reason is not made yet.
4. **Order the build by prerequisites, not by domain.** Use the
   [build order](build-order.md). It is a graph of what must exist before what, in neutral
   terms. The repo's own flow order is one realization of it, not the plan for a customer
   org.
5. **Values come from the customer.** A name, price, term, count or threshold in the plan
   must trace to the source or to a logged assumption. Never carry over a sample, demo or
   repo-shipped value.
6. **Flag what nobody measured.** The domain skills tag behavior as Help-documented,
   inferred, traced or measured. Carry the tag into the plan. Behavior tagged open or
   "not measured" becomes a verification item, not a promise.
7. **Derive counts.** Instances per decomposition scope, lines per bundle, periods per
   term and records per load come from the model and the source, not from a remembered
   example. Show the derivation.
8. **Self-review before presenting.** Run the [plan checks](#plan-self-review) and say
   which passed.
9. **Close with the acceptance chain.** Every plan ends with the
   [acceptance chain](acceptance-chain.md), each step bound to the requirement it proves.

## DO NOT

- **DO NOT** restate or paraphrase a domain skill's rules as your own. Link the owning
  section; if the rule is not written down there, say so and treat it as open.
- **DO NOT** reuse the repo's sample catalog, data plans, names or numbers as the
  customer's plan. They are illustrations. See
  [Instances vs. mechanism](../skill-authoring/SKILL.md#instances-vs-mechanism).
- **DO NOT** hard-code this repo's flow step numbers in a plan or in documentation. Cite
  steps by name. A plan for a customer org does not run this repo's flow at all unless the
  customer asked for the repo build.
- **DO NOT** treat a feature as available because a skill mentions it. Establish the target
  release and org type first ([revenue-cloud-docs](../revenue-cloud-docs/SKILL.md)).
- **DO NOT** resolve a conflict between requirements silently. Log it as a decision with
  both readings.
- **DO NOT** present measured-only behavior (one org, one release) as a platform
  guarantee.
- **DO NOT** run any build step from this skill. Execution belongs to the domain skills
  and the repo's pre-merge procedure in [AGENTS.md](../../../AGENTS.md).

## Entry Conditions

| Request | Route |
|---|---|
| "Here is the customer's requirements, plan the build" | This skill, from [Workflow](#workflow) |
| "In what order do I build X, Y, Z" | [build-order.md](build-order.md) |
| "What do I ask the customer about billing, usage, approvals" | [intake-and-decisions.md](intake-and-decisions.md) |
| "How do I prove the whole thing works" | [acceptance-chain.md](acceptance-chain.md) |
| One domain only (a catalog, a pricing rule, a DRO plan) | The domain skill; use [Domain routing](#domain-routing) |
| Add this repo's feature, data plan or metadata | [repo-integration](../repo-integration/SKILL.md) |
| Prepare a QuantumBit demo or workshop org | [qb-demo-script](../qb-demo-script/SKILL.md), [df-workshop-setup](../df-workshop-setup/SKILL.md) |
| Debug a failing build step | [troubleshooting](../troubleshooting/SKILL.md) |

## Workflow

1. **Fix the target.** Release, org type, editions and enabled features. A fresh org and
   an upgraded org can differ; the live org is ground truth
   ([revenue-cloud-docs](../revenue-cloud-docs/SKILL.md)).
2. **Intake.** Extract requirements per category with citations to the source
   ([intake-and-decisions.md](intake-and-decisions.md#intake-categories)). Produce a
   requirements table: id, category, statement, source location, status
   (stated / inferred / missing).
3. **Close the gaps.** For each missing item ask the category's questions. Batch them into
   one list for the customer, grouped by owner. Record answers or assumptions.
4. **Decide.** Fill the [decision log](intake-and-decisions.md#decision-log). Route each
   decision to its owning section and read it before choosing.
5. **Sequence.** Place every build item on the [graph](build-order.md#prerequisite-graph).
   Group into stages with an exit check each; independent branches can proceed in
   parallel.
6. **Self-review** ([below](#plan-self-review)), then present the plan: requirements
   table, decision log, staged build items, open items, acceptance chain.
7. **Hand off.** Each build item names its owning skill so the implementer starts there.

## Domain routing

| Domain | Owner | Owning decision or setup section |
|---|---|---|
| Catalog, bundles, selling models | [product-catalog-modeling](../product-catalog-modeling/SKILL.md) | [Product vs attribute vs component](../product-catalog-modeling/SKILL.md#product-vs-attribute-vs-component) |
| Configurator rules | [constraint-models](../constraint-models/SKILL.md) | [Entry Conditions](../constraint-models/SKILL.md#entry-conditions) |
| Pricing enablement, price books | [pricing-setup](../pricing-setup/SKILL.md) | [Setup order](../pricing-setup/SKILL.md#setup-order) |
| Pricing procedure elements | [pricing-procedures](../pricing-procedures/SKILL.md) | [Element catalog](../pricing-procedures/SKILL.md#element-catalog) |
| Pricing layers in dependency order | [pricing-wiring](../pricing-wiring/SKILL.md) | [Reusable Layering Model](../pricing-wiring/SKILL.md#reusable-layering-model) |
| Procedure authoring and lifecycle | [expression-sets](../expression-sets/SKILL.md) | Skill entry |
| Lookup tables and freshness | [decision-tables](../decision-tables/SKILL.md) | [The timing rule](../decision-tables/SKILL.md#the-timing-rule) |
| Context definitions and tags | [context-service](../context-service/SKILL.md) | Skill entry |
| Approvals | [advanced-approvals](../advanced-approvals/SKILL.md) | [matrix-modeling.md](../advanced-approvals/matrix-modeling.md) |
| Quote rounds | [quote-negotiation-rounds](../quote-negotiation-rounds/SKILL.md) | [The round model](../quote-negotiation-rounds/SKILL.md#the-round-model) |
| Ramps | [ramped-quotes](../ramped-quotes/SKILL.md) | [Ramps](../product-catalog-modeling/selling-models-and-lifecycle.md#ramps) |
| Line editor and quote UI | [transaction-line-editor](../transaction-line-editor/SKILL.md) | [Discovery](../transaction-line-editor/SKILL.md#discovery) |
| Orders, APIs | [rlm-business-apis](../rlm-business-apis/SKILL.md) | [Transaction Lifecycle APIs](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis) |
| Fulfillment | [dro-plans](../dro-plans/SKILL.md) | [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md) |
| Assets and lifecycle changes | [asset-lifecycle-changes](../asset-lifecycle-changes/SKILL.md) | [Questions to settle in the plan](../asset-lifecycle-changes/change-policy-mapping.md#questions-to-settle-in-the-plan) |
| Billing | [billing-setup](../billing-setup/SKILL.md) | [Billing frequency](../billing-setup/SKILL.md#billing-frequency) |
| Usage and rating | [usage-consumption](../usage-consumption/SKILL.md) | [The Pipeline](../usage-consumption/SKILL.md#the-pipeline) |
| Contracts | [salesforce-contracts](../salesforce-contracts/SKILL.md) | [Workflow](../salesforce-contracts/SKILL.md#workflow) |
| Documents | [document-generation](../document-generation/SKILL.md), [odt-authoring](../odt-authoring/SKILL.md) | Skill entries |
| Data loading | [sfdmu-data-plans](../sfdmu-data-plans/SKILL.md) | Skill entry |
| Schema questions | [revenue-cloud-data-model](../revenue-cloud-data-model/SKILL.md) | Skill entry |
| Test data and harness | [txn-data-harness](../txn-data-harness/SKILL.md) | Skill entry |

Domains with no owning skill today (tax, collections, invoice runs and payments beyond
billing treatment, usage-product design, installation fulfillment to billing triggers):
state "no skill owns this" in the plan, point to the Help snapshot via
[revenue-cloud-docs](../revenue-cloud-docs/SKILL.md), and mark the item open.

## Plan self-review

Run before presenting. State pass or fail for each; a fail is fixed or listed as open.

| # | Check | How |
|---|---|---|
| 1 | Every requirement maps to a decision or a build item | Walk the requirements table; no row without a target id |
| 2 | Every decision has a choice, a reason and a linked section | Walk the decision log |
| 3 | Every value is the customer's | Search the plan for each name, price, term and count; each traces to the source or a logged assumption. No sample, demo or repo value remains |
| 4 | Every measured-only or open behavior is flagged | Search the plan for each domain-skill claim it relies on; carry the skill's tag; open items become verification steps |
| 5 | Every count is derived | Instances per decomposition scope, lines per bundle, periods per term: write the arithmetic next to the number |
| 6 | Every build item has a prerequisite on the graph | No item floats; no cycle |
| 7 | Every stage has an exit check | Taken from the owner's Validation Checks |
| 8 | Silent categories are listed | Each intake category is covered, asked, or marked not applicable with the customer's confirmation |
| 9 | Ownerless areas are named | The no-owner list above, with an open item each |
| 10 | The acceptance chain covers every requirement | Each chain step cites requirement ids; a requirement no step proves is a gap |

## Sub-files

| File | Read when |
|---|---|
| [intake-and-decisions.md](intake-and-decisions.md) | Extracting requirements, asking the customer, recording decisions |
| [build-order.md](build-order.md) | Sequencing build items; cross-checking against the repo's flow |
| [acceptance-chain.md](acceptance-chain.md) | Writing the end-to-end verification checklist |
| [worked-example.md](worked-example.md) | Seeing intake, decisions, order and chain applied to an invented business |

## Examples

### Example 1: route a multi-domain request

Request: "Plan the build for this customer's contract-based subscription service with
tiered usage." Read intake categories for catalog, selling models, usage, billing and
renewals; ask the questions for any the source skips; log decisions; place items on the
graph; present with the chain. Do not start at pricing procedures.

### Example 2: single-domain request that is really multi-domain

Request: "Set up discounts for this customer." Check intake for discount scope (header or
line, per round, approval thresholds) first. Pricing elements are
[pricing-procedures](../pricing-procedures/SKILL.md); thresholds that need sign-off bring in
[advanced-approvals](../advanced-approvals/SKILL.md); rounds bring in
[quote-negotiation-rounds](../quote-negotiation-rounds/SKILL.md).

## Validation Checks

- `python3 scripts/ai/analyze_agent_tooling.py check` after editing this skill.
- `python3 scripts/ai/skill_manifest.py --check` after the manifest entry changes.
- Every relative link in this directory resolves; every domain section linked still
  exists after a domain skill is edited. Update the links in the same change.
- When a domain skill gains or loses a prerequisite, update [build-order.md](build-order.md)
  and re-check its cross-check table against `cumulusci.yml`.
- Follow [doc-consistency](../doc-consistency/SKILL.md) before a PR.
