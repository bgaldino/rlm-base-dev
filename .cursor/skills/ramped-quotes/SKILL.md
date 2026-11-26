---
name: ramped-quotes
description: >-
  Build and verify multi-year Revenue Cloud group-ramp quotes through the Connect API
  or the quote UI. Use when creating per-period quote groups, cloning ramp segments, checking price
  uplift or compound uplift, or distinguishing group ramps from line ramps.
---

# Ramped Quotes — Build & Verify Multi-Year Group Ramps

Use this skill to build, verify, or report a **multi-year ramped** Revenue Cloud
quote (one commitment segment per period) over the Connect API or in the quote UI, and to get the
per-segment **price uplift** — including **compound** uplift — right. It is
consumable by any AI agent (Cursor, Claude Code, Copilot, Codex, Windsurf,
Aider).

> **Pinned to Release 264 / API v68.0.** Field legality (`field-legality.md`) and the enums here are
> live-observed on a 264 org (v68.0); re-verify on the target release at merge
> time. Ramp build is **transaction authoring**; the compound-uplift *engine*
> (the pricing procedure's `PriceRevision` element) belongs to
> `.cursor/skills/pricing-procedures/elements/price-revision-compound-uplift.md` —
> this skill links to it, not duplicates it.

Two distinct ramp mechanisms exist — do not confuse them:

| Mechanism | Shape | Compounds? |
|---|---|---|
| **Group ramp** (this skill) — `placeSalesTransaction` create → `groupRampAction: EditGroup` → clone × (N−1) → add the `RampScheduleGroup` parent (multi-schedule) | one **`QuoteLineGroup`** per period; segments carry `RampIdentifier` | **Yes** — the group holds `RampUpliftType`, so uplift can compound |
| **Line ramp** — `createRampDeal` on a single line (`/connect/revenue-management/sales-transaction-contexts/{lineId}/actions/ramp-deal-create`) | ungrouped segments (`QuoteLineGroupId=null`) | **No**: there's no group to hold the uplift mode, and `RLM_DefaultPricingProcedure` applies **no** `UnitPriceUplift` to line ramps at all (the ramp filter is limited to group ramps; measured 2026-10-28). Prefer group ramps. |
| *(legacy)* `/commerce/sales-transactions/ramp-deals` (v63–66) | quantity/revenue **commitment** ramp on the deprecated `/commerce/` path | out of scope |

**Compound price uplift requires the group ramp.** Build it with the sequence below, or in the
quote UI (`ui-group-ramp.md`, measured on 264).

## Quick Rules

1. **A group ramp is a per-period segment structure — and its shape depends on the
   *Multiple Ramp Schedules Per Transaction* setting** (`enableGroupRampMultiSchedulePref`),
   which **this repo enables by default** (`config/project-scratch-def.json`,
   `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`). **ON (repo
   default) ⇒ a two-level structure:** a top-level `QuoteLineGroup` with
   `Type='RampScheduleGroup'` and one **segment subgroup per period** nested under it
   (`ParentQuoteLineGroupId` → the schedule group). **OFF ⇒ a single-level list** of
   period groups (`ParentQuoteLineGroupId` null). Either way the call order is: (1)
   `placeSalesTransaction` **create** — Quote + period-1 group + one `QuoteLineItem`
   per product; (2) `groupRampAction: "EditGroup"` — `IsRamped=true`,
   `SegmentType=Yearly`, which converts the posted group into segment 1 and stamps
   `RampIdentifier` on its lines; (3) **clone × (N−1)** — one clone per
   *additional* period; (4) in multi-schedule mode, add the `RampScheduleGroup` parent
   yourself (measured on 264: neither call creates it, see step 2). A 3-year ramp =
   create + EditGroup + 2 clones + parent. The exact
   two-level graph and resulting ids must be confirmed by read-back on the target org
   (live-verify rule below).
2. **The group is created plain, then ramped by `EditGroup`.** Do **not** try to
   `POST` an already-ramped group. `EditGroup` sets `IsRamped`/`SegmentType`/dates.
3. **Clone is a separate Connect resource**, not a `groupRampAction`:
   `POST /connect/rev/sales-transaction/actions/clone` with
   `{salesTransactionId, recordIds:[<last ramped group id>] (max 1), options:{lineScope}}`.
   `lineScope` ∈ `AllLines` (default) | `RampedLinesOnly`. **Clone only the last
   segment's group.**
4. **Between mutating calls, poll `Quote.CalculationStatus` to a settled state**
   before the next call. Treat an unrecognized status as *stop and look*, never
   "assume done" (see [Status](verify-and-discover.md#status)).
5. **Compound uplift is group + engine, not a line write.** Set the per-segment
   percentage in **`QuoteLineItem.UnitPriceUplift`** (writeable). Set the mode in
   **`RampUpliftType`** (`Standard`|`Compound`) on the ramp **group** — with
   multi-schedule ON (repo default), on the **top-level `RampScheduleGroup`** (it
   cascades to segment subgroups and lines); with it OFF, on the single ramp segment
   group. `RampUpliftType` is engine-owned on the *line* and rejected there. The
   compounding itself is driven by the pricing procedure's `PriceRevision` element;
   see [Compound uplift](compound-uplift.md).
6. **`RampIdentifier` is the cross-segment linkage — constant per product across
   all segments.** Group the read-back matrix on it, not `SegmentIdentifier` (unique
   per line). `ParentQuoteLineGroupId` is **not** a linkage key: with multi-schedule
   ON a segment subgroup's `ParentQuoteLineGroupId` points to its top-level
   `RampScheduleGroup`; only with it OFF is it null.
7. **Report from the priced quote — never re-price.** PST already computed net
   prices, subtotals, and totals; read them back.
8. **`org_config.username` for `sf` CLI; `access_token` for REST only** (per
   `AGENTS.md`).
9. **A group-ramped bundle added by API (`AddProducts` into ramped segments) with a one-time or evergreen child cannot be
   amended** (`PlaceSalesTransactionPersistException`; measured on one 264 org). Built in the quote UI the same shape
   amended (evergreen not tried in the UI). Cancel failed too where tried. Detail and the assetization shapes:
   [pitfalls.md](pitfalls.md#api-built-ramped-bundle-with-a-one-time-or-evergreen-child),
   [bundle-children-lifecycle.md](bundle-children-lifecycle.md).
10. **In a UI-built Compound group ramp, a segment's uplift applies to every ramp-stamped line in it, unrounded**
    (One-Time and Evergreen lines too, whose `TotalPrice` doesn't follow the uplifted net; `UnitPriceUplift` 0 on a line
    exempts it). **A partial line edit re-applies the uplift to untouched ramp lines** (net prices move, totals don't):
    finish every ramp edit with a whole-quote Force reprice and read net prices, not totals. No line needs the exemption
    when the source's one-time and evergreen items sit outside the segments (top-level, unramped lines took no uplift)
    or when every ramped line should take the uplift `[inferred]`. A line without a `RampIdentifier` took no uplift (a
    standalone Evergreen product, one org). The uplifted price keeps full precision, not cents: add a rounding step
    after the ramp uplift if the source rounds. Not measured on a Standard ramp (the 2026-10-29 Standard UI run had one
    Term product and exact prices)
    [Measured: 2026-11-11/13, 264, scratch orgs; detail in [pitfalls.md](pitfalls.md#partial-line-patch-on-a-compound-ramp),
    [ui-group-ramp.md](ui-group-ramp.md#what-the-segment-uplift-reaches), [compound-uplift.md](compound-uplift.md)].

## DO NOT

- **DO NOT** write system-generated / read-only fields on the graph: on the line,
  `EndQuantity`, `NetUnitPrice`, `TotalPrice`; on the Quote, `GrandTotal`,
  `TotalPrice`, `CalculationStatus`, `QuoteNumber`. They are computed — the call
  fails if you set them.
- **DO NOT** set `RampIdentifier` or `SegmentIdentifier` on a line — the ramp
  actions stamp them. Whether a caller write is refused is not measured ([field-legality.md](field-legality.md)).
- **DO NOT** write `RampUpliftType` on `QuoteLineItem`/`OrderItem` via Place — it
  is engine-owned there (rejected as not-writeable even when FLS shows editable). Set it on the ramp **group**: the
  **top-level `RampScheduleGroup`** in multi-schedule mode (repo default), or the single segment group when the
  setting is off; it cascades to every ramped line in the schedule.
- **DO NOT** use the trial segment type `Trial` — the live enum is **`FreeTrial`**
  (`SegmentType` ∈ `Yearly`, `Custom`, `FreeTrial`, `Prorated`).
- **DO NOT** clone more than one group per call (`recordIds` takes exactly one id, the last segment's group), or
  expect a clone to vary quantity or price per period: it copies the prior segment as-is, so set per-segment values
  (quantity, `UnitPriceUplift`) after cloning. Do not fake growth silently; note it.
- **DO NOT** rely on an active CML model to add **standalone** products to a ramp segment, or put a one-instance
  rule on a quote-level virtual container (it sees every segment's lines at once). A rule-added child of a ramped
  parent is ramped. Measured detail: [pitfalls.md](pitfalls.md#cml-rules-and-ramp-segments).
- **DO NOT** treat a null `RampIdentifier` on read-back as a graph mistake before checking stale context
  definitions (sync them), a line a group-level CML `require` added, an `AddProducts` bundle child, or a
  standalone Evergreen line: [pitfalls.md](pitfalls.md#null-rampidentifier).
- **DO NOT** trust a `pricingPref: "System"` reprice to fix a **cloned** segment: delta pricing can skip its stale
  lines. Make the final reprice `Force` and check each ramp line's `PriceWaterfallIdentifier` starts with its own Id
  ([pitfalls.md](pitfalls.md#system-reprice-of-a-cloned-segment)).
- **DO NOT** trust untouched lines after a **partial line PATCH on a Compound ramp**
  ([pitfalls.md](pitfalls.md#partial-line-patch-on-a-compound-ramp)).
- **DO NOT** reprice a lifecycle quote after its order is activated: lifecycle lines price from the source asset's
  current state and activation rewrites it; a measured renewal repriced to 0
  ([pitfalls.md](pitfalls.md#reprice-after-activation),
  [asset-lifecycle-changes/verification.md](../asset-lifecycle-changes/verification.md)).
- **DO NOT** claim a build "works" from an offline dry-run — a mutating ramp run
  must be verified against a **live 264 org**, writing only to a confirmed
  **writable** org.
- **DO NOT** assume a custom Create Ramp Schedule flow receives the quote id: it receives no inputs on 264
  ([custom-ramp-flow.md](custom-ramp-flow.md)).

## Entry Conditions

| Situation | Use |
|---|---|
| Build / add a segment to / verify a multi-year **group** ramp quote | This skill |
| Build or check a group ramp **in the quote UI** (demo, rep-built quote) | `ui-group-ramp.md` |
| Get **compound** per-segment uplift right (the `PriceRevision` engine, `IsCompoundUpliftEnabled`, prerequisites) | [Compound uplift](compound-uplift.md) → `.cursor/skills/pricing-procedures/elements/price-revision-compound-uplift.md` |
| Turn on **Advanced Detail Line Pricing** / sync context definitions (a compound prerequisite) | `.cursor/skills/context-service/SKILL.md` |
| Resolve Account / Pricebook / Product2 / PricebookEntry ids | [Discovering ids](verify-and-discover.md#discovering-ids) |
| Build a non-ramp quote → order → asset | `scripts/build_quote_to_asset.py`; `.cursor/skills/txn-data-harness/SKILL.md` |
| The v68 Connect endpoint catalog (place, clone, ramp-deal, amend/renew/cancel) | `docs/salesforce/264/dev-guide/index.md` (tracked 264 dev-guide index — use the `/connect/rev/...` payloads above). `docs/api/transaction-management-apis-reference.md` is a v68-grounded summary of the same routes; prefer the dev-guide page when the two disagree |
| A null `RampIdentifier` / stale context definitions | `.cursor/skills/context-service/SKILL.md`; for a line a group-level CML `require` added, or a one-time/evergreen child added with `AddProducts`, see [pitfalls.md](pitfalls.md) and Quick Rule 9; a standalone Evergreen line carries none ([ui-group-ramp.md](ui-group-ramp.md)) |
| Replace the admin flow behind Create Ramp Schedule, or edit a segment's uplift after creation | [custom-ramp-flow.md](custom-ramp-flow.md) |
| A reprice, clone or partial-PATCH result looks wrong | [pitfalls.md](pitfalls.md) |

## The proven build sequence

Full payloads, the leap-year rule, the multi-schedule parent and the response checks are in
[build-sequence.md](build-sequence.md). In order:

1. **`placeSalesTransaction` create:** Quote + period-1 group + one `QuoteLineItem` per product (`Product2Id` and
   `PricebookEntryId`, Quote `CurrencyIsoCode` = account currency). Check the body for `errorResponse`, not just a Quote id.
2. **`groupRampAction: "EditGroup"`:** `IsRamped=true`, `SegmentType=Yearly`, segment 1 exactly 365 days; each
   `referenceId` the record's own Id. In multi-schedule mode add the `RampScheduleGroup` parent yourself after the clones.
3. **`POST /connect/rev/sales-transaction/actions/clone`** once per additional period, cloning the last segment's group.
4. **Place PATCH:** `RampUpliftType='Compound'` on the parent group and `UnitPriceUplift` per segment line, `pricingPref: "Force"`.

Poll `Quote.CalculationStatus` between calls and read the groups back before the prices
([verify-and-discover.md](verify-and-discover.md)). Compound uplift: [compound-uplift.md](compound-uplift.md) and
[the engine](../pricing-procedures/elements/price-revision-compound-uplift.md).

## Examples

**Worked example — a 3-year ramp on a standalone SKU** (substitute your own ids):

1. Resolve ids for one eligible subscription (term-defined) product + its standard,
   active `PricebookEntry` in the account currency (no per-product ramp flag needed
   for group ramps).
2. `placeSalesTransaction` create → Quote + "Year 1" group + one line (365-day
   window; resolve a `BillingTreatmentId`). Poll until settled: `CompletedWithPricing`
   on a default Foundations build, `CompletedWithTax` where estimated tax is on.
3. `placeSalesTransaction` `EditGroup` on the Year-1 group (`IsRamped=true`,
   `SegmentType=Yearly`, each `referenceId` the record's Id). Poll.
4. `cloneSalesTransaction` twice (Year 2, Year 3), each cloning the last ramped
   segment. Poll after each. In multi-schedule mode, then POST the `RampScheduleGroup`
   and reparent the segments to it by DML (step 2 of the sequence), and read the groups
   back to get its id.
5. For compound uplift (step 4 of the sequence): PATCH `RampUpliftType='Compound'`
   on the **top-level `RampScheduleGroup`** and per-segment `UnitPriceUplift`, then
   reprice (`pricingPref:"Force"`) and poll (needs the fully-configured
   `PriceRevision` engine — [Compound uplift](compound-uplift.md)).
6. Read back; report TCV, per-year subtotal, % of TCV, ramp-by-product matrix.

Expected compound shape for this 3-year ramp (base 360, uplifts 5/3% — baseline +
2 uplifts = 3 periods): 360 → 378 → 389.34 (applied % 0 → 5 → 8.15). A 4-year ramp
would add a 3rd uplift, e.g. +2% → 397.1268 (applied % 10.313; the uplift isn't rounded, so 397.13
only with a rounding step after the ramp uplift, see `compound-uplift.md`).

## Validation Checks

- [ ] Group ramp (per-period segment structure — the two-level `RampScheduleGroup`
      in the repo's multi-schedule default), not a line ramp, if compound uplift is
      in scope.
- [ ] The `Yearly` segment 1 sent to EditGroup is **exactly 365 days** and doesn't contain
      29 February (clones end later segments on calendar anniversaries); `Custom` used for
      variable/calendar durations.
- [ ] `BillingTreatmentId` resolved on each line whose frequency differs from the term
      unit (Active, account
      currency, `CanChangeBillingFrequency=true`).
- [ ] No read-only/system fields written on the graph (see [`field-legality.md`](field-legality.md)).
- [ ] `RampUpliftType='Compound'` on the ramp **group** (the top-level
      `RampScheduleGroup` in multi-schedule mode), never on the line; per-segment
      `UnitPriceUplift` set on lines, then repriced with `pricingPref:"Force"`.
- [ ] `CalculationStatus` polled to a settled state between calls; unknown status
      halted, not assumed.
- [ ] Group shape asserted before prices (*Read-back*): segment fields set, one segment per
      period, and in multi-schedule mode one `RampScheduleGroup` parent that every segment points
      at.
- [ ] Read-back grouped on `RampIdentifier`; every ramped line carries both
      `RampIdentifier` and `SegmentIdentifier` (proves it went through
      `groupRampAction`); TCV reconciles.
- [ ] Compound arithmetic verified against a read-back (applied % compounds on the
      prior factor).
- [ ] Any mutating run executed against a confirmed **writable** live 264 org.


## Sub-files

- `build-sequence.md` — the API build with payloads (create, EditGroup, clone, compound PATCH). Read it to build a group ramp.
- `verify-and-discover.md` — `CalculationStatus` polling, the read-back queries and report, and resolving Account, price book entry and billing treatment ids. Read it between and after build calls.
- `pitfalls.md` — measured detail behind the DO NOT list: CML rules in ramp segments, null `RampIdentifier`, reprice of a cloned segment, partial PATCH re-uplift, reprice after activation.
- `compound-uplift.md` — Compound price uplift: the quote-side prerequisites, a read-back
  check, and the unrounded precision (round after the uplift); the engine and full arithmetic live
  in `pricing-procedures`. Read it when applying or checking Compound.
- `field-legality.md` — which ramp and pricing line fields are writable on live 264, including `QuoteLineGroup.UnitPriceUplift`. Read it when a call rejects a field.
- `custom-ramp-flow.md` — the Create Ramp Schedule admin flow contract (no inputs on 264), editing a segment's uplift after creation, and ramping products automatically. Read it before customizing the ramp flow.
- `bundle-children-lifecycle.md` — a group-ramped bundle with a one-time or evergreen child: limiting the child to
  segment 1, what a UI-built bundle ramp carries per segment, assetization shape, the amend/cancel 500 on API-built bundles, renewal rules and lifecycle-recipe prerequisites. Read it before
  amending, cancelling or renewing a ramped bundle.
- `ui-group-ramp.md` — building a Standard or Compound group ramp in the 264 quote UI, the
  expected prices and assets, which lines the segment uplift reaches, and how to verify. Read it for
  a UI demo or a UI-built quote.

## Headless toolkit (in development)

A dependency-free `scripts/ramp_deals/` toolkit (schedule math, payload builders, status polling, read-back
invariants) mirroring `scripts/expression_sets/` is being built on branch `feat/ramp-deals-core`, not yet merged to
`main`. Until it lands, use the raw Connect calls in [build-sequence.md](build-sequence.md); when it merges, wire its
CLIs into this skill's routing.

## Related References

- **Compound-uplift engine** (`PriceRevision`, `IsCompoundUpliftEnabled`, ramp vs
  non-ramp path): [`../pricing-procedures/elements/price-revision-compound-uplift.md`](../pricing-procedures/elements/price-revision-compound-uplift.md).
- **Advanced Detail Line Pricing / context definition sync** (compound
  prerequisite; null-`RampIdentifier` fix): `.cursor/skills/context-service/SKILL.md`.
- **v68 Connect endpoint catalog** (place, clone, ramp-deal, amend/renew/cancel):
  `docs/salesforce/264/dev-guide/index.md` (tracked 264 dev-guide — `/connect/rev/...`).
  `docs/api/transaction-management-apis-reference.md` summarizes the same v68
  routes; prefer the dev-guide page when the two disagree.
- **Non-ramp quote→order→asset builder:** `scripts/build_quote_to_asset.py`;
  `.cursor/skills/txn-data-harness/SKILL.md`.
- **RLM object/field model:** `.cursor/skills/revenue-cloud-data-model/SKILL.md`.

