# Session Orchestration — Parallel Build Sessions

Read this when a plan splits the build across sessions. Parent:
[commercial-model-planning](SKILL.md).

## Layout

- **Main session.** Owns the plan, the design model, the golden tests, extraction,
  integration, lifecycle and billing work (P6), the pack and every gate.
- **Spike sessions.** Group the live spikes by area, for example pricing and
  lifecycle. Each session runs on its own kept org. Nothing from a spike goes into the
  model or the pack; its results go in `spikes/<area>/`, and the session reports each
  outcome to the main session, which records it in the verification ledger.
- **Build sessions.** One per independent area, for example catalog and configuration,
  pricing and cost, negotiation and approvals. Each runs on its own org and writes its
  data plans, models and overlays from the design model; extraction doesn't write them.
  A session whose area depends on another's loads that session's finished plans onto
  its own org first. When a spike's route choice touches its area, it follows
  [SKILL.md](SKILL.md) step 6 (Route prerequisites).
- **Integration org.** Build-phase gates (P3–P6) count only here. The main session
  loads each finished piece onto it and runs that piece's gate. P2 spike results are
  recorded from each spike session's own org, and the final gate is the fresh-org load
  (the template's P7), on a new org.

**A private pack's files live in the pack's repo,** not in the Foundations checkout.
Sessions own folders there. CCI still runs from the Foundations root, with explicit
paths into the pack, and the main session commits only in the pack's repo until
promotion.

Dependencies decide what runs in parallel. A typical chain:

```text
extraction → spikes → catalog → (configuration ∥ pricing) → negotiation → lifecycle → pack
```

## Rules

1. **One org per session,** built through the build harness and kept, with a lifetime
   that covers the session (`build-harness` → Keep an org for a multi-day build).
   Each session reports its org alias. No one deletes an org without the user's yes.
2. **No worktrees for CCI or harness work.** CCI finds the project root by a `.git`
   directory; in a git worktree `.git` is a file, so a run there uses another
   checkout's files (or none). Run from the main checkout or a regular clone. Sessions share that
   checkout, and each one owns specific folders; a session never writes outside them.
   Concurrent harness builds are fine, each with its own run id (`--run-id`), on a
   harness that gives each run its own Robot output folder (`main` since 2026-11-11);
   on an older one, two runs' Robot steps overwrite each other's output.
3. **Only the main session commits,** after reviewing a session's files at its gate.
   This stops two sessions racing on one git index.
4. **Every brief stands alone.** It names:
    - the phase and its gate,
    - the files the session owns,
    - its golden set,
    - the skills and articles to read first,
    - what done looks like.
   Write the brief in your own words; don't point at "the findings above".
5. **A platform defect stops the thread.** The session records it with a repro and
   tells the main session; it doesn't build a workaround into the model on its own.
6. **Sessions report skill gaps:** where a skill was missing, wrong or silent. These
   feed the plan's gap section.
7. **Check the org allowance first.** Count the integration org, the new org for the
   fresh-org gate (P7), and every parallel session against the dev hub's limits:

   ```bash
   sf org list limits -o <dev hub alias>
   ```

   Read `ActiveScratchOrgs` and `DailyScratchOrgs`. If the count doesn't fit, merge
   the spike sessions.
8. **Group spikes by the skill they read.** Spikes that read the same skill and touch
   the same objects share a session; keep each session to a handful of spikes, so one
   blocked spike doesn't hold up many.

## Plan table

| Session | Phase(s) | Org | Writes (owns) | Reads |
|---|---|---|---|---|
| main | P0, P1, P6–P8, P9 if chosen, integration | integration; a new org for P7 | plan, design, golden, tools, pack | everything |
| \<area\> spikes | \<spike ids\> | own | `spikes/<area>/` | design, golden |
| \<area\> build | \<phase\> | own (+ dependencies loaded) | its data plans, models, overlays | design, golden, dependencies' plans |
