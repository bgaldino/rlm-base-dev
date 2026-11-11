# Session Orchestration — Parallel Build Sessions

Read this when a plan splits the build across sessions. Parent:
[commercial-model-planning](SKILL.md).

## Layout

- **Main session.** Owns the plan, the design model, the golden tests, extraction,
  integration, lifecycle work, the pack and every gate.
- **Spike sessions.** Group the live spikes by area, for example pricing and
  lifecycle. Each session runs on its own org and keeps nothing.
- **Build sessions.** One per independent area, for example catalog and configuration,
  pricing and cost, negotiation and approvals. Each runs on its own org. A session
  whose area depends on another's loads that session's finished plans onto its own
  org first.
- **Integration org.** Gates count only here. The main session loads each finished
  piece onto it and runs that piece's gate.

Dependencies decide what runs in parallel. A typical chain:

```text
extraction → spikes → catalog → (configuration ∥ pricing) → negotiation → lifecycle → pack
```

## Rules

1. **One org per session,** built through the build harness and kept (`build-harness`).
   Each session reports its org alias. No one deletes an org without the user's yes.
2. **No worktrees for CCI work.** Sessions share the checkout, and each one owns
   specific folders. A session never writes outside them.
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
7. **Check the org allowance first.** Count the integration org plus every parallel
   session against the dev hub's limits:

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
| main | P0, P1, P6–P8, integration | integration | plan, design, golden, tools, pack | everything |
| \<area\> spikes | \<spike ids\> | own | `spikes/<area>/` | design, golden |
| \<area\> build | \<phase\> | own (+ dependencies loaded) | its data plans, models, overlays | design, dependencies' plans |
