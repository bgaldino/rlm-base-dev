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
   `docs/salesforce/<release>/` snapshot settles it, or a live org must. Having no
   skill is a gap to record, not a reason for a live spike. Use the
   rule in [knowledge-sources.md](knowledge-sources.md), and record the decision per
   rule in the plan.
4. **Spike live only what the repo can't answer.** A live spike is for a corpus that
   is silent, a repo measurement that differs from the docs, numbers across the
   asset lifecycle, or docs that disagree. Everything else is modeled directly and
   proved at its build gate.
5. **Golden tests come from the source's own worked examples.** Every expected value
   traces to a cell, a page or a sentence in the source. Recompute calculated values
   from inputs (formula parity) before trusting them.
6. **Test past the first placement.** Reprice, order, amend and renew, and read
   attributes as well as prices. A price that is right once can still drift.
7. **Name the skills each phase reads, and the gaps.** Each phase lists its skills;
   a phase that needed knowledge no skill held becomes a proposed skill or skill
   extension.
8. **The plan is reviewed before anything is built.** Present it, stop, and wait for
   approval.

## DO NOT

- **DO NOT** start building (data plans, CML, procedures, org changes) before the plan
  is approved.
- **DO NOT** call something in the source an inconsistency until you have read the
  source's own notes on it. A label that looks contradictory may be defined elsewhere,
  for example a "Proposed" policy that a note defines as "approved, not yet in the
  calculator". Real inconsistencies become decisions, not silent choices.
- **DO NOT** put customer, brand or third-party commercial data in the public repo.
  Decide where the plan and data live (Quick Rule 1). A private plan may name real
  data; this skill and anything public may not.
- **DO NOT** assert Revenue Cloud behaviour from memory. Cite the skill or the
  snapshot article that says it, or mark the rule for live verification. While a
  release is pre-GA, a live org is ground truth (`AGENTS.md`).
- **DO NOT** plan a header discount to stand in for line or product-line discounts
  without a live test. On a 264 org with an active procedure plan, a header discount
  was measured applying twice.
- **DO NOT** plan parallel sessions in git worktrees for CCI work. CCI runs from the
  project root and ignores worktree changes; use separate orgs and file ownership
  instead ([session-orchestration.md](session-orchestration.md)).
- **DO NOT** let a test pass on configuration with rules off. Place quotes with
  configuration rules on, and assert each rejection's own message.

## Entry Conditions

| Situation | Use this skill? | Instead / also |
|---|---|---|
| "Model this spreadsheet / store / price list in Revenue Cloud" | Yes | — |
| "Write a build plan for this demo" with an external source | Yes | — |
| Revising a plan after review | Yes | Keep the decision log and evidence log intact |
| Building the catalog the plan describes | No | `sfdmu-data-plans`, `revenue-cloud-data-model` |
| Building pricing the plan describes | No | `pricing-setup`, `pricing-procedures`, `pricing-wiring`, `expression-sets` |
| Building configuration rules | No | `constraint-models` |
| Answering one product question ("does Revenue Cloud support X?") | No | `revenue-cloud-docs`, then a live check if pre-GA |
| A demo walkthrough for an existing build | No | `qb-demo-script` |

## Sub-files

- [plan-template.md](plan-template.md): read when writing the plan. Section order,
  what each section must hold, and a self-review checklist.
- [concept-map.md](concept-map.md): read when mapping. Common commercial concepts,
  the Revenue Cloud feature to try first, the skill that covers it, and the usual
  live-verification triggers.
- [knowledge-sources.md](knowledge-sources.md): read when deciding which rules need a
  live org. The decision rule, the coverage sweep commands, and how to record the
  result.
- [session-orchestration.md](session-orchestration.md): read when the user wants the
  build split across sessions. Org-per-session layout, file ownership, integration
  gates and session briefs.

---

## Workflow

### 1. Intake

Ask these, one at a time, and record each answer as a decision with its date. Skip any
the request already answers, and say what you assumed instead.

| Question | Why it matters |
|---|---|
| What is the build for (demo, customer proof, benchmark, product extension)? | Sets "done": reproducing worked examples, a walkthrough, or a shipped feature |
| Where does it live (private pack first, public repo behind a flag, or both)? | Sets data handling and the promotion phase |
| What is in scope beyond catalog and standard pricing? | Cost and margin, negotiation and approvals, lifecycle changes and renewal, proposed policies |
| Is the source read once, or kept in sync? | Read once means one extraction with a parity check; kept in sync adds a generator to maintain |
| What runtime surface? | The standard Transaction Line Editor and configurator, or custom UI |
| How should the work be split? | One session, sequential sessions, or parallel sessions each with its own org |
| What matters more: accuracy of the model or polish of the experience? | Decides where the effort and the live verification go |
| Who answers questions about what the source *means*? | The person who owns the source (a commercial desk, a product manager), not always the person asking for the build. Some inconsistencies only they can settle |

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
  give each one an ID in the inventory. The mapping, the knowledge-source table and the
  golden tests all refer to these IDs, so the counts agree.

