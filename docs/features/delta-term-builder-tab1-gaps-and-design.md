# Delta Term Builder — Tab 1 (Data Gathering + Contract Shell Creation): Gaps & Design

> Companion to [`delta-negotiation-modeling-demo.md`](delta-negotiation-modeling-demo.md).
> That doc covers **Tab 2** (discounting / modeling / negotiation). This one covers **Tab 1**
> (contract data gathering + contract shell creation) of the modularized 2-tab Term Builder
> (`dlmWorkspaceShell`), measured against the current data-gathering / contract-shell requirements.

## Why this doc exists

Tab 1 is the *start* of the analyst workflow: gather a set of flown data for an account, then construct
the contract shell (terms + geography) that the modeling tab prices against. We need a clear-eyed read of
where the already-built work meets the requirements, where it falls short, and how to improve the start of
the process before investing in implementation.

### The single most important finding

The entire analytics layer (`dlDemoModel`) is a **client-side, deterministic mock**. Concretely:

- There is **no real flown-data ingestion** (PRISM/ARC). Magnitudes are synthesized from an FNV-1a hash
  of term id + route, so a reload reproduces identical numbers.
- There is **no persisted row-level structure** for flown data organized by Market Pair × Fare Basis ×
  Carrier — the shape the requirements make the atomic unit of analysis.
- There is **no mapping of current-contract information** (current discount, discount name, term, goal,
  goal measure, compare fare) onto data rows.
- A single `Quote` (the "negotiation") **conflates three concepts** the requirements treat as distinct:
  the gathered **data set**, the **contract shell**, and the **modeling scenario**.

None of this is a defect in the existing work — it was built and documented as a deterministic demo. It is
simply the gap between a demo and the product the requirements describe.

### Scope decisions governing the recommendations below

- **Fidelity = Hybrid.** Design the real row-level data-set + term-stamping model now, but keep the
  mock/deterministic fill behind the existing `term.modeling` seam until real feeds land.
- **Entity model = keep single-Quote for now.** Do not introduce separate Data Set / Shell / Scenario
  objects yet. Requirement 8 (one data set → many shells → many scenarios) is **deferred** and recorded
  as a known limitation.
- **Target build = modularized** (`unpackaged/post_modularized_term_builder/`), reusing the parked `dl*`
  engine bundles under `unpackaged/post_term_builder/lwc/` verbatim.

---

## Part A — Gap analysis (requirements vs. current state)

Status legend: **Met** / **Partial** / **Gap**. Each row cites the file that owns the behavior today (or
would own it).

### A.1 Gathering Data

| Req | Status | Where it lives / would live | Note |
|---|---|---|---|
| 1.1 Select start/end of flown data to analyze | **Met** | `dlmDataSetConfig.js` → `Quote.DL_AnalysisPeriodStart__c` / `DL_AnalysisPeriodEnd__c` | Persisted; drives the analytics `periodFactor`. |
| 1.1 If range < 12 months, annualize to a 12-month equivalent | **Gap — inverted** | `dlmDataSetConfig.periodFactor` (`days/365`) consumed by `dlDemoModel.seedTermFlown` / `computeTermKpis` | Current factor **shrinks** short windows (6 mo → 0.5×). The requirement wants the opposite: **annualize up** (6 mo → 2×). |
| 1.2 Include "subsidiary" accounts of the primary | **Partial** | `dlmDataSetConfig` subsidiary picker (Account `ParentId` children) | Captured **client-only**, **not persisted**, and **not folded** into any aggregation. |
| 1.3 Partner selection → partner flown data as **host** revenue + aggregate partner **FMS** per market pair | **Partial** | `Quote.DL_ParticipatingCarriers__c` + `dlDemoModel` (`hostRevenue`, `fmsPts`) | Carriers captured & persisted; host + FMS numbers are **mock**, not aggregated from partner flown data. |
| 2. Map current-contract info per row: current discount, discount name, term name, goal, goal measure, compare fare | **Gap (mostly)** | `QuoteLineItem.DL_PriorDiscount__c` (renewal only); `discountName`/goal/measure exist as mock grid columns / term attributes | No mechanism attaches current-contract facts to gathered data rows. **`compareFare` is confirmed absent** (asserted absent in `dlDemoModel/__tests__`). |
| 3. Organize by **Market Pair × Fare Basis × Carrier** = a unique row | **Gap** | *(no owner today)* | There is **no flown-data row grid** at all. The data model is Term-bundle → fare-class line, not analytical rows. Geography roll-up (aggregate at any scope level) is the `DL_Geography__c` backbone — see **D.1**. |
| 3.1 With current-contract info present, extend row identity by current term / discount / discount name | **Gap** | *(no owner today)* | Depends on Gap 3. |

