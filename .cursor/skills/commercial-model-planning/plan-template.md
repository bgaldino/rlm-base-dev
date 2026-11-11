# Plan Template — Sections, Contents, Self-Review

Read this when writing or revising a plan with [commercial-model-planning](SKILL.md).
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

## 1. Goal and definition of done

One bullet per capability area, each phrased as something checkable. End with:
- the proof (golden tests on a fresh-org load),
- the record (rule decisions and knowledge sources),
- how it repeats (pack, flag or flow).

## 2. Decisions

| # | Decision | Recommendation |
|---|---|---|
| Dn | **DECIDED yyyy-mm-dd: \<answer\>.** \<the question\> | \<what it means for the build\> |
| Dn | \<open question, with the facts that make it a question\> | \<recommendation\>, and the alternative |

Include every inconsistency found in the source, with numbers showing what each choice
changes (which totals move, by how much, and whether any threshold or approval outcome
changes). Note who has to answer it: the source's owner or the build's owner.

## 3. Architecture: source mapped to Revenue Cloud

- **Approach,** stated once. Native first, with a recorded fallback per rule, unless
  the user chose otherwise.
- **One subsection per area:**
    - catalog
    - configuration and rules
    - pricing
    - cost and margin
    - negotiation and approvals
    - lifecycle changes
    - extraction
- Each subsection keeps the source's own numbers and its order of application.
- **Rule decision record:** a table filled in as spikes and gates finish, with columns
  rule | decided by | native feature | exact vs source? | path taken | evidence.
- **Knowledge source per area:** the table from
  [knowledge-sources.md](knowledge-sources.md), with the decision rule stated above it.

## 4. Golden tests

| Set | Source location | Cases | Must match |
|---|---|---|---|

Always include a **Reprice** set (price again, then order, then amend) and an
**Attributes** set (attributes unchanged through each step).

## 5. Phases, gates, skills

Dependencies on one line, for example `P1 → P2 → P3a → (P3b ∥ P4) → P5 → P6 → P7 → P8 → P9`.
For each phase:
- the work items,
- **Skills:** the skills and sub-files to read first,
- the **Gate:** what must pass, and on which org.

The usual phases:

| Phase | Typical content |
|---|---|
| P0 Environment | Integration org through the build harness; feature and enablement checks; tooling |
| P1 Extraction | Source → design model and golden values; parity; independent re-check of a sample; user reviews the design |
| P2 Live spikes | Only the rules the knowledge-source table sends to a live org |
| P3 Catalog, then configuration | Data plans derived from the base build's own plans; CML |
| P4 Pricing and cost | Price books, adjustments, procedure changes, cost wiring |
| P5 Negotiation, approvals, runtime surface | Quote rounds, approvals, Transaction Line Editor configuration |
| P6 Lifecycle | Order, activate, amend, swap, cancel, renew |
| P7 Pack and fresh-org load | Every gate in one run on a new org; reload changes nothing |
| P8 Walkthrough and sign-off | Independent verifier, then the user |
| P9 Promotion | Public repo through a pull request, if chosen; its own approval |

## 6. Session orchestration

The table and rules from [session-orchestration.md](session-orchestration.md).

## 7. Evidence log

| Date | Phase | Check | Result | Notes |
|---|---|---|---|---|

Start it with the source read, and the coverage sweep with its counts.

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
- [ ] Every number traces to the source, and calculated ones passed parity.
- [ ] Every rule in the source appears in the mapping, or is listed as out of scope by
  decision.
- [ ] Every area has a knowledge-source row; every live spike has a must-hit value
  and the skills and articles to read first.
- [ ] Every skill, sub-file and snapshot article named exists.
- [ ] Decisions don't contradict each other or the mapping.
- [ ] Gates name the org they run on.
- [ ] Public and private boundaries match the hosting decision.
