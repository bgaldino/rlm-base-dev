# Delta Term Builder — Negotiation-Modeling Demo (parked)

Status: **built, tested, and deployed once to the Delta demo org, then removed from
the UI.** The five demo LWC bundles remain in the repo as saved artifacts; the Term
Builder orchestrator (`dlTermBuilder`) has been reverted to its pre-demo baseline so
the shipped app shows no demo surfaces. This document is the recipe for wiring the
demo back in when it's wanted again.

## What this demo adds

Three analyst-facing surfaces layered onto the existing Delta "Term Builder" app,
covering the *modeling* stage of Delta's Requirements-for-Contracting workflow:

1. **Live KPI band** — contract-wide rollup under the header + a slim per-Term band
   in the workspace (Revenue, Flights, Share, FMS, Share Gap, EDR). Animates the
   Share / Share Gap / EDR headline tiles as discounts are modeled.
2. **Multi-round modeling grid** — a client-only negotiation spreadsheet on a new
   "Modeling" tab (Product vs Fare-Class row builders, four explicit rounds, inline
   spend/discount editing, sticky Value/Carrier columns + a sticky totals/EDR row).
3. **On-screen Proposal Summary** — a `LightningModal` opened from the header with a
   contract rollup + per-Term table marking the recommended Final Offer.

Plus a simulated **"Simulated Data" context strip** and an **Apply Final Offer to
Quote** action that writes modeled Product-mode discounts back to the Quote fare
lines (via the existing `RLM_DeltaLineController.updateLineDiscountAndDates`) so the
existing **Create Contract** button converts them truthfully.

### Scope / guarantees

- **All numbers are mock, computed client-side, and deterministic** (FNV-1a hash →
  LCG rng, keyed on term id + route). No `Math.random`, no timestamps — a reload
  reproduces identical baselines; only in-session edits are lost.
- **No new Apex, no schema, no data plans.** The only server call is the reused
  `updateLineDiscountAndDates`. Everything else reads the existing
  `RLM_DeltaTermBuilderController.getBuilderState(quoteId)` payload.
- All demo model state is in-memory and labelled "Demo model — session only".

## The saved artifacts (kept in the repo)

Five LWC bundles under `unpackaged/post_term_builder/lwc/`, none of which are
referenced by any shipped component after the revert, so they are inert until
re-wired:

| Bundle | Type | Role |
|---|---|---|
| `dlDemoModel` | plain ES module (no template) | Pure deterministic seed / spend-normalization / EDR / KPI / aggregation engine + formatters. Imported by the other three. |
| `dlDataContext` | presentational | The read-only "Simulated Data" strip. |
| `dlKpiBand` | presentational | KPI tiles + Share-Gap animation. `variant="contract"` \| `"term"`. |
| `dlModelingGrid` | stateful, client-only | The negotiation spreadsheet. Emits `modelchange` / `methodchange` / `expandtoggle`. |
| `dlProposalSummary` | `LightningModal` | On-screen all-terms rollup. |

Jest suites live in `dlDemoModel/__tests__` (31), `dlKpiBand/__tests__` (6), and
`dlModelingGrid/__tests__` (8) — **45 demo-specific tests, all green** as of the last
run (`npm test` / `npx sfdx-lwc-jest`). These keep running in CI regardless of
whether the demo is wired into the UI, so the engine stays verified while parked.

> Note: `dlDataContext` and `dlProposalSummary` have no `__tests__` of their own —
> they are presentational and were validated by the manual walkthrough. The three
> tested bundles cover the logic (engine + grid + band).

## The removed wiring

The only files that changed to *host* the demo were the three orchestrator files:

- `unpackaged/post_term_builder/lwc/dlTermBuilder/dlTermBuilder.js`
- `unpackaged/post_term_builder/lwc/dlTermBuilder/dlTermBuilder.html`
- `unpackaged/post_term_builder/lwc/dlTermBuilder/dlTermBuilder.css`

