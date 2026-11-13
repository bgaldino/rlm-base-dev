---
name: implementation-planning
description: >-
  Plan a Revenue Cloud implementation from a customer's commercial source (a
  quoting or costing spreadsheet, a price list export, a public web store, written
  policies, a PRD or an RFP) before anything is built. Covers intake questions, inventorying the source, mapping each
  concept to Revenue Cloud, deciding for each rule whether a repo skill, the
  release's Help and developer-guide snapshot, or a live org settles it, golden tests
  from the source's own worked examples, decisions, phases and gates, the skills
  each phase reads, parallel build sessions, skill gaps, and a ledger that measures
  the plan's predictions against what the build finds. Use the domain skills
  (pricing-setup, pricing-procedures, constraint-models, sfdmu-data-plans, and so
  on) to build what the plan describes.
---

# Implementation Planning — From a Commercial Source to a Revenue Cloud Build Plan

Use this skill when someone hands you a description of how they sell, such as a
spreadsheet, a store, a price list or a requirements document, and wants it modeled
in Revenue Cloud. The output is a **plan for review**, not a build. The plan states
what "done" means, how every rule maps to Revenue Cloud, which source of knowledge
decides each mapping, what the golden tests are, and how the work is split. It
follows the [plan template](plan-template.md). Any agent that can read repository
files can use it.

## Quick Rules