### A.2 Contract Shell Creation

| Req | Status | Where it lives / would live | Note |
|---|---|---|---|
| 1. Construct/import terms across geo scopes: airport, city grouping, country, entity/region, super-region, custom group | **Partial** | `dlDemoModel` `DL_ScopeType` + `SCOPE_TYPE_RANK` (Airport 5 → Super-region 1 → Custom 0); `RLM_DeltaTermBuilderController.addTerm` | Scope types and specificity rank exist; term construction works via PST bundle roots. Binding scope to real `DL_Geography__c` records + custom-group m2m — see **D.2**, **D.4**. |
| 1.2 Directional origin / bidirectional / includes-excludes / in-or-out-of a geography | **Partial** | `DL_Directionality` attribute; Includes/Excludes toggle in `dlmTermCard` | Includes/Excludes is **UI-only, transient, never persisted** to the Contract geography EAV. "In / out of a geography" is **not modeled**. Matching-semantics design — see **D.3**. |
| 2. Import from a library of pre-built templatized **terms** (with geography visible in the UI) | **Gap** | *(no owner today)* | No term-template library object or UI. Two candidate models (custom objects vs. catalog products) — see **D.5**. |
| 3. Import a full templatized **contract**, OR copy the full term set from an existing contract | **Partial** | Renewal path: flow `DL_InitiateRenewalFromContract` + `RLM_DeltaRenewalFinalizer.restoreClonedLineFidelity` | Copy-from-existing exists via renewal clone; there is **no template-contract library**. |
| 4. Admin user maintains these libraries | **Gap** | *(no owner today)* | No library, no admin-gated maintenance surface. |
| 5. Stamp/map every selected data row to the correct term | **Gap** | `dlDemoModel.resolveTermForMarket` (client-side, mock markets) | The resolver helper exists, but there are no real rows to stamp. Geography-containment matching (vs. today's token/exact-string match) — see **D.1**. |
| 5.1 Tie-breaker when a row fits multiple term geographies | **Partial** | `SCOPE_TYPE_RANK` most-specific-wins + stable original-index tiebreak | Logic present; runs only against mock market strings. Tie-break is unchanged by the geography upgrade — see **D.1**. |
| 5.2 Hierarchy easily changed in the UI | **Partial / Gap** | `dlmTermCard` rank badge | Rank is **displayed** but not editable or persisted. |
| 6. Change gathered-data parameters even after terms are selected/created | **Partial** | `configchange` → shell re-scales KPI bands | Works for the mock; a real build must recompute rows and **re-stamp** them to terms. |
| 7. High-level KPIs on the fly as terms are added: Industry & Host Revenue, Industry & Host Flights (Passengers), Share, FMS, Share gap | **Met (on mock)** | `dlKpiBand` + `dlDemoModel.computeTermKpis` / `aggregateKpis` | Present and animated. Needs a real-row source through the seam. |
| 8. One data set → many contract shells; one shell → many modeling scenarios | **Gap — deferred** | *(single-Quote conflation)* | **Deferred by decision.** A single Quote is data set + shell + scenario today. Recorded as a known limitation. |

---

## Part B — Recommended design for Tab 1 (hybrid, single-Quote)

**Unifying move:** make the row-level flown-data set a first-class, well-specified **data contract** that
flows through the *already-wired* `term.modeling` seam — mock-filled now, server-fillable later — without
introducing new persisted top-level objects. Seven pillars.

### B.1 Row-level flown-data contract — the core new abstraction

Define a canonical row shape and deliver it as the payload behind the existing seam. `dlDemoModel`
already honors it: `seedModel(term, method, modeling)` uses `modeling.rows` verbatim when present, and
`seedTermFlown(term, modeling)` uses `modeling.flown`. Today the shell supplies **no `modeling` field at
all** (`dlmWorkspaceShell` passes terms straight from `getBuilderState` with no `modeling` key), so the seam
functions fall back to their `term && term.modeling` default — which resolves to `undefined` and triggers
deterministic seeding. The seam is therefore wired end-to-end and inert: a real provider populates
`modeling` and the fill switches from synthesized to server-sourced with no engine change.

```
FlownRow = {
  marketPair,            // e.g. "ATL-LHR"
  fareBasis,             // fare basis code
  carrier,               // operating/ticketing carrier
  industryRevenue, hostRevenue,
  industryPassengers, hostPassengers,
  fms,                   // fair market share for the market pair
  // extended identity — present only when current-contract info is mapped in (B.2):
  currentTerm, currentDiscount, currentDiscountName
}
```

The **row uniqueness key** is `marketPair + fareBasis + carrier` (req 3), extended to
`+ currentTerm + currentDiscount + currentDiscountName` when current-contract info is present (req 3.1).
Mock fill continues to synthesize rows deterministically; a future server provider pins the same keys. **No
new persisted object is required** — rows live in the in-session data-set payload keyed to the Quote.

### B.2 Current-contract mapping onto rows

Extend `FlownRow` with the six current-contract facets (req 2): current discount, current **discount
name**, current term name, current goal, current goal measure, and current **compare fare** (the
fixed-dollar lane-fare comparator — the confirmed-missing field). For renewal shells, source them from the
clone path already in place (`restoreClonedLineFidelity`, `QuoteLineItem.DL_PriorDiscount__c`); mock-fill
otherwise. Introduce a `DL_CurrentCompareFare` facet for fixed-dollar lane fares.

### B.3 Data-set config fixes (`dlmDataSetConfig.js`)

- **Annualization (fixes the inverted `periodFactor`).** Replace `periodFactor = days/365` with an
  **annualization factor** that scales a `< 12-month` window *up* to a 12-month equivalent:
  `factor = 365 / days`. Worked examples the design must satisfy: **6-month window → ×2**, **12-month →
  ×1**. Decide the ≥12-month behavior: recommend **normalize-to-12** (a 24-month window → ×0.5) so every
  data set is a comparable 12-month picture; call this out explicitly since it differs from a naive
  "never shrink" clamp. Update the `seedTermFlown` / `computeTermKpis` callers, which already accept the
  factor as a parameter.
- **Subsidiaries.** Define how subsidiary accounts *aggregate* into the data set — their flown rows fold
  into the primary account's set under the same uniqueness key — and decide persistence (today the picker
  is client-only and dropped on reload).