Their exact demo diff — the difference between the baseline orchestrator and the
fully-wired demo — is saved as a patch next to this doc:

```
docs/features/delta-negotiation-modeling-demo.patch
```

The patch was captured against orchestrator baseline commit **`aae52786`** and
verified to re-apply cleanly onto that baseline.

## How to add it back — the fast path (recommended)

From the repo root, with the orchestrator at its committed baseline (i.e. no local
edits to the three `dlTermBuilder` files):

```bash
git apply docs/features/delta-negotiation-modeling-demo.patch
```

Then verify and deploy:

```bash
# lint + tests
npx eslint "unpackaged/post_term_builder/lwc/**/*.js"
npx sfdx-lwc-jest -- --testPathPattern 'post_term_builder'

# deploy the orchestrator + the five demo bundles (+ emblem already on org)
sf project deploy start --target-org <alias> \
  -d unpackaged/post_term_builder/lwc/dlDemoModel \
  -d unpackaged/post_term_builder/lwc/dlDataContext \
  -d unpackaged/post_term_builder/lwc/dlKpiBand \
  -d unpackaged/post_term_builder/lwc/dlModelingGrid \
  -d unpackaged/post_term_builder/lwc/dlProposalSummary \
  -d unpackaged/post_term_builder/lwc/dlTermBuilder
```

If `git apply` fails because the orchestrator has drifted since `aae52786`, fall
back to a 3-way merge, which resolves against the current tree:

```bash
git apply --3way docs/features/delta-negotiation-modeling-demo.patch
```

If that still conflicts, use the manual checklist below to re-create the wiring by
hand — the patch remains the source of truth for exact code.

## How to add it back — the manual checklist

If the patch can't apply (the orchestrator was substantially refactored), reproduce
these edits. This is the complete inventory of what the demo wiring adds.

### `dlTermBuilder.js`

**Imports** (top of file):
```js
import DlProposalSummary from "c/dlProposalSummary";
import updateLineDiscountAndDates from "@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates";
import {
  METHOD_PRODUCT,
  seedModel,
  computeTermKpis,
  aggregateKpis,
  finalOfferLineDiscounts,
  routeLabel,
  methodLabel
} from "c/dlDemoModel";
```

**Instance state** (new class fields):
```js
currencyCode = "USD";       // retained from getBuilderState so bands/proposal format money
activeTab = "fares";        // "fares" | "modeling"
_modelsByTermId = {};       // keyed `${termId}::${method}`; seeded lazily, cleared on quote switch
selectedMethod = METHOD_PRODUCT;
@track activeModel = null;   // reactive mirror of the selected Term+method model, handed to the grid
workspaceExpanded = false;   // collapses the Terms rail to give the grid room
applyingOffer = false;
```

**Calls injected into existing methods:**
- `handleAccountChange()` → add `this._resetDemoModels();`
- `openQuote(quoteId)` → if `quoteId !== this.quoteId`, call `this._resetDemoModels();`
- `refreshState()` → retain `this.currencyCode = quote.currencyCode || this.currencyCode || "USD";`,
  call `this._pruneDemoModels();`, and call `this._syncActiveModel();`
- `handleTermSelect()` and `handleTermAdded()` → call `this._syncActiveModel();`
- `handleFareAdded()` → call `this._reseedModelsForTerm(this.selectedTermId);` (a new backing
  fare invalidates the seeded model for that Term)

**New getters:** `_termKpiList`, `contractKpis`, `selectedTermKpis`, `hasContractKpis`,
`isModelingTab`, `showTermsRail`, `railColumnClass`, `workspaceColumnClass`,
`proposalDisabled`, `applyOfferDisabled`.

**New handlers:** `handleTabActive`, `handleModelChange`, `handleMethodChange`,
`handleExpandToggle`, `handleOpenProposal` (projects each Term at its model's
`finalOfferRoundIndex`), `handleApplyFinalOffer` (calls `updateLineDiscountAndDates`
with `finalOfferLineDiscounts(this.activeModel)`, then `refreshState`), `handleResetModel`.

