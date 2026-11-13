# Plan Template — Sections, Contents, Self-Review

Read this when writing or revising a plan with [implementation-planning](SKILL.md).
The sections appear in this order. A section that doesn't apply says so in one line
rather than disappearing, so a reviewer can tell it was considered.

## Header

- Title: `<Source name> on Revenue Cloud — Build Plan`.
- Owner, drafted date, revision dates with what changed, and status (draft for
  review, approved, building, done).
- **Source identity:** file and revision with a checksum, or capture dates.
- **Base:** the org shape and build path (for example a QuantumBit build through the
  build harness), and the release and API version.
- **Tracker item,** when the work is tracked.
- **What the build optimizes for:** the user's stated priorities, quoted or closely
  paraphrased.
- **Blind plan,** when the build measures the planner: where the unedited blind plan is
  kept ([SKILL.md](SKILL.md) → Review).
- **Plan as approved,** once approved: the frozen copy (`plan-as-approved.md`) the
  ledger measures; this file is then revised to as-built ([SKILL.md](SKILL.md) step 9).

## 1. Goal and definition of done

One bullet per capability area, each phrased as something checkable. End with:
- the proof (golden tests on a fresh-org load),
- the record (rule decisions and knowledge sources),
- how it repeats (pack, flag or flow).

## 2. Decisions

Only decision tables start with a `#` column (the ledger reads every one here). Number
intake answers first, in the intake's order, so `ledger.py init --intake` takes one range.
Decisions a person settles after the blind plan keep their IDs and go to `--owner` as a
list (`D7,D9`).

| # | Decision | Recommendation |
|---|---|---|
| Dn | **DECIDED yyyy-mm-dd: \<answer\>.** \<the question\> | \<what it means for the build\> |
| Dn | \<open question, with the facts that make it a question\> | \<recommendation\>, and the alternative |

Include every inconsistency found in the source, with numbers showing what each choice
changes (which totals move, by how much, and whether any threshold or approval outcome
changes). Note who has to answer it: the source's owner or the build's owner.

## 3. Architecture: source mapped to Revenue Cloud

- **3.0 Source inventory and rule register,** first: the inventory's counts (tabs,
  named ranges, formulas, validations; or products and pages) and one row per rule
  with its ID, its place in the source, and its area. Every later section refers to
  these IDs.
- **Approach,** stated once. Native first, with a recorded fallback per rule, unless
  the user chose otherwise.
- **One subsection per area:**
    - catalog
    - configuration and rules
    - pricing
    - cost and margin
    - negotiation and approvals
    - lifecycle changes
    - billing
    - runtime surface
    - extraction
- Each subsection keeps the source's own numbers and its order of application.
- **Configuration and rules** gives every rule that rejects or warns its message, for
  the rules golden set: the source's wording, or the plan's own, marked as such.
- **Extraction** says what the converter (the script that reads the source) writes,
  and how it is accepted:
    - It writes the **design model and the golden values**, nothing else. The build
      sessions (laid out in section 6) write data plans, constraint models and procedure
      rows from the design model, so each file has one owner.
    - **Acceptance** (the P1 gate), as tests the converter ships with: it refuses a
      source whose checksum isn't the pinned one; formula parity has 0 mismatches; every
      cached value equals its recomputation; every value the plan states (an anchor in
      a decision, a spike or a golden) equals the computed one. A prior build ran these,
      with a changed source refused; it didn't also feed each comparison a wrong value
      to prove it can fail, which is recommended so none passes vacuously.
      A source without formulas (a store capture, a document) keeps the checks that
      apply to it.
- **Rule decision record,** under a heading containing that name: one row per rule ID,
  with columns rule | decided by | native feature and fallback | exact vs source?, all
  set at planning time. A rule may carry two "decided by" values (new sale vs
  amendment). Build results go to the ledger; in `plan.md` an as-built revision of a
  row cites its ledger ID, and `plan-as-approved.md` keeps the row as predicted.
- **Knowledge source per area:** the table from
  [knowledge-sources.md](knowledge-sources.md), with the decision rule stated above it.

## 4. Golden tests

| Set | Source location | Cases | Must match |
|---|---|---|---|

A case an open decision affects carries the recommended value, tagged with the decision
ID, and the alternative's value beside it (SKILL.md step 5).

Always include a **Reprice** set (price again, then order, amend and renew) and an
**Attributes** set (attributes unchanged through each step; on a bundle sized by
configuration answers, the unchanged answers through two answer changes in a row). Include each attribute's
minimum and maximum, every option the source allows that its worked examples don't
use, and a check for anything the source marks internal-only (for example a round
that must never be presented). Billing cases cover every order the plan creates (the
new sale, each amendment, cancellation and renewal), not only the first. The measured
invoice routes invoiced through today, sending only schedules due by then (`rlm-business-apis` →
`backdated-asset-lifecycle.md`, Billing); invoicing to a future date isn't covered. So on a
future-dated replay, check billing at schedule level, and say which invoice values wait
for the replay-dates decision ([SKILL.md](SKILL.md), dated replay). For a
milestone-billed service, state what a quantity an amendment adds is billed by, and
record milestone billing of a service an amendment adds as an open decision (`billing-setup`).

## 5. Phases, gates, skills