- **Partners → host + FMS.** Specify the semantic the mock must honor and the server provider must
  implement: a selected partner's flown data counts as **host** revenue, and the partner's **FMS is
  aggregated per market pair**.

### B.4 Term geography model

Persist what is currently transient. The **Includes/Excludes operator** lives only in `dlmTermCard`
component state today and never reaches the Contract geography EAV; promote it (and **directionality**) to
real `DL_*` attributes so the shell round-trips them. Add an **"in / out of a geography"** facet
(e.g. market pairs in/out of ATL). Reuse `termScopeChips` / `scopeLabel` from `dlDemoModel` for UI
visibility of each term's geography definition (req 1, 2 visibility).

### B.5 Term & contract template libraries + admin maintenance

Design a library model (req 2, 3, 4):

- A tagged catalog of **reusable Term definitions** (geography scope + goal/measure) an analyst can import
  into a shell, with the geography rendered via `termScopeChips`.
- A catalog of **full term-set "contract templates"** an analyst can instantiate wholesale; copy-from-
  existing-contract reuses the renewal clone machinery already present.
- An **admin-gated maintenance surface** (permission-set controlled, following `RLM_TermBuilderPermset`
  conventions) for curating both libraries.

### B.6 Row → Term stamping engine + editable hierarchy

Promote `resolveTermForMarket` + `SCOPE_TYPE_RANK` from mock-market resolution to **stamping every
gathered `FlownRow` to its winning term** (req 5). The tie-breaker hierarchy (req 5.1) already uses
most-specific-scope-wins with a stable index tiebreak; make it **editable and persisted per shell** by
turning the `dlmTermCard` rank badge into a reorderable control that writes back (req 5.2). Re-run stamping
whenever the data-set config changes (req 6).