**New helpers:** `_modelKey`, `_modelFor` (lazy seed), `_syncActiveModel`,
`_reseedModelsForTerm`, `_pruneDemoModels`, `_resetDemoModels`.

### `dlTermBuilder.html`

1. **Header action** — a `Proposal Summary` `lightning-button` (`disabled={proposalDisabled}`,
   `onclick={handleOpenProposal}`) beside the existing Create Contract / View Contract buttons.
2. **Context + contract band** — after the header, inside `<template if:true={hasQuote}>`:
   `<c-dl-data-context>` followed by `<c-dl-kpi-band variant="contract" heading="Contract KPIs"
   kpis={contractKpis} currency-code={currencyCode}>` (guarded by `hasContractKpis`).
3. **Rail column** — change the Terms rail `<div>` to `class={railColumnClass}` (collapses when
   Modeling is expanded).
4. **Workspace column** — change to `class={workspaceColumnClass}`; inside the workspace card add:
   - a card `actions` slot with the "Demo model — session only" `<span class="dl-tb-session-label">`
     + a reset `lightning-button-icon` (`onclick={handleResetModel}`);
   - a slim `<c-dl-kpi-band variant="term" kpis={selectedTermKpis} currency-code={currencyCode}>`;
   - a `<lightning-tabset variant="scoped" active-tab-value={activeTab}>` with:
     - **Fares** tab (`value="fares"`, `onactive={handleTabActive}`) hosting the existing
       `c-dl-quote-line-grid` + `c-dl-add-fare-class` (unchanged content, just moved into the tab);
     - **Modeling** tab (`value="modeling"`, `onactive={handleTabActive}`) hosting an
       `Apply Final Offer to Quote` `lightning-button` (`disabled={applyOfferDisabled}`,
       `onclick={handleApplyFinalOffer}`) + `<c-dl-modeling-grid term={selectedTerm}
       model={activeModel} currency-code={currencyCode} expanded={workspaceExpanded}
       onmodelchange={handleModelChange} onmethodchange={handleMethodChange}
       onexpandtoggle={handleExpandToggle}>`.

### `dlTermBuilder.css`

- Centralized Delta brand tokens on `:host` as CSS custom properties (`--dl-navy`,
  `--dl-red`, `--dl-tint`, `--dl-hairline`, `--dl-muted`, `--dl-positive`,
  `--dl-page-bg`) with SLDS-style literal fallbacks.
- New classes: `.dl-tb-context` (spacing for the context/band block),
  `.dl-tb-header__action` (light button on the navy band), `.dl-tb-session-label`
  (the italic uppercase "session only" disclosure).

## Gotchas when re-integrating

- **Meta description length ≤ 255.** `LightningComponentBundle` `<description>` in
  each `*.js-meta.xml` has a hard 255-char limit; the demo bundles are already
  trimmed to fit. If you re-expand any description, deploy will fail with
  *"Value too long for field: Description maximum length is: 255"*.
- **Deploy is all-or-nothing.** If the orchestrator references `c-dl-modeling-grid`
  et al. but you only deploy `dlTermBuilder`, the deploy fails with *"No MODULE named
  markup://c:dlModelingGrid found"*. Always deploy the five bundles **with** the
  orchestrator (see the fast-path command).
- **Permission-set FLS is already in place.** `RLM_TermBuilderPermset` already grants
  editable FLS on `QuoteLineItem.DL_FareCodes__c`, `Discount`, `StartDate`, `EndDate`
  — the fields the Apply-Final-Offer write-back touches. No permset change needed.
- **`prefers-reduced-motion`.** The KPI band snaps animations off under reduced-motion
  and in jsdom; verify the animated headline moment in a real browser during rehearsal.

## Provenance

