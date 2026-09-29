# Revenue Cloud Base Foundations — Weekly Engineering Summary

**September 28, 2026 – September 29, 2026**

*Prepared for product leadership. Sources: merged pull requests #461 and #465 on main, two direct commits to main, back-sync pull requests #467 and #468 into the 264 branch, and active feature branches. The prior summary (September 21 – 28) is stored in the artifacts repository, not this one.*

## Executive Summary

This was a short reporting window, one day past the end of the last summary, and a quiet one for merges to main. Two small pull requests landed: a routine refresh of the agent tooling scorecard and an update to the Trialforce template identifiers used to provision demo orgs. Both were then carried into the 264 release branch through back-sync pull requests, keeping the two lines aligned.

The more consequential activity sits on unmerged branches. A multi-commit approvals effort moves quote-line approval flags from calculated formulas into stored fields that the pricing procedure writes on every reprice, and it hardens the tooling that applies those pricing changes so step labels are no longer lost. Separately, a fix to Dynamic Revenue Orchestrator (DRO) fulfillment provisioning is awaiting merge. None of this is shipped yet, and it is described below as in-flight.

## Week Detail

### Demo Environment Provisioning

**PR #465 — Trialforce template IDs refreshed for CDO, SDO and SDO-Lite** — The template identifiers that let the team spin up preconfigured demo orgs were updated for three org types, and the catalog documentation was synchronized with the new values after review. This is a small change with a direct operational effect: Sales Engineers provisioning from these templates get the current versions rather than stale ones. It merged to main and was back-synced to the 264 line through #468.

### AI Agent Operations and Developer Tooling

**PR #461 — Agent tooling artifacts refreshed** — The tooling scorecard and optimization report were regenerated, keeping the measure of how well the repository serves AI coding agents current. The change is small, two files, and was back-synced to the 264 branch through #467. Its value is continuity: the scorecard remains a trustworthy baseline for further agent tooling work.

**Direct commits to main** — Two commits by the same contributor accompanied #465: the template ID update and a documentation sync of the Trialforce README catalog in response to review feedback.

### Release Planning

**PR #467, #468 — 264 branch back-syncs** — Both changes above were merged into the 264 branch, so the release line and main carry the same tooling artifacts and template IDs. This keeps the Winter '27 line from drifting from main while both are active.

### In-Flight Work (not yet merged)

**Approvals: stored quote-line approval flags (branch feature/refactor-approval-flags)** — Approval level and label on each quote line move from formula fields to stored fields with the same names. A new pricing procedure overlay resets every line and then assigns Manager, Director or VP bands based on line discount (15% up to 25%, 25% up to 35%, 35% up to 100%), with a 100% discount left unflagged. The commit describes a new build step and additive context plan supporting this, and states it applies to fresh builds only, with no migration of existing formula fields. It reports validation on a disposable clone of the procedure in a live 264 org. Follow-on commits widen the label field to 255 characters and document that conditional-assignment overlays must reset every line first. For Product Management this makes approval thresholds visible and adjustable in pricing configuration; it is not on main.

**Expression set tooling: step labels preserved (same branch)** — A platform behavior was rebuilding every pricing procedure step label from its internal name whenever the build applied a change through the Connect API. The branch snapshots labels before the change and restores them afterward, adds a guard test against unprotected updates, and adds documentation for the three shipped overlays. This protects readable pricing procedure labels for anyone inspecting the procedure in an org. It is not merged.

**DRO fulfillment scope fix (branch fix/dro-fulfillment-scope)** — One commit corrects manual provisioning data for the QuantumBit DRO plan and replaces a group fulfillment scope that the commit describes as unsupported, with related task and test updates and an expanded plan README. It is not merged.

## Impact by User Group

### Distribution / Sales Engineering

Refreshed Trialforce template IDs for CDO, SDO and SDO-Lite mean new demo orgs start from current templates. The in-flight DRO fix, once merged, should make the fulfillment demo data provision correctly on fresh builds.

### Product Management

The in-flight approvals work would make discount-based approval tiers a visible, stored value on each quote line rather than a calculated display. That supports iterating on approval policy without engineering interpretation, but only after it merges.

## Cumulative Impact

The window is too short to show a trend on its own, but it confirms the pattern of keeping main and the 264 line in step through back-sync pull requests. The approvals and expression set work continues the pricing procedure investment, and the DRO fix continues the effort to make demo data dependable on fresh 264 builds. The prior summary's in-flight items could not be compared item by item because its contents were not readable from this repository; the next summary should confirm whether the approvals branch merges.
