# Ramped Quotes — Bundles with one-time / evergreen children, and their lifecycle

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. Measured 2026-11-05/06 on one 264 scratch org
> (Enterprise, API 68.0), **Quote** output; sections and bullets dated 2026-11-11 come from fresh 264 `ent-sb0`
> scratch orgs. Rows say whether the bundle was built by API or in the quote UI;
> the two paths gave different amend results (see the matrix). "API-built" means the bundle was added with
> `AddProducts` into already-ramped segments; the EditGroup-then-clone shape is covered separately below. Treat
> each row as a measurement, not a root cause. Re-verify on the target org.

## Limiting a one-time child to segment 1

A group-ramped term bundle (root + term child + one-time child). Add the bundle to every segment with
`groupRampAction: AddProducts` (one line set per segment group, plus a `QuoteLineRelationship` per child with
`AssociatedQuoteLinePricing`), then `DeleteProducts` the one-time child's lines in segments 2 and 3.

- The root and the term child are stamped with `RampIdentifier`/`SegmentIdentifier`. Built by API, a **one-time or evergreen
  child gets neither** when added with `AddProducts` into already-ramped segments, so no contiguity check applied to it in
  the test, and a segment 2-only delete of it was accepted. (Lines present before EditGroup and then cloned were stamped,
  one-time child included; see [Cloning a segment that holds a bundle](#cloning-a-segment-that-holds-a-bundle). Amend and cancel on that shape were not measured.)
  Built in the quote UI (Browse Catalogs, *Current and Subsequent Segments*), a one-time child of a term bundle **is**
  stamped. An API delete of only the segment 2 line of such a stamped child was refused ("You can't delete ramped line items
  selectively. Include all related ramped line items from subsequent group ramp segments and try again.").
- In the quote UI the same result is reachable for an **optional** child: open the bundle's configurator in segment 2, untick the
  child, save. The dialog says "Configuration changes will apply to current and all future segments", and the child stayed
  in segment 1 only; root and term child stayed in all three. Unticking it in segment 3 only removed it from segment 3.
  Re-ticking it in segment 3 (the last segment, the only one tried) was accepted. No constraint model referenced
  that bundle.
- **A child that a CML rule sizes can't be removed this way.** On a fresh 264 `ent-sb0` scratch org (2026-11-11,
  rules on), unticking an optional child sized by `relation[T] == <answer>` in segment 2's configurator was
  silently re-ticked by the solver after "Processing…", with no message. So with rules on, a rule-sized one-time
  child stays in every segment (see [What a UI-built bundle ramp carries](#what-a-ui-built-bundle-ramp-carries)).
  This fits how the solver treats lines: an optional line the rep hasn't fixed is only a candidate, so a rule that
  needs it makes the solver add it back with no message of its own, and a rule that can be met with none drops it
  silently instead of refusing [Platform behaviour, traced]. Which status the configurator sends for a ticked
  child wasn't established.
  Whether a rule that relaxes the child after segment 1 (one that reads a segment or ramp answer) would let it be
  unticked was not measured.
- **A root answer that zeroes the one-time children does work** (two fresh 264 `ent-sb0` scratch orgs, 2026-11-11,
  rules on, quote UI). The build:
  - a required choice attribute on the bundle root (for example Keep/Drop, default Keep; names illustrative, also in the measured run below);
  - in CML, each one-time child relation keeps its sizing rule under Keep and gets `== 0` under Drop. Give each
    relation its own Drop rule carrying that relation's message: with one shared Drop rule, its message was the
    one reported when a different sizing rule broke on a Keep bundle (consistent with the solver treating the
    answer as free, which it does when the answer reaches the solve as a default, engine-derived or fresh-add
    value, not a rep-entered one on a context that tracks node status; the first-failed rule's message is kept,
    so a flipped branch can report the other rule; which case this was isn't established; see
    [constraint-models → a choice that switches rules](../constraint-models/quantities-from-attributes.md));
  - in PCM, the minimum of each component group holding those children lowered to 0, and any of them that was
    required (`IsComponentRequired`) made optional.

  Configure segment 1 and save (that sized every segment), then set the answer to Drop in segment 2's
  configurator and save. The dialog says "Configuration changes will apply to current and all future segments":
  segments 2 and 3 kept only the root and its other children, segment 1 kept every one-time line, and no error log
was written (checked on one org). The 0 minimums raised no group-range warning (in the segment 2 configurator, or headless with
  Drop, with and without defaults), and Validate Product Definition reported no errors. A contract value rolled
  up over all segments then counted the one-time children once and matched the source's figure. Switching back to
  Keep, and order, amend and assetization of this shape, weren't measured. That the 0 minimums raised no
  range warning isn't a rule for a minimum of 1. A solver group-range check exists only where the model declares
  instance bounds on the group; a separate bundle validation reports a count mismatch for a group minimum of 1 with 0 lines
  [Platform behaviour, traced]; whether the solver range check fires at a PCM-only group minimum of 1, and the effect on order, amend and assetize, aren't established. The
  solver counts a quantity-N line as 1 with `split = false`, N with `split = true`, and the lines built when
  unset. Whether a PCM minimum reaches the model isn't established (live check) [Platform behaviour, traced in part].
- A **required** child cannot be removed by unticking: its checkbox is disabled in the segment 2 configurator and the line's row
  menu has no delete.
- UI adds of the test bundles failed with `UNKNOWN_EXCEPTION` and no lines written while `IsDefault` was false on their
  `ProductSellingModelOption` rows. Setting `IsDefault = true` on the root and child options together fixed it; which row
  matters was not isolated. Simple products with it false added fine.
- The API recipe ran outside the active CML models because no constraint model references the test products
  (`configurationMethod: Skip` alone does not stop a clone running group rules). Where a model adds products to a
  ramped quote, see the SKILL.md DO NOT on rule-added products.

## What a UI-built bundle ramp carries

Measured 2026-11-11 on fresh 264 `ent-sb0` scratch orgs (two orgs): a configurable bundle with Term Annual, Evergreen
and One-Time children, CML rules on, added with Browse Catalogs → *Current and Subsequent Segments* on a
three-segment Annual ramp.

- **Every child lands in every segment, with ramp identity.** One-Time and Evergreen children too: each segment
  held the same set of products, every line with a `RampIdentifier` (a split, below, adds extra instances).
- **An Evergreen child is one period per segment** (`PricingTermCount` 1 on each segment's line).
- **A One-Time child is quoted once per segment.** Each segment's line is a separate quote line, so the platform
  quote total counts the child N times. A contract value that should count it once must be computed per segment (or the child kept out of later
  segments: rules re-add an unticked rule-sized child, but a root answer can zero it; see [Limiting a one-time child to segment 1](#limiting-a-one-time-child-to-segment-1)).
- **`IsPrimarySegment` was false on every segment** (read on one of the orgs), so it can't single out segment 1; order segments by `StartDate`.
- **The segment's uplift reaches these children too**; see
  [ui-group-ramp.md → What the segment uplift reaches](ui-group-ramp.md#what-the-segment-uplift-reaches).

**A CML-sized default component splits into two instances in the configurator** (one of the orgs). With a child that is
`IsDefaultComponent` (quantity 1) and sized by a rule `relation[T] == <answer>`, the configurator kept the default
instance at 1 and added a second instance for the rest (1 + n−1). Each component group counted both instances and
exceeded its maximum of 1 (a range warning per group), and the two instances priced on different volume bands. Correcting segment 1 in the
configurator to one instance at the rule's quantity fixed segment 1 only: segments 2 and 3 kept the default
instance beside it (n + 1), which broke the rule and was flagged only by the group-range warning. With `IsDefaultComponent` false on the sized children (a required child must be a default, so
it was made optional), each child was one instance at the rule's quantity in every segment, with no warning. The
API path doesn't show this when it sends the child lines itself with `addDefaultConfiguration: false`.

Why: a default component is pre-added at its configured quantity (1 when unset). For a type with no `split`
annotation that line is fixed, so a rule asking for more makes the solver add a separate line for the remainder;
with `split = false` the line's quantity is a variable and the line is reused. Each segment's bundle root is
solved on its own, so, per segment, a `split = false` component gets one line (outside a `Quote` container;
with one, all segments share one solve) [Platform behaviour, traced]. Which
status or quantity the clone gives the segment's lines is set outside the solver and wasn't traced.

The CML fix is `@(split = false)` on each component type a rule sizes: it kept default components as one line at
the rule's quantity in the configurator (2026-11-11; see
[`constraint-models/quantities-from-attributes.md`](../constraint-models/quantities-from-attributes.md)). On the
second org, where every sized component type was `@(split = false)` and the children stayed default components,
the UI ramp held one line per child at the rule's quantity in every segment. Correcting a split segment 1 by hand
wasn't repeated there.

## Cloning a segment that holds a bundle

Measured on the same 264 org (2026-11-06), root and term child on Term Annual, EditGroup then Connect clone
(`lineScope: AllLines`) to three segments:

- A test bundle with a term child and a one-time child (no constraint model references it) cloned with no error.
  Each segment kept the root, term child and one-time child, all stamped.
- A model-referenced bundle (`QB-COMPLETE`, rules run before the clone and a configure call per segment after it)
  cloned with no error. Each segment kept its term children and its one-time default child, all stamped. The shipped
  models have no group-level container, so no group `require` fired in this run.
- Clone copies what segment 1 held, so a default child present before the clone is present in every segment.
- In an earlier quote UI run, a bundle no active model references and one a model references were each added across
  three segments with ramp ids on every line (not cloned).

Clone is not the failure point for these shapes. The persist failures in the matrix below are at amend and cancel,
and were measured on bundles added with `AddProducts`, not on this clone-built shape.

## Assetization shape

| Line | Result |
|---|---|
| Ramped bundle, term child | 1 Asset with N AssetStatePeriods |
| One-time child in N segments, API-built | N separate Assets (1 ASP each, no end date) + N AssetRelationships |
| One-time child in all 3 segments, quote UI-built | 1 Asset with 3 AssetStatePeriods (quantity 1, 2, 3; the last has no end date) |
| One-time child in segment 1 only (either path) | 1 Asset, 1 ASP, no end date |
| Evergreen child in N segments, API-built | N separate Assets, no end date (ASP and relationship counts not checked) |

## Amend and cancel limitation

Connect `assets/actions/amend` fails with `success:false`, `UNKNOWN_EXCEPTION` `PlaceSalesTransactionPersistException`
(`Invalid or missing reference ID @{null.id}`, `MainQuoteLineId`, entity `QuoteLineRelationship`; the `errorCode` string
reports `http=500`, the transport status was not recorded), and the `initiateAmendment` invocable fails with the same
exception, when an **API-built group-ramped bundle has a non-term-defined (one-time or evergreen) bundle child**. It did not
reproduce on bundles built in the quote UI (rows below). Check the response body, not the status. "500" below is
shorthand for this failure. Cancel (Connect) failed the same way on the API-built segment 1-only shape. The other
**500** rows were amend-only.

| Shape | Amend (cancel where noted) |
|---|---|
| Plain bundle (regular group) + one-time child | works |
| Group ramp, term child only | works (+1, -1 per segment, cancel) |
| Group ramp + standalone one-time line (not a bundle child) | works |
| Group ramp + one-time bundle child, **quote UI-built**, child in segment 1 only (optional child unticked in segment 2) | **works** (amend ordered and activated: bundle chain quantity 1, 2, 1, 1) |
| Group ramp + one-time bundle child, **API-built**: segment 1 only (child deleted from segments 2-3 at quote time; cancel also 500), all segments, QSM Proportional | **500** |
| Group ramp + one-time bundle child in all segments, **API-built**, after deleting the child's segment 2-3 ASPs, AssetRelationships and Assets | **500** |
| Group ramp + evergreen bundle child, **API-built** (amend only) | **500** |
| Group ramp + one-time bundle child in all segments, **API-built**, after deleting ALL of the child's ASPs, then AssetRelationships, then Assets (evergreen not tried) | works (amend, cancel, ramped renewal) |
| Group ramp + one-time bundle child in all segments, **quote UI-built**, after deleting only the child's segment 2-3 ASPs | amend inside period 1 fails with a 400 ("Specify Term-Defined as the Product Selling Model on the initial sale asset action source"); amend dated after period 1 and cancel work at quote level |
| Same UI-built shape, after also deleting the child's remaining ASP, AssetRelationship and Asset | works (amend ordered and activated), but no one-time Asset remains and the order no longer matches |

- The same segment 1-only shape amended when built in the quote UI and failed when built by API. The cause of the difference is
  not established.
- A UI-built group ramp bundle whose one-time child sat in all 3 segments amended too at quote level (the control was built in
  the UI with a 100% segment 2-3 discount applied by API, amended at both 2027-06-01 and 2028-06-01). Cancel succeeded at
  quote level on UI-built quotes (not ordered).
- Cause unconfirmed. The error's reference map shows a `NonrampedGroup`, which suggests the amendment builds the child in a
  separate non-ramped group. State it as a limitation, not a root cause.
- Quantity-scale method is not the lever: `AssociatedQuantScaleMethod: Proportional` on the relationship is accepted by Place
  and does not change the outcome.
- The delete workaround is unsupported: the order no longer matches its assets. Offer it only as a customer-flow option
  with that caveat. On a quote UI-built bundle with an optional child, removing the child at quote time is cleaner. On API-built bundles, removing the child at quote time did not avoid the failure; it persisted while any of the one-time child's Assets remained.
- Amend works per segment on a term-only group ramp: +1 / -1 changes only the segment holding the amend date and its remainder.

## Amend date window

On or after the Lifecycle Start Date of **every** asset in the request, and before the Lifecycle End Date of each asset that has
one. One-time and evergreen Assets have no end date, so only the start bound applies to them. On an API-built bundle a one-time child in
later segments starts its own Asset there, so the earliest allowed amend date moves to the last segment's start (inferred from the every-asset rule; an amend at
2027-06-01, before the 2028 and 2029 one-time Asset starts, returned a 400). The upper bound for null-end Assets was not
measured. An asset with a future ramped renewal refused an earlier amend (an ordered plain renewal blocked it the same
way) as measured, and source agrees: an amend or cancel dated before an ordered renewal's start is refused, and on or after
the latest renewal start is allowed (subject to the org's pending-operation limit). A ramped asset refuses an amend dated
before any later change even where earlier-dated amends are otherwise allowed [Platform behaviour, traced].

## Renewal

- A plain Connect `renew` of a bundle with a one-time child worked (API-built; evergreen child and UI-built renewal not tested).
- **Early ramped renewal** needs a start date inside the asset lifecycle, and the platform rejects it for a group-ramped bundle
  containing evergreen or one-time products ("You can't do an early renewal of a group ramped bundle containing evergreen or
  one-time products..."). A plain renew of a ramped asset early is refused; the platform message points to turning on "Create a Ramp Schedule" when setting the renewal terms.
- `rampOptionsDetails {segmentType, durationInMonths}`: `durationInMonths` is the **total** ramp duration (12 gave one
  segment on a 24-month span; use 24 for two yearly segments).
- Dates for `initiateRenewal` use `yyyy-MM-dd'T'HH:mm:ss` (a bare date is `INVALID_DATE_FORMAT`).
- The as-is renewal setting never applies to a ramped asset or line (or a derived-price product); those renewals are
  repriced as ordinary lines [Platform behaviour, traced].
- Ordering a ramped renewal of a term-only ramped asset extends the same asset and its ASP chain in place.

## Lifecycle prerequisites

- Before `Status = Activated`, copy the account's Billing and Shipping address and a `BillToContactId` onto the order,
  matching what backdated-change orders need (see
  `.cursor/skills/rlm-business-apis/backdated-asset-lifecycle.md`).
- An evergreen line needs `PeriodBoundary: Anniversary` (without it the order fails: "Evergreen order products must have an
  Anniversary period boundary") and a billing treatment.
- Use **Quote** output for these recipes. `outputRecordType: Order` failed on the test org with *"We couldn't fetch the data
  for RLM_SalesTransactionContext context definition"* for every action, ramps or not (not diagnosed on that org). Two causes are known since: a stock procedure tag
  with a Quote-lens row and no Order-lens row, and a custom attribute mapped on the Quote lens only (see
  `.cursor/skills/troubleshooting/SKILL.md` → Place on an Order fails).

## `Product2.CanRamp`

Line-ramp flag only; group ramps need none. On the test org it describes as `createable=false, updateable=false` and direct
writes were refused through REST, `sf data update record`, Bulk API and Apex, so a line-ramped bundle's amend could not be
tested by flipping it. The four QB simple products that carry it true came from the qb-pcm plan (its Product2 CSV has a
`CanRamp` column); how that load sets it was not re-verified.

## Runbook: group-ramped bundle with a one-time or evergreen child

Measured on one 264 scratch org: API build path, plus amend and cancel on quote UI-built bundles. Run it on a disposable org. Check each response body, not the status.
This runbook builds the API (unstamped) shape. Steps 4, 6, 7 and 9 differ on a quote UI-built bundle (see "Limiting a one-time child to segment 1", the matrix and Assetization shape); renewal of a UI-built bundle was not measured.

1. **Create the quote and an empty first-year group.** `placeSalesTransaction` create: Quote with `CurrencyIsoCode` set
   to the account currency, plus one empty `QuoteLineGroup`. Poll `Quote.CalculationStatus` to settled.
2. **Ramp the group.** `groupRampAction: EditGroup` with `IsRamped` and `SegmentType` Yearly. Clone the last segment's
   group until there are N segments (Connect clone, one group per call). Poll between calls. In the default
   multi-schedule mode, EditGroup and clone create only the segments. Create the `RampScheduleGroup` parent through
   Place, read back its Id, and parent the segments to it before adding products. Without the parent, order activation
   fails with "Specify a ramp schedule group for ramp segment" (see SKILL.md, the group-ramp build sequence).
3. **Add the bundle to each segment.** `AddProducts` with the root bundle line, the term child line, the one-time or
   evergreen child line in each segment group, and a `QuoteLineRelationship` per child (with
   `AssociatedQuoteLinePricing`). `groupIds` were not needed. For an evergreen child, set `PeriodBoundary: Anniversary`
   on its line now; without it the order cannot be created. Set a billing treatment too.
4. **Optional: remove the child from later segments (API-built).** `DeleteProducts` of the one-time child's lines in the segments
   you do not want it in. The root and term child stay stamped.
5. **Order and activate.** `createOrdersFromQuote` with the quote id. Find the order by its `QuoteId`. Copy the account's
   Billing and Shipping address and a contact onto the order as `BillToContactId`, then set `Status` Activated.
6. **Lifecycle action.** Connect `assets/actions/amend` with `assetIds`, `amendmentStartDate`, `quantityChange`,
   `outputRecordType: Quote`. Connect `cancel` with `cancellationDate`. Connect `renew` with `renewalStartDate`.
   Use Quote output for every recipe. On the test org, Order output failed for every action with a
   `RLM_SalesTransactionContext` fetch error.
   - Amend (API-built): if the child was left in every segment, pick a date on or after the last segment's one-time Asset start.
     Earlier dates fail with a 400 date-window error, which is not the persist failure in step 7. (Inferred for cancel;
     not measured.)
   - Amend (UI-built): the child is one Asset from segment 1. An amend inside period 1 succeeded at quote level with the
     child in all segments, on a bundle whose segment 2-3 discount was applied by API (not ordered; see the matrix bullets).
7. **Expect the persist failure when a one-time or evergreen child is present (API-built).** Amend and cancel both return
   `success:false` with `PlaceSalesTransactionPersistException` (cancel was tested on the one-time, segment-1-only
   shape). Judge by `success:false` in the body, not the HTTP status. For a one-time child, the failure
   went away only after all of the child's assets were deleted (an unsupported workaround; see the matrix and the delete
   bullet above). Evergreen was not tested with that recovery.
8. **Renewal.** Expect an early ramped renewal (`initiateRenewal` with `rampOptionsDetails`) of this bundle to be rejected
   by the platform. A plain Connect `renew` starting after the asset's end date worked with a one-time child present
   (evergreen not tested). A renew before the end of a ramped asset is refused. Ramped renewal was only shown to work on
   term-only bundles, or after the child's assets are deleted (an unsupported workaround). For a ramped renewal,
   `rampOptionsDetails` takes `segmentType` and `durationInMonths`, where the duration is the total ramp length, and
   dates use `yyyy-MM-dd'T'HH:mm:ss`.
9. **Verify (API-built).** For the bundle asset, check Assets per child: the term child gives one Asset with one AssetStatePeriod per
   segment. A one-time child that was left in N segments gives N Assets with one period each and no end date. Count
   AssetRelationships to the bundle: one for the term child, plus one per child Asset. Check that each order line's
   dates match a segment.