- Orchestrator baseline for the patch: commit `aae52786`
  (*"feat(term-builder): negotiation default dates + Term Annual selling model default"*).
- The demo was deployed once to the Delta demo org (`scheck@deltarevcloud.demo`),
  deploy id `0Afaj00000dqQkjCAE` — then removed from the UI per request. If the org
  still carries the demo bundles from that deploy, they are harmless while the
  deployed orchestrator no longer references them; redeploy the reverted orchestrator
  to fully restore the pre-demo UI (see below).

---

# Round 2 — modularized host + data-provider seam

Round 2 lights the workbench back up, but on the **modularized** Term Builder variant
(`unpackaged/post_modularized_term_builder/`) instead of the monolith `dlTermBuilder`.
The five `dl*` bundles above are **reused verbatim in place** at
`unpackaged/post_term_builder/lwc/` — they are *not* copied into the modularized dir
(that would create duplicate `c/*` components and a deploy conflict). A new
always-mounted `dlmWorkspaceShell` hosts a `lightning-tabset` (Shell Creation /
Modeling / Performance) and owns the per-Term model cache + the always-visible
contract KPI band; `dlmModelingWorkspace` is a controlled wrapper around
`c-dl-modeling-grid` (props down, events up), mirroring the monolith orchestrator/grid
contract documented above.

## Engine changes in Round 2 (`dlDemoModel`)

These are **additive and backward-compatible** — the parked Jest suites stay green
(now 84 across the two variants):

1. **KPI rename Flights → Passengers.** `seedTermFlown`, `computeTermKpis`, and
   `aggregateKpis` now emit `industryPassengers` / `hostPassengers` (was
   `industryFlights` / `hostFlights`); `dlKpiBand` renders "Industry Passengers" /
   "Host Passengers" tiles (keys `ind-pax` / `host-pax`). **FMS stays flight-capacity
   based** — it is still `hostPassengers ÷ industryPassengers` (the capacity metric),
   only the field/label wording changed.
2. **Read-only prior-discount column.** Each `buildRows` row now carries
   `priorDiscountPct` — the fare's prior-cycle discount, sourced by enriching
   `term.fares[*].priorDiscount` (from `RLM_DeltaLineController.getQuoteLines`, keyed
   by line id) **before** seeding. It is display-only and never affects any KPI;
   `null` when the fare wasn't enriched (today's `getBuilderState` fares don't carry
   it, so no Apex change is required).

## Data-provider seam (the `term.modeling` contract)

`dlDemoModel` accepts an **optional** `modeling` blob so a future server-side data
stream can pin real magnitudes without touching the engine's callers. When absent
(today), the deterministic seed is used verbatim and behavior is byte-identical.

- `seedTermFlown(term, modeling = term.modeling)` — reads `modeling.flown`, a partial
  object whose **finite numeric** keys override the seeded baseline. Recognized keys:
  `industryRevenue`, `hostRevenue`, `industryPassengers`, `hostPassengers`,
  `negotiatedSpendUSD`, `baseSharePts`, `fmsPts`, `gapPts`, `beta`. Non-numeric or
  missing keys fall through to the seed. The provider should supply a *consistent*
  set (e.g. if it pins `baseSharePts` + `fmsPts`, also pin `gapPts`).
- `seedModel(term, method, modeling = term.modeling)` — honors a `modeling.rows`
  array (already in row shape) verbatim; otherwise seeds rows deterministically.
- `computeTermKpis(term, model, roundIndexOverride, modeling = term.modeling)` —
  threads `modeling` through to `seedTermFlown`.

`term.modeling` is `null`/absent in every current `getBuilderState` payload;
`getBuilderState` passes a `null` `term.modeling` through explicitly so the seam is
wired end-to-end and ready to populate. See `RLM_DeltaTermBuilderController` (the
`terms[]` builder) and the row builders in
`unpackaged/post_term_builder/lwc/dlDemoModel/dlDemoModel.js`.