### B.7 On-the-fly KPIs

Already met on the mock. The B.1 real-row contract feeds `computeTermKpis` / `aggregateKpis` unchanged, so
the KPI band (Industry & Host Revenue, Passengers, Share, FMS, Share gap) stays live as terms are added
(req 7). No engine change beyond sourcing rows through the seam.

### Deferred

**Entity separation (req 8).** Kept single-Quote by decision. A future `DataSet` entity would decouple one
data set from many shells and many scenarios; noted here as the forward path.

---

## Part C — Suggested sequencing (for eventual implementation)

1. **Annualization fix + `FlownRow` contract spec** — smallest, highest-signal; unblocks correct
   magnitudes and defines the seam payload everything else rides on.
2. **Current-contract mapping + `compareFare` facet** (B.2).
3. **Geography backbone + scope binding + stamping engine + editable hierarchy** (B.4, B.6; **D.1, D.2**).
   Wire `DL_Geography__c` into the resolver (hierarchy walk → geography-containment matching), bind term
   scope attributes to `DL_Geography__c.DL_Code__c`, and add the hierarchy-aware scope picker. This is what
   turns mock-string stamping into real row → term stamping.
4. **Directionality / includes-excludes / in-or-out-of persistence** (**D.3**) — matching-semantics
   promoted to real `DL_*` attributes once the backbone is proven.
5. **Template libraries + admin maintenance** (B.5; **D.5** — pick Approach 1 vs. 2 first).
6. **(Deferred) Custom-group many-to-many** geography junction (**D.4**) and the **Data Set entity** for
   req 8 reuse.

---

## Part D — Geography model integration & the Term Library

Two topics deserve their own treatment because the repo just gained the building block for both:
a standalone **`DL_Geography__c`** object (`unpackaged/post_term_builder/objects/DL_Geography__c/`,
seeded by `datasets/sfdmu/dl/en-US/dl-geographies/`). It is a self-lookup hierarchy — airport → city
→ country → region → super-region → custom group, keyed on a unique `DL_Code__c`, typed by
`DL_Geography_Type__c`, parented by `DL_Parent_Geography__c`. **Nothing reads it yet** (its own
description calls it "independent of the Term Builder engine for now"). This part designs how it
becomes the backbone of data analysis (D.1–D.4) and how a reusable Term Library builds on it (D.5).
It refines, rather than replaces, §B.4 (term geography), §B.5 (libraries), and §B.6 (stamping).

### D.1 — `DL_Geography__c` as the resolver backbone (recommended anchor, highest priority)

This is the single integration that makes "integrate geography into the data analysis" real, and
everything else in Part D depends on it.

- **The join.** A `FlownRow.marketPair` such as `"ATL-LHR"` (§B.1) decomposes into two airport
  `DL_Code__c` endpoints. Each endpoint is walked up `DL_Parent_Geography__c` to yield its full
  ancestry (LHR → London → GB → Europe → EMEA). This is the missing link between a concrete market
  and the abstract geographies a term is scoped to.
- **Data delivery — settle this before writing the resolver.** The resolver (`termMatchesMarket` /
  `resolveTermForMarket`) is **client-side** in `dlDemoModel.js`, but `DL_Geography__c` is **server-side
  master data**. So D.1 has an unstated prerequisite: ship the geography ancestry to the client. Recommended
  shape — extend `getBuilderState` to include a compact geography map (each `DL_Code__c` → its parent code +
  type), let the engine build the ancestry-walk lookup once, and resolve `marketPair` endpoints against it
  in-memory. This keeps the hot matching path synchronous (no per-row Apex) and preserves the parked Jest
  suites, which run without a server. A server-side resolver is the alternative but would move stamping out
  of the engine the tests cover — not recommended for the first build.