### 3. Map each concept to Revenue Cloud

Use [concept-map.md](concept-map.md). For every concept, write the feature to try first
and the skill that covers it, and keep the source's own numbers next to it. Order
matters as much as the features do: write down the source's order of application and
where it rounds. Some sources round once at the end; a pricing procedure may round at
each step.

### 4. Decide each rule's knowledge source

Use [knowledge-sources.md](knowledge-sources.md). Run the coverage sweep, then apply the
decision rule. The plan gets a table with one row per area: the skills, the snapshot
articles, prior measured knowledge, the source that decides, and why. Rules that need a
live org become spikes, each with the source value it must hit.

### 5. Golden tests

- One set per area: sizing or configuration, rules (with expected messages), standard
  pricing, programs and edges (every band boundary), currency, policies, negotiation,
  approvals, lifecycle changes, reprice, and attributes.
- Each expected value cites where it comes from in the source. A value the source
  doesn't show but its rules determine (a band edge, a second example of a formula) is
  allowed: mark it **derived** and cite the rule's cells.
- Recompute calculated values from inputs and match them to the source's own results
  (formula parity). A mis-read rule fails here instead of in the org.
- Where the source and Revenue Cloud measure different things, write the mapping into
  the test rather than forcing equality. Example: a monthly plan the source counts
  for the contract term "for comparison only".

### 6. Decisions, phases, sessions, skills

Write these in the template's order:
- **Decisions:** each one decided or recommended, with the alternative.
- **Phases:** each with a gate and its skills.
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
  `pack.yml` that lists its steps, side effects and gates. A loader script runs
  Foundations' own CCI tasks on it with explicit paths, onto a base build.
    - Deploy metadata from a temporary copy: `sf` ignores paths under a dot-folder
      relative to the project root, and a deploy from there reports success with an
      empty package.
    - After every deploy, check the org for the components.
- **Feature flag (public):** the same content under `datasets/`, `unpackaged/` and
  `cumulusci.yml`, behind a flag (`repo-integration`, `cci-orchestration`).
- **Flow or task only:** when the build is small enough to live in one task.

### 8. Review

Run the self-review in [plan-template.md](plan-template.md), present the plan with its
open decisions, and stop for approval. Record review changes as a revision with its
date, not by rewriting history.

---

## Examples

**Example 1 — a pricing workbook.** A price list tab, a tab of bundles with their
options, a tab of discount tiers, and a calculator tab that prices a sample order.
- **Inventory:** each tab's named ranges and formulas. The calculator's cached totals
  become golden values once the parity check recomputes them.
- **Mapping:** bundles → configurable bundles with component groups; options →
  attributes or components; tiers → volume and tier discounts.
- **Knowledge sources:** run the sweep for each area and decide from what it finds:
    - An area a skill documents with measurements is **Repo**.
    - An area only the Help or developer guide documents is **Snapshot**, and a skill
      gap.
    - An area where a skill records measured behaviour the docs don't show is
      **Live (b)**.
  Don't carry a decision over from another plan or release; sweep again.
- **Golden tests:** the calculator's lines and totals, and every tier boundary
  (derived from the tier table).

**Example 2 — a public web store.** Configurable products with option deltas, presets,
service plans and trade-in credits.
- **Mapping:** one configurable root per model plus a root per preset; options as
  attributes with attribute-based price; service plans as bundle components with
  their own selling models; option exclusions and dependencies as CML.
- **Source handling:** captured with a browser; an independent re-capture of a sample
  verifies it.
- **Golden tests:** every preset price and a sample of custom configurations, plus an
  allowed-and-disallowed option matrix checked through the configure API with rules on.

**Example 3 — routing.** "Add volume tiers to the existing price book" is not this skill:
use `pricing-setup` and `pricing-procedures`. "We have a costing spreadsheet; can Revenue
Cloud do this?" is this skill, starting with the intake questions.

## Validation Checks

Before presenting the plan:

- Every skill named in the plan exists:

  ```bash
  ls .cursor/skills/<name>/SKILL.md
  ```

- Every sub-file named exists under its skill.
- Every snapshot article cited exists under `docs/salesforce/<release>/`.
- Every golden value cites its place in the source, and the parity check passed.
- Every area has a knowledge-source row, and every live spike has a value it must hit.
- Every decision is marked decided (with a date) or recommended (with the alternative).
- Nothing in a public file names customer, brand or third-party commercial data.
- The plan's self-review checklist ([plan-template.md](plan-template.md)) passes.
