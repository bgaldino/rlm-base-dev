# Ramped Quotes — Pitfalls (measured detail)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. The long form of the DO NOT list and Quick Rules 9 and 10 in SKILL.md.

## CML rules and ramp segments

- **DO NOT** rely on an active CML model to add **standalone** products to a ramp segment.
  Help (*Considerations for Ramp Deals*): configuration rules don't recognize quote or order
  groups, and a rule that adds a standalone product to a segment doesn't ramp it or add it to
  later segments. A rule-added **child of a ramped parent** is ramped and carried forward.
  A group-level `require` (a `groupBy = SalesTransactionItemGroup` container) adds its products to
  ramped segments with blank `RampIdentifier`, `SegmentIdentifier` and `SegmentType` when it fires
  during a Connect clone or a `configurationMethod: Force` Place without `groupRampAction`. Rules keyed
  on `IsLineGroupRamped__std` and `ItemSegmentType == "Yearly"` fired during the clone even with every Place call
  set to `Skip`. A `Force` Place with `groupRampAction: AddProducts` stamped the products it added, but
  not blank lines already on the quote (one 264 org, 2026-11-06, test model, standalone Term Annual
  products; order and amend of the blank lines not measured). See
  [constraint-models → Ramp groups and segments](../constraint-models/SKILL.md#ramp-groups-and-segments).
  The bundles tested in ramped segments, added in the quote UI or cloned, kept ramp ids on every line; see
  [Cloning a segment that holds a bundle](bundle-children-lifecycle.md#cloning-a-segment-that-holds-a-bundle).
- **DO NOT** allow only one instance per type on a virtual transaction (`Quote`) container in a group ramp.
  The container sees every segment's lines at once: the configurator is handed every line of the quote in one
  set, and no per-group scope was found on the input side. A `groupBy` container partitions by an attribute
  value; whether that can scope a ramp segment wasn't shown. Source shows the solver's cardinality check allows
  one line of an unsplit type (or in a `[0..1]` relation) per relation, and a quote-level virtual container puts
  every segment's lines in one relation, so a second segment's line would fail it [Platform behaviour, traced in
  part]. The measured message below is not the solver's text, so whether this check produced it isn't
  established. What Place does to a cloned segment line's status and quantity wasn't traced (live check). See the container rule in
  [constraint-models → Checks across top-level lines](../constraint-models/quantities-from-attributes.md#checks-across-top-level-lines-a-virtual-quote-container).
  Measured 2026-11-11 (fresh 264 `ent-sb0` scratch org, quote UI): with the bundle relation `[0..1]` and `@(split = false)` on the top-level line types it held,
  the ramp quote got "You can't add more than one of the same '<product>' product to the '<type>' product
  class" and the configurator couldn't save. Widening those relations' cardinality and dropping
  `split = false` from those types (changed together) fixed it. Write the container's cross-line checks as
  totals across all segments. The container pattern, including its `[0..1]` bundle bound for an unramped
  quote, is in the same section. Whether a `[0..1]` or `split = false` bound alone is the trigger, or a
  setting is also involved, wasn't isolated (live check).
  Model a one-instance type per bundle, not in a shared quote-level container.

## Null RampIdentifier

- **DO NOT** treat a null `RampIdentifier` on read-back as a graph mistake — it
  usually means the org's **context definitions are stale**; a Context Definition
  sync fixes it (see `.cursor/skills/context-service/SKILL.md`). Other known causes: a line a
  group-level CML `require` added (DO NOT above), and a one-time or evergreen bundle child added with
  `AddProducts` into ramped segments (Quick Rule 9), and a standalone Evergreen line
  ([ui-group-ramp.md](ui-group-ramp.md)).

## System reprice of a cloned segment

- **DO NOT** trust a `pricingPref: "System"` reprice to fix a **cloned** group-ramp segment. When delta
  pricing applies (rule linked below), only the edited lines and the
  lines that depend on them re-run, so a clone's stale lines can be skipped; Help says Compound Uplift lines in a
  ramp group are repriced on every run regardless of delta pricing
  [Help: `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure`], so the skip would apply only to
  lines without Compound Uplift [inferred]. A
  segment created by clone can keep its clone-time price indefinitely.
  Delta pricing (on in every Foundations-built org
  [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`]) is defined once in
  [pricing-procedures](../pricing-procedures/runtime-and-observability.md#delta-pricing);
  when it doesn't apply, every line reprices
  ([transaction-line-editor → runtime behavior](../transaction-line-editor/runtime-behavior.md)).

  Measured 2026-10-29/30 on 264 with a probe that set the uplift at placement:
  - 8 of 8 builds came out of cloning with the last segment un-uplifted (setting the uplift
    after the clones instead avoided it, 8 of 8);
  - one System reprice repaired 7 of them (the request contents were not recorded, so it
    isn't known to be header-only; a graph-style System request with only the Quote header
    isn't priced, though a request carrying a context id is when lines exist, not measured
    [Platform behaviour, traced]);
  - the 8th stayed stuck through that reprice and two more System reprices;
  - one **`Force`** reprice fixed it (todo 160).

  Make the final reprice `Force`. On a ramped renewal, amendment or cancellation quote, do it
  before the order is activated, not after (see
  [asset-lifecycle-changes → verification](../asset-lifecycle-changes/verification.md)).
  Then check that every ramp line's `PriceWaterfallIdentifier`
  starts with its **own** Id. One that starts with `Quote_QuoteLineItem_<other Id>` hasn't been
  fully priced since its clone. (`build_quote_to_asset.py` asserts this.)

## Partial line PATCH on a Compound ramp

- **DO NOT** trust the lines you didn't touch after a **partial line PATCH on a Compound ramp.**
  Measured 2026-11-11 on a fresh 264 `ent-sb0` scratch org (a UI-built Compound ramp): a
  Place PATCH (`pricingPref: "System"`, `configurationMethod: Force`) that set only some lines'
  `UnitPriceUplift` re-applied the uplift to the other ramp lines. Their `NetUnitPrice` was uplifted
  again on top of the already uplifted net (each segment by its applied % once more), while
  their `TotalPrice` stayed put. **Reprice All** in the line editor restored every line; a `Force`
  reprice wasn't tried for this Place-PATCH case; it was tried after a System PATCH (below). What the source shows: when delta
  skipping doesn't apply, every line runs through every pricing element again, and the uplift step isn't
  idempotent, so an untouched line is uplifted again; when it applies, only the edited lines and their
  dependents re-run [Platform behaviour, traced]. Help adds that a Compound Uplift Price Revision step reprices every line in the ramp group on each run regardless of delta pricing [Help: `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure`]; that fits the re-uplift of untouched ramp lines [inferred]. The 2026-11-11 org was built from the repo's scratch
  definition, so delta pricing was probably on, but its setting wasn't read there, and whether the re-uplifted
  lines (the Term child) were dependents of the edited ones, or this is a different path, is not established
  (live check). On a second org with the setting read as on, a System PATCH of one ramp line with no field change (configuration Skip) left every line's waterfall id unchanged, yet re-applied the compound uplift to every uplifted line's `NetUnitPrice`, unrounded, with totals unchanged [Measured: 2026-11-12, 264, scratch; one org]. Help's rule fits which lines moved, but not the unchanged waterfalls or the uplift compounding on the stored net; that path is not traced. Don't
  rely on a partial PATCH leaving other lines untouched. To reproduce: on a Compound UI ramp,
  PATCH `UnitPriceUplift` on some lines of segments 2 and 3 only, then read the other lines'
  `NetUnitPrice` in those segments (measured with a bundle: the PATCHed lines were its Evergreen and
  One-Time children, the re-uplifted ones its Term child). Finish every ramp line edit with Reprice
  All and re-read all segments.

  After a System PATCH on a delta-pricing org, a Force reprice of the whole quote with no line changes restored
  every net price exactly [Measured: 2026-11-13, 264, scratch, one org; Compound ramp, three segments, two products,
  delta pricing on; quote only, not ordered; a Place call with Force pricing, not the line-editor button]. So run a
  whole-quote reprice after any ramp edit and read the net prices, not the totals `[inferred]`. The cause is not
  isolated.

## Reprice after activation

- **DO NOT** reprice a lifecycle quote after its order is activated. Lifecycle lines are priced
  from the source asset's current state, and activation rewrites that state [Platform behaviour,
  traced in part]; see
  [asset-lifecycle-changes/verification.md](../asset-lifecycle-changes/verification.md).
  Measured once on a renewal quote: a full reprice (every line, pricing `Force`, configuration
  `Skip`) after the order was activated set the renewal lines' totals and the quote total to
  0 [Measured: 2026-11-12, 264, scratch org]: each lot became a -lot/+lot pair netting 0, and the
  order and assets were unchanged. An activated cancellation quote also repriced to 0, while an amend-add and an
  Evergreen-reduce amendment quote did not change [Measured: 2026-11-26, 264, ent-sb0 harness build]. Other
  amendment shapes and any ramped quote are not measured; why the reprice returned 0 is not traced. Read quote values before activation and
  don't reprice afterwards.

## API-built ramped bundle with a one-time or evergreen child

Quick Rule 9 in SKILL.md states the rule. The measured amend and cancel failures, the assetization shapes and the
lifecycle recipe are in [bundle-children-lifecycle.md](bundle-children-lifecycle.md).
