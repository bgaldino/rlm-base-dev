# RCA/RCB Billing Gating Implementation Plan

## Objective

Enable reliable RCA-only builds while keeping a single feature model (no new `billing_advanced_capable` flag) by tightening use of the existing `billing` flag wherever Billing-only dependencies are currently included.

This plan documents:

- Decisions made
- Tradeoffs accepted
- Scope for future implementation
- Validation and rollout strategy

## Context and Evidence

This plan is based on:

- Flow/task gating analysis in `cumulusci.yml`
- Template and dataset scans for Billing-only objects
- Live org comparison between:
  - `rlm-base__rca_only_1`
  - `rlm-base__mar30_1`
- Detailed diff report:
  - `docs/analysis/rca-only-vs-mar30-object-metadata-diff.md`

Key finding: the RCA org has a partial billing data model, but many Billing Advanced objects/permissions are missing. Several build paths still include Billing dependencies when `billing=false`.

---

## Decisions Made

1. **Single-flag model**
   - Keep `billing` as the only Billing capability switch.
   - Do not introduce `billing_advanced_capable` or any new capability flag.

2. **Gate by concrete dependency**
   - If a task/metadata/dataset references Billing-only objects (from mar30-only list), it should be gated by `billing`.

3. **Fail-safe over maximal feature retention**
   - Initial implementation favors RCA stability and deterministic builds over enabling borderline paths.
   - Some feature paths (e.g., docgen/payments/rating) may be temporarily over-gated until sub-splitting is complete.

4. **Phased rollout**
   - Implement low-risk, high-impact gating first (core security + flow `when` clauses).
   - Defer structural refactors (shared vs billing-specific metadata extraction) to later phases.

---

## Current Gaps (What Is Not Correctly Gated)

### A) Core security group assignment

- `prepare_core` recalculates/assigns PSGs using `*rlm_psg_api_names` unconditionally.
- `*rlm_psg_api_names` includes `RLM_RCB`, which contains Billing Advanced perms.

Impact:

- RCA-only builds can fail due to missing Billing Advanced permsets/PSLs.

### B) Rating/rates pipeline

- `prepare_rating` is gated by `rating/rates/qb/q3`, but not `billing`.
- Dataset references include `UsageResourceBillingPolicy` and billing-linked dependencies.

Impact:

- RCA runs with `rating=true` can fail or behave inconsistently.

### C) Payments pipeline

- `prepare_payments` is gated by `payments`, not `billing`.
- Deploys invoice/payment artifacts that assume Billing domain availability.

Impact:

- RCA can fail or partially configure unsupported functionality.

### D) Docgen pipeline

- `prepare_docgen` is gated by `docgen`, not `billing`.
- Includes invoice-related templates/transforms tied to Billing objects.

Impact:

- RCA can fail or ship partially broken invoice document generation.

### E) Unconditional shared deploy path

- `deploy_full` runs unconditionally.
- `force-app/main/default` contains Billing-linked metadata (flows/context definitions).

Impact:

- `billing=false` does not fully protect RCA builds.

### F) UX assembly contamination

- Base/QB/payments template sources can include Billing references even when `billing=false`.

Impact:

- Deploy/runtime issues when Billing-only fields/objects are missing.

---

## Implementation Scope (Future Work)

## Phase 1 - Immediate Gating Fixes (low risk, high value)

1. **Split PSG assignment lists**
   - In `cumulusci.yml`:
     - `rlm_psg_api_names_shared` (exclude `RLM_RCB`)
     - `rlm_psg_api_names_billing` (`RLM_RCB`)
   - In `prepare_core`:
     - always recalc/assign shared list
     - recalc/assign billing list only when `billing=true`

2. **Add `billing` guard to `prepare_rating` steps**
   - Steps 1-8 in `prepare_rating` require `billing=true`.

3. **Add `billing` guard to `prepare_payments` steps**
   - All `prepare_payments` steps require both `payments=true` and `billing=true`.

4. **Add `billing` guard to `prepare_docgen` steps (initially conservative)**
   - All `prepare_docgen` steps require both `docgen=true` and `billing=true`.
   - Later refinement can re-enable non-billing quote-only docgen paths.

## Phase 2 - Shared vs Billing Metadata Separation

5. **Reduce `deploy_full` Billing leakage**
   - Move known Billing-only metadata out of unconditional deploy path and into billing-gated deploys.
   - Prioritize:
     - `RLM_Order_to_Billing_Schedule_Flow.flow-meta.xml`
     - Billing-only context definition segments (where practical)

6. **UX source hygiene**
   - Keep base templates RCA-safe.
   - Move Billing references into billing overlays/patches.
   - Ensure `ux=true` with `billing=false` does not pull Billing-only components.

## Phase 3 - Precision Un-gating (optional optimization)

7. **Refine over-gating from Phase 1**
   - Split docgen into quote-safe vs invoice-billing paths.
   - Split payments into shared-safe vs billing-advanced paths.
   - Split rating into billing-independent core vs billing-dependent overlays if justified.

---

## Tradeoffs

## Accepted Tradeoffs

- **Short-term over-gating**
  - Gating all of `prepare_docgen` and `prepare_payments` by `billing` may disable some capabilities that could technically work in RCA.
  - Accepted for initial reliability.

- **Incremental refactor instead of big-bang**
  - Keeps risk manageable and rollback simpler.

- **Single-flag simplicity over expressiveness**
  - Using only `billing` avoids configuration sprawl and confusion.
  - Cost: less granular control for hybrid capability scenarios.

## Rejected Tradeoffs

- **New capability flag**
  - Rejected by decision: no `billing_advanced_capable` style flag.

- **Leave core PSG list unchanged**
  - Rejected due to demonstrated RCA failure risk.

---

## Validation Strategy

## Build Matrix

Run these scenarios after each phase:

1. RCA baseline:
   - `billing=false`
   - expected: no Billing Advanced assignment/deploy failures

2. RCB baseline:
   - `billing=true`
   - expected: existing behavior preserved

3. Targeted feature toggles:
   - `rating=true`
   - `payments=true`
   - `docgen=true`
   - verify gating semantics and error absence/presence is intentional

## Verification Checks

- No attempts to assign `RLM_RCB` when `billing=false`
- No billing data plan tasks triggered when `billing=false`
- No billing-linked metadata deploy attempts in RCA-only path
- RCB path still deploys billing metadata and data as before

---

## Risks and Mitigations

- **Risk:** RCB regressions from gating edits
  - Mitigation: always run RCB control build after each change set.

- **Risk:** Hidden Billing references remain in shared metadata
  - Mitigation: use mar30-only object list as a recurring scan set in CI checks.

- **Risk:** UX assembly still pulls indirect Billing refs
  - Mitigation: add template-level scan step before deployment in Phase 2.

---

## Proposed Deliverables

1. `cumulusci.yml` gating changes (Phase 1)
2. Updated build guide notes for billing semantics
3. Metadata split PR for `deploy_full` and UX hygiene (Phase 2)
4. Optional precision refinements (Phase 3)

---

## Exit Criteria

Implementation is complete when:

- RCA-only build succeeds with `billing=false` without manual bypasses.
- RCB build succeeds with `billing=true` with no functional regression.
- All known Billing-only object dependencies are either:
  - gated by `billing`, or
  - moved to billing-only deploy paths.

