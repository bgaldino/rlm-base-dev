---
name: commercial-model-planning
description: >-
  Turn a commercial source (a quoting or costing spreadsheet, a public web store,
  a price list export, a PRD or an RFP) into a Revenue Cloud build plan before
  anything is built. Covers intake questions, inventorying the source, mapping each
  concept to Revenue Cloud, deciding for each rule whether a repo skill, the
  release's Help and developer-guide snapshot, or a live org settles it, golden tests
  from the source's own worked examples, decisions, phases and gates, the skills
  each phase reads, parallel build sessions, and skill gaps. Use the domain skills
  (pricing-setup, pricing-procedures, constraint-models, sfdmu-data-plans, and so
  on) to build what the plan describes.
---

# Commercial Model Planning — From a Source to a Revenue Cloud Build Plan

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
9. **Measure the build against the plan; don't rewrite the plan to match it.** Each
   prediction's outcome goes in a verification ledger and the evidence log
   ([step 9](#9-measure-the-build-against-the-plan)).

## DO NOT

- **DO NOT** start building (data plans, CML, procedures, org changes) before the plan
  is approved.
- **DO NOT** call something in the source an inconsistency until you have read the
  source's own notes on it. A label that looks contradictory may be defined elsewhere,
  for example a policy whose status a note defines as approved but not yet in the
  calculator. Real inconsistencies become decisions, not silent choices. When a note
  states a rule and a formula breaks it, recommend the stated rule, and keep the
  formula's cached values only to check the extraction.
- **DO NOT** put customer, brand or third-party commercial data in the public repo.
  Decide where the plan and data live (Quick Rule 1). A private plan may name real
  data; this skill and anything public may not.
- **DO NOT** assert Revenue Cloud behaviour from memory. Cite the skill or the
  snapshot article that says it, or mark the rule for live verification. While a
  release is pre-GA, a live org is ground truth (`AGENTS.md`).
- **DO NOT** plan a header discount to stand in for line or product-line discounts
  without a live test. On a 264 org with an active procedure plan and
  `skipOrgSttPricing` on, a header discount was measured applying twice (`transaction-line-editor` → `runtime-behavior.md`).
- **DO NOT** plan CCI or build-harness work in a git worktree nested in the checkout.
  CCI finds the project root by a `.git` directory, so from a worktree it runs the
  parent checkout's files and ignores the worktree's changes. Use the main checkout or
  a regular clone, with separate orgs and file ownership
  ([session-orchestration.md](session-orchestration.md)).
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
- [session-orchestration.md](session-orchestration.md): read when the user wants the
  build split across sessions. Org-per-session layout, file ownership, integration
  gates and session briefs.
- [`scripts/ledger.py`](scripts/ledger.py): the verification ledger
  ([step 9](#9-measure-the-build-against-the-plan)); tested by
  `tests/test_commercial_model_planning_ledger.py`.

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
| How should the work be split? | One session, sequential sessions, or parallel sessions each with its own org |
| What matters more: accuracy of the model or polish of the experience? | Decides where the effort and the live verification go |
| Who answers questions about what the source *means*? | The person who owns the source (a pricing team, a product manager), not always the person asking for the build. Some inconsistencies only they can settle |

### 2. Inventory the source

- **Workbook:** use a reader that returns formulas *and* cached values (for example
  `openpyxl` loaded twice, with `data_only=False` and `data_only=True`). List:
    - every tab, named range, data validation, merged range and long note;
    - hidden state: hidden sheets, rows and columns, cell comments, conditional
      formatting (often the "input cell" legend), and external links.

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
  a change type. Use the source's own IDs where it has them (SR-01, P-03); otherwise
  give each one an ID. The register goes in the plan's section 3.0
  ([plan-template.md](plan-template.md)). The mapping, the rule decision record and the
  golden tests all refer to these IDs, so the counts agree.

### 3. Map each concept to Revenue Cloud

Use [concept-map.md](concept-map.md). For every concept, write the feature to try first
and the skill that covers it, and keep the source's own numbers next to it. Order
matters as much as the features do: write down the source's order of application and
where it rounds. Some sources round once at the end. Decide where the build rounds (a
Rounding Values step or a `ROUND()` in a formula; the shipped procedures have no
Rounding Values step, `pricing-procedures` → `elements/rounding-values.md`), and add a
golden case off the source's own examples that would show a rounding difference.

### 4. Decide each rule's knowledge source

Use [knowledge-sources.md](knowledge-sources.md). Run the coverage sweep, then apply the
decision rule. The plan gets two records:
- **Per area, the evidence:** the skills, the snapshot articles, prior measured
  knowledge, the source that decides, and why.
- **Per rule, the decision:** which source decides each rule. A rule can carry two
  decisions, for example **Repo** on a new sale and **Live (c)** on an amendment.

Rules that need a live org become spikes, each with the source value it must hit.

### 5. Golden tests

- One set per area, in the template's section 4, split where useful: sizing or
  configuration, rules (with expected messages), standard pricing, programs and edges
  (every band boundary), currency, policies, cost and margin, negotiation, approvals,
  lifecycle changes, billing, plus the template's Reprice and Attributes sets.
- Each expected value cites where it comes from in the source. A value the source
  doesn't show but its rules determine (a band edge, a second example of a formula) is
  allowed: mark it **derived** and cite the rule's cells.
- Recompute calculated values from inputs and match them to the source's own results
  (formula parity). A mis-read rule fails here instead of in the org.
- **Every rule that rejects or warns has its message in the plan,** in the rule's own
  words, and the rules golden set asserts it. A rule left without one gets a message
  made up at build time, which no golden then checks.
- **Assert platform-enforced behaviour where the platform enforces it.** A lock or
  limit the platform lets a quote save with, then refuses at order, is asserted at the
  order (or in the error log it writes), not at save. When the enforcement point is
  unknown, the golden names it as part of a spike's must-hit.
- **Cross-rule parity.** Run each worked example through every rule in the register,
  not only its own formula: guards, dependencies and thresholds. A source's summary
  formulas often skip a rule its policy text states (a per-line floor-margin guard, a
  never-below-cost rule). Each violation is a decision, not a silent choice.
- **Replay lifecycle examples in date order,** with configuration rules on. Anchor
  the timeline first (the contract start, and whether the replay's dates are in the
  future of the build), and state whether proration is by month or by day.
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
  creates the record (API, line editor, clone).
- **Phases:** each with a gate and its skills.
- **Route prerequisites:** a spike that chooses between routes lists, for each
  candidate, what it needs from the catalog and the model (a classification, a
  price-impacting attribute, a CML line). The catalog phase either waits for that spike
  or builds every candidate's prerequisites; otherwise its files are amended after a
  later phase has started.
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
      as part of the pack phase, not as existing tooling.
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

Track every prediction in a verification ledger: each rule in the rule decision record,
each decision, and each live spike's must-hit. The skill ships the script,
[`scripts/ledger.py`](scripts/ledger.py) (standard library). Run it from the plan's
folder:

```bash
L=<Foundations root>/.cursor/skills/commercial-model-planning/scripts/ledger.py
python3 "$L" init --plan plan.md --blind <blind plan> [--intake <IDs, e.g. D1-D6>] [--owner <IDs>]
python3 "$L" record <ID> <outcome> "<org, record ids, values>" [--path "<what was built>"] \
  [--skill "<skill/file: claim>"] [--blind-right yes|no]
python3 "$L" report   # writes verification/scorecard.md
```

- **Origin,** set by `init`: `blind` (in the blind plan unchanged), `edited` (changed by
  the audit's edits; the blind text is kept), `added`, `intake` or `owner` (decisions
  given to the planner, excluded from accuracy). Without `--blind`, every item is
  `blind`.
- **Outcome,** set at each gate: `affirmed` (built as predicted, goldens pass),
  `modified` (works with a changed path or values), `refuted` (the prediction was wrong;
  a fallback or another path was needed) or `inconclusive`.
- `init` finds the plan's sections by the template's headings and labels ("2. Decisions",
  "Rule decision record", "P2 Live spikes"; see [plan-template.md](plan-template.md)) and
  warns when one has no rows. Re-running it adds new rows, keeps every recorded outcome
  and first prediction, and re-applies `--intake` and `--owner`, so a decision the source
  owner settles later can still leave the accuracy count.
- **Sessions report; the main session records.** A session reports per item: outcome,
  path, evidence, and the skill file and line when a refutation traces to a skill claim.
- **Findings go to the ledger and the evidence log.** The plan isn't rewritten to match
  what the build found, so the prediction stays measurable. A refuted or modified skill
  claim is fixed in that skill ([knowledge-sources.md](knowledge-sources.md) → After the
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
- Every decision is marked decided (with a date) or recommended (with the alternative).
- Nothing in a public file names customer, brand or third-party commercial data.
- The plan's self-review checklist ([plan-template.md](plan-template.md)) passes.