1. **Ask before you plan.** Purpose and success criteria first, one question at a
   time. Then where the build lives, scope, session layout and the runtime surface.
   The [intake questions](#1-intake) list what each answer changes.
2. **Inventory the source completely before mapping it.** For a workbook: every tab,
   named range, data validation and formula, with its cached value. For a store: every
   product, option, price and "not available with" state. Map from the inventory,
   never from memory of the source.
3. **Decide each rule's knowledge source explicitly.** A repo skill or the
   `docs/salesforce/<release>/` snapshot settles it, its build gate does (a custom
   computation), or a live org must. Having no
   skill is a gap to record, not a reason for a live spike. Use the
   rule in [knowledge-sources.md](knowledge-sources.md): the per-area table holds the
   evidence, and the per-rule decision record holds each rule's decision.
4. **Spike live only what the repo can't answer:** a rule that meets one of the four
   triggers in [knowledge-sources.md](knowledge-sources.md). Everything else is modeled
   directly and proved at its build gate.
5. **Golden tests come from the source's own worked examples.** Every expected value
   traces to a cell, a page or a sentence in the source. Recompute calculated values
   from inputs (formula parity), then run every worked example through every rule
   (cross-rule parity) before trusting them.
6. **Test past the first placement.** Reprice, order, amend and renew, and read
   attributes as well as prices. A price that is right once can still drift.
7. **Name the skills each phase reads, and the gaps.** Each phase lists its skills;
   a phase that needed knowledge no skill held becomes a proposed skill or skill
   extension.
8. **The plan is reviewed before anything is built.** Present it, stop, and wait for
   approval.
9. **Measure the build against a frozen copy of the approved plan.** The copy keeps
   the predictions; `plan.md` is revised to as-built, each change citing its ledger ID
   ([step 9](#9-measure-the-build-against-the-plan)).
10. **Run the prediction checks before you predict.** Each check in
    [prediction-checks.md](prediction-checks.md) is a step whose omission modified or
    refuted a prior plan's prediction, or sharpens a guard that build showed too weak:
    a measurement read past its shape, a structure chosen for the new sale only, a
    recommendation with no mechanism, a native guard on the wrong path.

## DO NOT

- **DO NOT** start building (data plans, CML, procedures, org changes) before the plan
  is approved.
- **DO NOT** call something in the source an inconsistency until you have read the
  source's own notes on it. A label that looks contradictory may be defined elsewhere,
  for example a policy whose status a note defines as approved but not yet in the
  calculator. Real inconsistencies become decisions, not silent choices. When a note
  states a rule and a formula breaks it, recommend the stated rule, and keep the
  formula's cached values only to check the extraction. When a stated rule breaks a
  worked example's stated outcome, look for a reading that keeps both (a narrower
  scope, or a data choice such as a line the rule never touches) and recommend it;
  give the literal reading as the alternative and list the examples it breaks. If no
  reading keeps both, prefer a resolution the source states itself (a note on the
  example), and give each option's values; if it states none, recommend the stated rule
  and list the examples it breaks.
- **DO NOT** put customer, brand or third-party commercial data in the public repo.
  Decide where the plan and data live (Quick Rule 1). A private plan may name real
  data; this skill and anything public may not.
- **DO NOT** assert Revenue Cloud behaviour from memory. Cite the skill or the
  snapshot article that says it, or mark the rule for live verification. While a
  release is pre-GA, a live org is ground truth (`AGENTS.md`).
- **DO NOT** plan a header discount to stand in for line or product-line discounts
  without a live test. On a 264 org with an active procedure plan and
  `skipOrgSttPricing` on, a header discount was measured applying twice (`transaction-line-editor` → `runtime-behavior.md`).
- **DO NOT** plan CCI or build-harness work in a git worktree; use the main checkout
  or a regular clone, with separate orgs and file ownership
  ([session-orchestration.md](session-orchestration.md) Rule 2).
- **DO NOT** let a test pass on configuration with rules off. Place quotes with
  configuration rules on, and assert each rejection's own message.
- **DO NOT** assume a source's lifecycle examples can run in the order it lists them.
  Replay them as a dated sequence first. Whether a change dated before an existing
  later change is refused is open: the Help says both (`asset-lifecycle-changes`), so
  an example that depends on it is a live check.

## Entry Conditions

| Situation | Use this skill? | Instead / also |
|---|---|---|
| "Model this spreadsheet / store / price list in Revenue Cloud" | Yes | — |
| "Write a build plan for this demo" with an external source | Yes | — |
| Revising a plan after review | Yes | Keep the decision log and evidence log intact |
| Modeling or building the catalog the plan describes | No | `product-catalog-modeling`, then `sfdmu-data-plans` to load it |
| Building pricing the plan describes | No | `pricing-setup`, `pricing-procedures`, `pricing-wiring`, `expression-sets` |
| Building configuration rules, or sizing quantities from answers | No | `constraint-models` → `quantities-from-attributes.md` |
| Building the approval matrix | No | `advanced-approvals` |
| Bid rounds as quote versions | No | `quote-negotiation-rounds` |
| Billing frequency, treatments, milestones, payment terms | No | `billing-setup` |
| Amend, swap, cancel and renew rules and their numbers | No | `asset-lifecycle-changes` |
| Configuring the line editor the rep uses | No | `transaction-line-editor` |
| Answering one product question ("does Revenue Cloud support X?") | No | `revenue-cloud-docs`, then a live check if pre-GA |
| A demo walkthrough for an existing build | No | `qb-demo-script` |

## Sub-files

- [plan-template.md](plan-template.md): read when writing the plan. Section order,
  what each section must hold, and a self-review checklist.
- [concept-map.md](concept-map.md): read when mapping. Common commercial concepts,
  the Revenue Cloud feature to try first, and the skill that covers it.
- [knowledge-sources.md](knowledge-sources.md): read when deciding which rules need a
  live org. The decision rule, the coverage sweep commands, and how to record the
  result.
- [prediction-checks.md](prediction-checks.md): read before writing decisions, the
  rule decision record, spikes and goldens. Checks a prior build's measurements showed
  the planner must run, each pointing at the domain skill that holds the fact.
- [session-orchestration.md](session-orchestration.md): read when the user wants the
  build split across sessions. Org-per-session layout, file ownership, integration
  gates and session briefs.
- [`scripts/ledger.py`](scripts/ledger.py): the verification ledger
  ([step 9](#9-measure-the-build-against-the-plan)).

---

## Workflow

### 1. Intake

Ask these, one at a time, and record each answer as a decision with its date. Skip any
the request already answers, and say what you assumed instead.

| Question | Why it matters |
|---|---|
| What is the build for (demo, customer proof, benchmark, product extension)? | Sets "done": reproducing worked examples, a walkthrough, or a shipped feature |
| Where does it live (private pack first, public repo behind a flag, or both)? | Sets data handling and the promotion phase |
| What is in scope beyond catalog and standard pricing? | Cost and margin, negotiation and approvals, lifecycle changes and renewal, billing, policies not yet in force |
| Is the source read once, or kept in sync? | Read once means one extraction with a parity check; kept in sync adds a generator to maintain |
| What runtime surface? | The standard Transaction Line Editor and configurator, or custom UI |
| How are quantities derived, and may a rep override them? | Rule-owned sizing or editable defaults (`constraint-models` → `quantities-from-attributes.md`), and the amendment path. A source can say both in different places |
| How should the work be split? | One session, sequential sessions, or parallel sessions each with its own org |
| What matters more: accuracy of the model or polish of the experience? | Decides where the effort and the live verification go |
| Who answers questions about what the source *means*? | The person who owns the source (a pricing team, a product manager), not always the person asking for the build. Some inconsistencies only they can settle |

### 2. Inventory the source

- **Workbook:** use a reader that returns formulas *and* cached values (for example
  `openpyxl` loaded twice, with `data_only=False` and `data_only=True`). List:
    - every tab, named range, data validation, merged range and long note;
    - hidden state: hidden sheets, rows and columns, cell comments, conditional
      formatting, and external links;
    - cell fills and fonts that a legend defines (input, calculated, needs attention).
      A legend is often plain fill colour, which a values-and-formulas read misses; it
      tells an input cell from a calculated one.

  Read rules by named range rather than cell address where the workbook defines one.
- **Web store:** pages are usually rendered by JavaScript, so capture with a browser.
  For each product, record options, prices, option deltas, "not available with"
  states and images, with the capture date.
- **Document (PRD or RFP):** list every priced item, rule and example, citing page
  and section.
- Record the source's identity in the plan: file name, revision, date and a checksum,
  or capture dates.
- **Number the rules.** A rule is one behaviour the source states and that can be
  tested on its own: a sizing rule, a discount program, a policy, an approval trigger,
  a change type. Use the source's own IDs where it has them; otherwise give each one
  an ID. The register goes in the plan's section 3.0
  ([plan-template.md](plan-template.md)). The mapping, the rule decision record and the
  golden tests all refer to these IDs, so the counts agree.

### 3. Map each concept to Revenue Cloud

Use [concept-map.md](concept-map.md). For every concept, write the feature to try first
and the skill that covers it, and keep the source's own numbers next to it. Order
matters as much as the features do: write down the source's order of application and
where it rounds. Some sources round once at the end. Decide where the build rounds (a
Rounding Values step or a `ROUND()` in a formula; the shipped procedures have no
Rounding Values step, `pricing-procedures` → `elements/rounding-values.md`), and again
after a later step that multiplies, such as a ramp uplift, only where the source rounds
after it ([prediction-checks.md](prediction-checks.md) check 11). Add a golden case off the
source's own examples that would show a rounding difference.

### 4. Decide each rule's knowledge source

Use [knowledge-sources.md](knowledge-sources.md). Run the coverage sweep, then apply the
decision rule. The plan gets two records:
- **Per area, the evidence:** the skills, the snapshot articles, prior measured
  knowledge, the source that decides, and why.
- **Per rule, the decision:** which source decides each rule. A rule can carry two
  decisions, for example **Repo** on a new sale and **Live (c)** on an amendment.

Rules that need a live org become spikes, each with the source value it must hit. Run
the knowledge-source checks in [prediction-checks.md](prediction-checks.md) (1–4)
first: a measurement covers only the shape and route it measured.

### 5. Golden tests

- One set per area, in the template's section 4, split where useful: sizing or
  configuration, rules (each with its message, template section 3), standard pricing, programs and edges
  (every band boundary), currency, policies, cost and margin, negotiation, approvals,
  lifecycle changes, billing, plus the template's Reprice and Attributes sets.
- Each expected value cites where it comes from in the source. A value the source
  doesn't show but its rules determine (a band edge, a second example of a formula) is
  allowed: mark it **derived** and cite the rule's cells.
- Recompute calculated values from inputs and match them to the source's own results
  (formula parity). A mis-read rule fails here instead of in the org.
- **A golden an open decision affects asserts the recommended value,** tagged with the
  decision ID, with the alternative's value beside it, and names the gate that needs the
  owner's answer. The build proceeds on the recommendation. When the owner answers, the
  converter regenerates the goldens; nobody edits them by hand.
- Run the golden checks in [prediction-checks.md](prediction-checks.md) (9–15): derived
  quantities at each answer's maximum, proration by day, rounding only where the source
  rounds, line inputs, where a refusal's message appears, answers carried across
  changes, and fresh decision tables.
- **Assert platform-enforced behaviour where the platform enforces it.** Where the
  platform accepts a change and enforces the rule later (at order, activation or
  amendment), the golden asserts at that later step.
- **Cross-rule parity.** Run each worked example through every rule in the register,
  not only its own formula: guards, dependencies and thresholds. A source's summary
  formulas often skip a rule its policy text states (a per-line floor-margin guard, a
  never-below-cost rule). Each violation is a decision, not a silent choice. Run worked
  examples against each other too: in the dated replay each one starts from the state
  the one before left, and an example that ignores that state is a decision.
- **Replay lifecycle examples in date order,** with configuration rules on. Anchor
  the timeline first: the contract start, and whether the replay's dates are in the
  future of the build. The choice is a decision:
    - **Keep the source's dates** (future-dated): exercised in a prior build, where rules
      ran on future-dated amendments as on current-dated ones (`asset-lifecycle-changes`
      Quick Rule 7). Add a current-dated contract for any case that must be shown today.
    - **Shift the replay back by whole years** (backdated): not exercised. It adds a
      backdated new sale; read `rlm-business-apis` → `backdated-asset-lifecycle.md` first.
    - Either way, partial periods prorate by day on the shipped policy, not by month
      ([prediction-checks.md](prediction-checks.md) check 10).
    - At each step, run the running totals through every rule as well as the end state:
      a threshold the contract crosses part way through (a deal-size approval level,
      a band) is a decision too.
    - An example that breaks a sizing rule, or that runs a change dated before an
      existing later one, is a decision. Whether the platform refuses the second case
      is open in `asset-lifecycle-changes`, so plan a live check for it.
- Where the source and Revenue Cloud measure different things, write the mapping into
  the test rather than forcing equality. Example: the source counts an until-cancelled
  monthly line over the whole contract term, while the platform counts it for the
  Pricing Setup default term count.

### 6. Decisions, phases, sessions, skills

Write these in the template's order:
- **Decisions:** each one decided or recommended, with the alternative. Check every
  recommendation and fallback against the Quick Rules of the domain skills it touches.
  A decision that depends on a marker or flag names what sets it, on every path that
  creates the record (API, line editor, clone). Run the structure and decision checks in
  [prediction-checks.md](prediction-checks.md) (5–8): choose each structure against every
  lifecycle change, name each recommendation's mechanism, and name where each native
  guard is enforced.
- **Phases:** each with a gate and its skills.
- **Route prerequisites:** a spike that chooses between routes lists what each route
  needs from the catalog and the model. The catalog phase waits for that spike or
  builds them all, and the plan's dependency line shows that edge. A prior build let a
  pricing spike choose a route while the catalog was built beside it, and the catalog
  and model were amended after pricing had started.
- **Sessions:** see [session-orchestration.md](session-orchestration.md).
- **Skills:** a phase-by-skill matrix.
- **Skill gaps:** areas where the coverage sweep found no skill, and areas a phase
  will measure first. Propose each as a new skill or an extension of an existing one,
  drafted after the phase that exercises it, so it holds measured facts.

### 7. How the build repeats

Decide how the finished build is loaded again on a new org, and write it into the
plan:
- **Overlay pack (private first):** one folder outside the public tree holding the
  build's data plans, constraint models, procedure overlays and metadata, with a
  manifest that lists its steps, side effects and gates. A loader runs Foundations'
  own CCI tasks on it with explicit paths, onto a base build.
    - The repo ships no pack format or loader. The first build writes them; plan that
      as build work, not as existing tooling.
    - **Write the loader at the end of the catalog phase and extend it at each later
      gate,** not only in the pack phase. Spike sessions after the catalog and orgs that
      replace expiring ones load from it, so the fresh-org load runs a loader exercised
      since the catalog phase. A prior build did this, filling its later spike orgs and
      its integration org with it. A multi-session build can outlast its orgs: the TUI
      caps an org at 30 days, and no harness or TUI code lengthens an existing org's life
      (`build-harness` → Keep an org for a multi-day build).
    - After every deploy, query the org for the components. A prior build saw a deploy
      from a path the project ignored (under a dot-folder) report success with an empty
      package; deploying from a temporary copy avoided it.
- **Feature flag (public):** the same content under `datasets/`, `unpackaged/` and
  `cumulusci.yml`, behind a flag (`repo-integration`, `cci-orchestration`).
- **Flow or task only:** when the build is small enough to live in one task.

### 8. Review

Run the self-review in [plan-template.md](plan-template.md), present the plan with its
open decisions, and stop for approval. Record review changes as a revision with its
date, not by rewriting history.

When the build also measures how well the plan predicted it (a test of this skill or
of the planner), review in three steps:
1. **Blind generation:** a fresh session with only the source, the intake answers and
   the skills writes the plan.
2. **Independent audit:** a second fresh agent checks it against the source and the
   skills, and lists the edits the build needs.
3. **Edits on a copy:** the edits go into a copy that becomes the build plan, with a
   section listing them. The blind plan is kept unchanged, for measurement.

### 9. Measure the build against the plan

Keep a verification ledger with [`scripts/ledger.py`](scripts/ledger.py); its `--help`
has the commands. Run it from the plan's folder; for a private plan that folder is in
the pack's repo, since the ledger copies the plan's rows.
- **Freeze the plan at approval.** Copy it to `plan-as-approved.md` and commit the copy;
  `init --plan` reads that copy, as do the converter's plan-anchor tests. `plan.md` then
  tracks the build: revise it to as-built, with each change citing the ledger ID or
  decision it comes from, and the evidence log (section 7) holds the trail. A prior
  build ran it this way.

The ledger reads the plan's decisions, rule decision record and P2 spike table, by the
names [plan-template.md](plan-template.md) gives them, and gives each row:
- an **origin:** in the blind plan unchanged, edited, or added; or given to the planner
  (an intake answer, or a decision a person settled later), which doesn't count toward
  accuracy;
- an **outcome,** the latest recorded (name the gate in the evidence): `affirmed`, `modified` (held with different values or
  configuration), `refuted` (failed) or `inconclusive` (not tested).

For an edited row, the evidence also says whether the blind text would have held.
Sessions report each outcome with its evidence; the main session records it. Findings
go to the ledger and the evidence log, and into `plan.md` as as-built revisions that
cite them; never into `plan-as-approved.md`, so the predictions stay measurable. A
refuted skill claim is fixed in that skill
([knowledge-sources.md](knowledge-sources.md) → After the build).

**Score each later blind regeneration against the measured outcomes.** When the
planning skill or the domain skills change, a fresh session regenerates the plan blind
from the same source (step 8), and its accuracy is scored:
1. `ledger.py truth` writes `truth.json` beside the ledger: every measured item, with
   what the plan predicted and what the build measured.
2. A fresh judge agent, given only the regenerated plan and `truth.json`, labels every
   item by topic, since the regeneration's IDs won't match: **hit** (predicts the
   measured result), **hedged** (doesn't assert it, but routes it to a live measurement
   that would find it), **miss** (asserts what the build refuted or changed) or
   **absent** (doesn't address it). The judgments file format is in `--help`.
3. `ledger.py score <judgments.json> <label>` writes the tally to `regen-scores.md`,
   beside the measured plan's own baseline (affirmed = hit, modified or refuted = miss,
   inconclusive = hedged), and lists what is still missed or absent. Those items point
   at the next skill fixes ([knowledge-sources.md](knowledge-sources.md) → After the
   build).

---

## Examples

**Example 1 — a pricing workbook.** A price list tab, a tab of bundles with their
options, a tab of discount tiers, and a calculator tab that prices a sample order.
- **Inventory:** each tab's named ranges and formulas. The calculator's cached totals
  become golden values once the parity check recomputes them.
- **Mapping:** bundles → configurable bundles with component groups; options →
  attributes or components; tiers → volume and tier discounts.
- **Knowledge sources:** run the sweep for each area and decide from what it finds:
    - An area a skill documents with measurements is **Repo**, unless a live trigger
      applies to one of its rules.
    - An area only the Help or developer guide documents is **Snapshot**, and a skill
      gap.
    - A rule that a skill's measured defect, or a measured contradiction of the docs,
      touches is **Live (b)**. The area row only summarizes its rules.
  Don't carry a decision over from another plan or release; sweep again.
- **Golden tests:** the calculator's lines and totals, and every tier boundary
  (derived from the tier table).

**Example 2 — a public web store.** Configurable products with option deltas, presets,
service plans and trade-in credits.
- **Mapping:** one configurable root per model plus a root per preset; options as
  attributes with attribute-based price; service plans as bundle components with
  their own selling models, unless a plan must be renewed or cancelled. A component
  alone is refused (`asset-lifecycle-changes` Quick Rule 3), and a one-time root
  renewed to quantity 0 (Quick Rule 5), so a renewable plan under a one-time device
  root is its own line. Option exclusions and dependencies as CML.
- **Source handling:** captured with a browser; an independent re-capture of a sample
  verifies it.
- **Golden tests:** every preset price and a sample of custom configurations, plus an
  allowed-and-disallowed option matrix checked through the configure API with rules on.

**Example 3 — routing.** "Add volume tiers to the existing price book" is not this skill:
use `pricing-setup` and `pricing-procedures`. "We have a costing spreadsheet; can Revenue
Cloud do this?" is this skill, starting with the intake questions.

## Validation Checks

Before presenting the plan:

- Every skill named in the plan exists (this skill may still be on an unmerged
  branch while it is being tested):

  Run from the Foundations repo root, with `PLAN` set to the plan's path (it may live
  in a private repo):

  The first command lists every hyphenated name in backticks that is not a skill, to
  check by hand; check single-word skill names (`toolchain`, `troubleshooting`) by eye.
  The second lists every `.md` file named in backticks or in a Markdown link; a file
  printed without a skill before it needs its skill looked up on its line before you
  check it with `ls`.

  ```bash
  PLAN=<path to plan.md>; test -f "$PLAN" || echo "no plan at $PLAN"
  for s in $(grep -oE '`[a-z0-9]+(-[a-z0-9]+)+`' "$PLAN" | tr -d '`' | sort -u); do
    [ -f ".cursor/skills/$s/SKILL.md" ] || echo "not a skill: $s"; done
  grep -oE '`[a-z0-9-]+` → `[^`]+\.md`|`[^` ]+\.md`|\]\([^)]+\.md\)' "$PLAN" | sort -u
  ```

- Every sub-file named exists under its skill.
- Every script the plan cites lives in the pack or the repo, never in a scratch or
  temporary folder: those paths are gone by the time someone re-runs the check.
- Every snapshot article cited exists under `docs/salesforce/<release>/`.
- Every golden value cites its place in the source, and both the formula and the
  cross-rule parity checks passed.
- Rule IDs and counts agree across the register, the rule decision record and the
  golden tests.
- Every area has a knowledge-source row, and every live spike has a value it must hit.
- Each check in [prediction-checks.md](prediction-checks.md) that applies ran, and its
  result is in the decision, rule row, spike or golden it touches.
- Every decision is marked decided (with a date) or recommended (with the alternative).
- Nothing in a public file names customer, brand or third-party commercial data.
- The plan's self-review checklist ([plan-template.md](plan-template.md)) passes.