- **Roll-up aggregation** (req A.1.3). With ancestry known, flown rows can be summed at *any* scope
  level for the KPI band — feeding `computeTermKpis` / `aggregateKpis` unchanged. Today rows can only
  be grouped by their literal `marketPair`; the hierarchy is what lets "all GB markets" or "all Europe
  markets" become a single aggregate.
- **Real term-stamping** (req A.2.5). Upgrade `termMatchesMarket`
  (`dlDemoModel.js:234`) from its two current modes — `DL_MarketGroup` token equality and an exact
  `DL_Origin` string match — to a **geography-containment test**: a term scoped to "Country: GB"
  matches any row whose origin (or destination) airport rolls up to GB. Note that `termMatchesMarket`
  today consumes only `market.origin`; `market.destination` is **not yet read**, so directional lane
  matching (D.3) is part of this upgrade. The tie-breaker is unchanged — `resolveTermForMarket`
  (`dlDemoModel.js:262`) still ranks candidates by `SCOPE_TYPE_RANK` (Airport 5 → Super-region 1 →
  Custom 0) with a stable index tiebreak.
- **Taxonomy alignment — one naming mismatch that MUST be reconciled at build time (verified).**
  `SCOPE_TYPE_RANK`'s keys (`Airport / City / Country / Region / Super-region / Custom`,
  `dlDemoModel.js:161-168`) match five of the six `DL_Geography_Type__c` picklist values exactly. The lone
  divergence is confirmed in the metadata: the object's picklist value is literally **`Custom Group`**
  (`DL_Geography_Type__c.field-meta.xml`) vs. the engine's **`Custom`** rank key. Reconcile these (rename
  one, or map at the boundary) when the backbone lands. This is not optional: `scopeTypeRank`
  (`dlDemoModel.js:172-178`) returns `0` for a **present-but-unrecognized** value — so `"Custom Group"`
  silently ranks as `0`, coincidentally equal to `Custom`'s rank. The alignment therefore *appears* to work
  by accident today; make it explicit so a future rank change to `Custom` doesn't silently desync from the
  picklist. (Note the adjacent edge case: an **absent** scope type returns `-1`, not `0` — so "unknown →
  0" holds only for present-but-unmapped values.)

### D.2 — Binding term scope to geography + a hierarchy-aware scope picker (recommended, coupled to D.1)

The backbone only resolves if a term's scope *references* a geography. Today the scope attribute
values (`DL_Origin`, `DL_Destination`, `DL_MarketGroup`) are free text / free picklist, unrelated to
`DL_Geography__c`.

- **Binding.** Persist scope attribute values as `DL_Geography__c.DL_Code__c` codes, and resolve the
  string → geography record at match time. This keeps the existing `QuoteLineItemAttribute` scope
  representation intact (no new persisted shape for terms) while making it geography-resolvable.
- **UI.** Replace free-text scope entry in the term card with a validated, hierarchy-aware **geography
  picker** sourced from `DL_Geography__c`. This directly satisfies req A.2.2's "visibility into
  geography definitions in the UI." Reuse `termScopeChips` / `scopeLabel` (`dlDemoModel.js`) for the
  read-side chip display so the rail card is unchanged.

### D.3 — Directionality & "in / out of a geography" semantics (design now, persist phased)

These are the matching-semantics layer — they change *which* rows a term matches, so the D.1 resolver
must account for them by design even if persistence is phased.

- **Directionality** already exists as the `DL_Directionality` attribute, and `scopeLabel` already
  surfaces it — note it does **not** hardcode "Between"; it echoes whatever the term's `DL_Directionality`
  value holds (so "Between" appears only when that value is "Between"). The D.1 upgrade wires this to test
  origin-only vs. destination-only vs. bidirectional containment (which is why `market.destination` must
  start being read).
- **Includes / Excludes** is `SCOPE_OPERATORS = ["Includes","Excludes"]` — passed into
  `termMatchesMarket` as a UI-only `operator` argument, deliberately **never a persisted attribute**
  (`dlDemoModel.js:133`). To round-trip an exclusion into a saved shell it must be promoted to a real
  `DL_*` attribute.
- **"In / out of a geography"** (e.g. all market pairs into/out of ATL) is **unmodeled** today; design
  it as a scope facet on the term, evaluated against the resolved origin/destination ancestry.
- **Recommendation:** specify all three in the D.1 resolver design; sequence the *persistence* of the
  operator and the in/out-of facet after the backbone is proven.

### D.4 — Custom-group many-to-many (deferred; document the forward path)

Delta's JV-style scopes (e.g. a Korean Air joint-venture market set) require a geography to belong to a
group of arbitrary geographies — a **many-to-many** the current `DL_Geography__c` self-lookup (strict
tree) cannot express. Document the forward extension: a `DL_Geography_Group_Member__c` junction over
`DL_Geography__c` (group ↔ member). Sequence it last — least common, highest complexity — and keep it
out of the first backbone build.

### D.5 — The Term Library: two modeling approaches (document both; decision deferred)

Requirement: analysts import pre-built templatized **terms** (with geography visible), import full
templatized **contracts** or copy a term set from an existing contract, and an **admin** maintains the
libraries (reqs A.2.2, A.2.3, A.2.4). Favorites are explicitly ruled out.

The governing constraint: a **term is a `QuoteLineItem`** — inherently transactional, always bound to
a Quote. A library entry therefore cannot *be* a term; it must be a **definition** that materializes
into real Terms (and fares, and scope attributes) on a live quote. Two ways to model that definition:

#### Approach 1 — Custom definition objects, materialized on the fly (lean recommendation)

- **`DL_Term_Template__c`** — the reusable term definition: name, description,
  **`DL_Scope_Geography__c` (lookup → `DL_Geography__c`)**, directionality, scope operator, in/out-of,
  measure/goal, requirement value, default discount, default fare codes (multiselect over the
  `DL_Fare_Codes` global value set), hierarchy rank, active flag, library tag.
- **Optional `DL_Contract_Template__c`** — a named full term set (parent of many `DL_Term_Template__c`);
  and, only if per-fare discount granularity is needed, a `DL_Term_Template_Fare__c` child (otherwise
  the default-fare-codes multiselect suffices).
- **Instantiation reuses the existing write pipeline verbatim.** A new `@AuraEnabled` method (e.g.
  `addTermsFromTemplate(quoteId, templateIds[])` on `RLM_DeltaTermBuilderController`) maps each template
  → the existing `addTerm` field builder + `RLM_DeltaCatalogController.saveLineAttributes` (stamping
  `DL_ScopeType` / `DL_Origin` / `DL_Destination` / … from the template's geography) + `addFareClassesToTerm`,
  all through PST. (`saveLineAttributes` lives on `RLM_DeltaCatalogController`, not the Term Builder
  controller — call it there or thin-wrap it.) No new write machinery. "Copy the term set from an existing contract" is a **save-as-template** path off
  the same objects (harvest a shell's terms into `DL_Term_Template__c` rows).
- **Admin maintenance** = a tab plus CRUD grants on `RLM_TermBuilderPermset` — exactly the pattern
  `DL_Geography__c` already follows.

| | Approach 1 (custom objects) |
|---|---|
| **Pros** | Clean definition/transaction split; admin-friendly and growable; geography-native (the lookup ties straight into D.1); no product-catalog pollution; models a *full-contract* template cleanly. |
| **Cons** | New objects/fields/permset/seed to build and maintain; a second scope representation (template fields vs. `QuoteLineItemAttribute`) to keep aligned; instantiation mapping code to write. |

#### Approach 2 — Pre-defined Terms in the Product Catalog

- Each template = a Product2 **variant of `DL-TERM`** whose `ProductAttributeDefinition` default values
  pre-set the scope attributes (the controller already reads PCM attribute-definition overrides),
  grouped in a "Delta Term Templates" ProductCategory and instantiated through the existing product
  finder + `addTerm`.

| | Approach 2 (catalog products) |
|---|---|
| **Pros** | Reuses catalog/PCM machinery; templates surface in the native product picker; attribute defaults are a native PCM concept. |
| **Cons** | Conflates sellable SKUs with saved configurations; PCM defaults are limited (one default per attribute — no full fare-set / discount / hierarchy-rank modeling); no clean catalog primitive for a *full-contract* template (a bundle-of-term-bundles is awkward); heavier admin story (catalog management + a PricebookEntry per template product); poor fit for a growing, analyst-curated library. |

**Net / recommendation (decision deferred by request).** Approach 1 (custom objects) fits the
requirements better — admin-maintained, geography-scoped, full-contract-capable, and it reuses the
existing `addTerm` pipeline. Approach 2 is viable only if templates must live inside the native
product-selection UX *and* the set stays small and fixed. Recorded here for a later decision; not yet
chosen.

### D.6 — How Part D changes the sequencing

The geography backbone (D.1) + scope binding (D.2) become the concrete content of Part C step 3
("stamping engine"): without them, stamping runs only on mock market strings. Directionality/in-out-of
persistence (D.3) and the custom-group junction (D.4) follow. The Term Library (Part C step 4) picks up
D.5's deferred approach decision before build.

---

## Verification approach (when implementation begins)

- **Seam back-compat.** The `FlownRow` contract must match the *existing* `term.modeling` keys in
  `dlDemoModel.js` (`modeling.rows`, `modeling.flown`) so mock fill stays byte-identical and the parked
  Jest suites (`dlDemoModel/__tests__`, ~101 tests across both build variants) remain green.
- **Annualization worked examples** as unit tests: 6-month → ×2, 12-month → ×1, and the chosen
  ≥12-month behavior.
- **Stamping determinism.** `resolveTermForMarket` on real rows must be covered by tests asserting the
  most-specific-wins hierarchy and the stable tiebreak, including the editable-hierarchy override.
- **Doc/convention checks** per `CLAUDE.md` (this file lives in `docs/features/`, lower-kebab-case).

## Key files

| File | Role |
|---|---|
| `unpackaged/post_modularized_term_builder/lwc/dlmWorkspaceShell/dlmWorkspaceShell.{js,html}` | The 2-tab host; `periodFactor` consumer; per-Term model cache + contract KPI band. |
| `unpackaged/post_modularized_term_builder/lwc/dlmDataSetConfig/dlmDataSetConfig.js` | The Tab 1 data-gathering panel (analysis period, subsidiaries, carriers). |
| `unpackaged/post_term_builder/lwc/dlDemoModel/dlDemoModel.js` | The engine: `term.modeling` seam, `seedTermFlown`/`seedModel`, `resolveTermForMarket`, `SCOPE_TYPE_RANK`, `termScopeChips`/`scopeLabel`. |
| `unpackaged/post_term_builder/lwc/dlmTermCard`, `dlmTermsRail` | Scope chips, Includes/Excludes toggle, rank badge. |
| `unpackaged/post_term_builder/classes/RLM_DeltaTermBuilderController.cls` | `getBuilderState`, `addTerm`, `addFareClassesToTerm`, renewal helpers (`restoreClonedLineFidelity`); host for a future `addTermsFromTemplate` (D.5). |
| `unpackaged/post_term_builder/classes/RLM_DeltaCatalogController.cls` | `saveLineAttributes` — the scope-attribute writer (`QuoteLineItemAttribute` values); reused by the D.5 template-instantiation path. |
| `unpackaged/post_term_builder/objects/DL_Geography__c/` | The geography master-data object (self-lookup hierarchy: `DL_Code__c`, `DL_Geography_Type__c`, `DL_Parent_Geography__c`). Resolver backbone — see Part D. Currently unwired. |
| `datasets/sfdmu/dl/en-US/dl-geographies/` | Seed data for `DL_Geography__c` (12 records; requires `RLM_TermBuilderPermset` FLS before load). |
| `docs/features/delta-negotiation-modeling-demo.md` | Companion Tab 2 spec (seam contract, G2 geography attributes, G3 grid columns). |