Dependencies on one line, for example `P1 → P2 → P3a → (P3b ∥ P4) → P5 → P6 → P7 → P8 → P9`.
Each phase opens with an unbulleted bold label naming it (P2's reads
**P2 Live spikes**; the ledger finds the spike table by it), then bullets:
- the work items,
- **Skills:** the skills and sub-files to read first,
- the **Gate:** what must pass, and on which org.

The usual phases:

| Phase | Typical content |
|---|---|
| P0 Environment | Integration org through the build harness, on a named scenario or shape, with a lifetime that covers the build (shipped scenarios use `days: 1`; see `build-harness` → Keep an org for a multi-day build); feature and enablement checks; tooling. A checklist of the org settings the plan relies on. Some have no known API (a 264 build found them in no settings metadata or sObject or Tooling describe): the Salesforce Pricing Setup default term counts (Evergreen, One Time) are read in Setup → Salesforce Pricing Setup → Proration Settings (a fresh 264 `ent-sb0` org showed Evergreen 1, One Time 0), or the plan adds a step that sets them |
| P1 Extraction | Source → design model and golden values; the converter's acceptance tests (section 3, Extraction); an independent re-check: a fresh agent, without the converter, recomputes a sample of golden values weighted to derived ones (exercised in a prior build); user reviews the design |
| P2 Live spikes | Only the rules the rule decision record marks **Live**, in a table with columns spike ID, rules, must hit, smallest case, read first. Usually two waves, exercised in a prior build, in one table with the wave in a column, or under sub-labels **P2a** and **P2b** that both sit inside the P2 section, before the P3 label (the ledger reads no spike table after it): **P2a**, spikes a probe product can answer (pricing routes, surface), beside or before P3; **P2b**, spikes whose must-hits need the real catalog, model and prices (amend, cancel, renew), run on an org the loader fills after the pricing gate's standard-price goldens pass |
| P3 Catalog, then configuration | Data plans derived from the base build's own plans; CML; the route prerequisites of every P2a spike that touches them; the first loader (SKILL.md step 7) |
| P4 Pricing and cost | Price books, adjustments, procedure changes, cost wiring. The gate prices only after the decision tables it reads are fresh (`decision-tables` Quick Rule 1) |
| P5 Negotiation, approvals, runtime surface | Quote rounds, approvals, Transaction Line Editor configuration |
| P6 Lifecycle and billing | Order, activate, amend, swap, cancel, renew; billing frequency, treatments and payment terms on the order |
| P7 Pack and fresh-org load | Every gate in one run on a new org, with the loader extended since P3; reload changes nothing |
| P8 Walkthrough and sign-off | Independent verifier, then the user |
| P9 Promotion | Public repo through a pull request, if chosen; its own approval |

## 6. Session orchestration

The table and rules from [session-orchestration.md](session-orchestration.md).

## 7. Evidence log

| Date | Phase | Check | Result | Notes |
|---|---|---|---|---|

Start it with the source read, and the coverage sweep with its counts. What the build
finds goes here and in the verification ledger ([SKILL.md](SKILL.md) step 9). The
sections above are revised to as-built, each change citing its ledger ID, while
`plan-as-approved.md` keeps what was planned.

## 8. Risks

Include known platform behaviours that touch this build, with their workaround and
the condition for revisiting them.

## 9. Skills used, by phase

A matrix with skills as rows and phases as columns: ● used, ○ only if needed.

## 10. Gaps worth turning into skills

| Proposed skill | Gap today | Content from this build | After phase |
|---|---|---|---|

Then list **extensions to existing skills** separately.

## Self-review checklist

- [ ] No placeholder text, "TBD" or empty required section.
- [ ] Every number traces to the source, and calculated ones passed formula parity.
- [ ] Every worked example was run through every rule (cross-rule parity), and each
  violation is a decision.
- [ ] Lifecycle examples run in date order with rules on, or the order is a decision.
- [ ] Each register row states one testable behaviour; a row that holds two is split
  before mapping, so neither drops out.
- [ ] Rule IDs and counts agree across the register, the decision record and the
  golden tests.
- [ ] Every rule in the source appears in the mapping, or is listed as out of scope by
  decision.
- [ ] Every area has a knowledge-source row; every live spike has a must-hit value
  and the skills and articles to read first.
- [ ] Every skill, sub-file and snapshot article named exists.
- [ ] Every script the plan cites lives in the pack or the repo, not in a scratch or
  temporary folder.
- [ ] Every rule that rejects or warns has its message in the plan.
- [ ] Goldens on platform-enforced behaviour assert where the platform enforces it.
- [ ] Every spike that chooses a route lists each route's prerequisites
  ([SKILL.md](SKILL.md) step 6), and the dependency line shows the phase that waits for it.
- [ ] Every spike's must-hit is the source's value (through a stated mapping where the
  platform measures differently, or a decision), with the fallback if native misses it; none lists guessed
  platform outcomes ([prediction-checks.md](prediction-checks.md)
  check 3).
- [ ] Every structure was run against every lifecycle change in the source, and every
  recommendation names its mechanism (prediction-checks.md checks 5 and 6).
- [ ] Every native guard names where it is enforced and on which paths
  (prediction-checks.md check 7).
- [ ] Every golden an open decision affects carries both values and the decision ID.
- [ ] The extraction section gives the converter only the design model and goldens,
  and lists its acceptance tests.
- [ ] Decisions don't contradict each other or the mapping.
- [ ] Gates name the org they run on.
- [ ] Public and private boundaries match the hosting decision.
