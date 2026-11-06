# Ramped Quotes — Bundles with one-time / evergreen children, and their lifecycle

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. Measured 2026-11-05 on one 264 scratch org
> (USA796, Enterprise, API 68.0), API only, **Quote** output. Not run through the configurator UI.
> Treat each row as a measurement, not a root cause. Re-verify on the target org.

## Limiting a one-time child to segment 1

A group-ramped term bundle (root + term child + one-time child). Add the bundle to every segment with
`groupRampAction: AddProducts` (one line set per segment group, plus a `QuoteLineRelationship` per child with
`AssociatedQuoteLinePricing`), then `DeleteProducts` the one-time child's lines in segments 2 and 3.

- The root and the term child are stamped with `RampIdentifier`/`SegmentIdentifier`. A **one-time or evergreen child gets
  neither**, so no contiguity check applied to it in the test. A segment 2-only delete of the one-time child was accepted.
- Measured by API only. Whether the UI's *Current and Subsequent Segments* places it the same way, and whether removing it
  in segment 2 through the configurator propagates forward only, is **not verified**.
- The recipe ran outside the active CML models (`configurationMethod: Skip`, test products with no constraint model). The
  CML-active-bundle DO NOT in SKILL.md still applies to catalog bundles.

## Assetization shape

| Line | Result |
|---|---|
| Ramped bundle, term child | 1 Asset with N AssetStatePeriods |
| One-time child in N segments | N separate Assets (1 ASP each, no end date) + N AssetRelationships |
| Evergreen child in N segments | N separate Assets, no end date (ASP and relationship counts not checked) |

## Amend and cancel limitation

Connect `assets/actions/amend` fails with `success:false`, `UNKNOWN_EXCEPTION` `PlaceSalesTransactionPersistException`
(`Invalid or missing reference ID @{null.id}`, `MainQuoteLineId`, entity `QuoteLineRelationship`; the `errorCode` string
reports `http=500`, the transport status was not recorded), and the `initiateAmendment` invocable fails with the same
exception, when a **group-ramped bundle has a non-term-defined (one-time or evergreen) bundle child**. Check the response
body, not the status. "500" below is shorthand for this failure. Cancel (Connect) failed the same way on the
segment 1-only shape. The other **500** rows were amend-only.

| Shape | Amend (cancel where noted) |
|---|---|
| Plain bundle (regular group) + one-time child | works |
| Group ramp, term child only | works (+1, -1 per segment, cancel) |
| Group ramp + standalone one-time line (not a bundle child) | works |
| Group ramp + one-time bundle child: segment 1 only (child deleted from segments 2-3 at quote time; cancel also 500), all segments, QSM Proportional | **500** |
| Group ramp + one-time bundle child in all segments, after deleting the child's segment 2-3 ASPs, AssetRelationships and Assets | **500** |
| Group ramp + evergreen bundle child (amend only) | **500** |
| Group ramp + one-time bundle child in all segments, after deleting ALL of the child's ASPs, then AssetRelationships, then Assets (evergreen not tried) | works (amend, cancel, ramped renewal) |

- Cause unconfirmed. Core lead only: `ARCSalesTransactionContextTransformer` builds its root-by-group map from
  ramp-stamped lines, and the error's reference map shows a `NonrampedGroup`. State it as a limitation, not a root cause.
- Quantity-scale method is not the lever: `AssociatedQuantScaleMethod: Proportional` on the relationship is accepted by Place
  and does not change the outcome.
- The delete workaround is unsupported: the order no longer matches its assets. Offer it only as a customer-flow option
  with that caveat. Removing the child at quote time is cleaner, but the limitation applies while any child asset remains.
- Amend works per segment on a term-only group ramp: +1 / -1 changes only the segment holding the amend date and its remainder.

## Amend date window

On or after the Lifecycle Start Date of **every** asset in the request, and before the Lifecycle End Date of each asset that has
one. One-time and evergreen Assets have no end date (E3, E16), so only the start bound applies to them. A one-time child in
later segments starts its own Asset there, so the earliest allowed amend date moves to the last segment's start (inferred from the every-asset rule; E7 measured a 400
for an amend at 2027-06-01, before the 2028 and 2029 one-time Asset starts). The upper bound for null-end Assets was not
measured. An asset with a future ramped renewal refuses an earlier amend (an ordered plain renewal blocks it the same way).

## Renewal

- A plain Connect `renew` of a bundle with a one-time child works (evergreen child not tested).
- **Early ramped renewal** needs a start date inside the asset lifecycle, and the platform rejects it for a group-ramped bundle
  containing evergreen or one-time products ("You can't do an early renewal of a group ramped bundle containing evergreen or
  one-time products..."). A plain renew of a ramped asset early is refused; the platform message points to turning on "Create a Ramp Schedule" when setting the renewal terms.
- `rampOptionsDetails {segmentType, durationInMonths}`: `durationInMonths` is the **total** ramp duration (12 gave one
  segment on a 24-month span; use 24 for two yearly segments).
- Dates for `initiateRenewal` use `yyyy-MM-dd'T'HH:mm:ss` (a bare date is `INVALID_DATE_FORMAT`).
- Ordering a ramped renewal of a term-only ramped asset extends the same asset and its ASP chain in place.

## Lifecycle prerequisites

- Before `Status = Activated`, copy the account's Billing and Shipping address and a `BillToContactId` onto the order,
  matching what backdated-change orders need (see
  `.cursor/skills/rlm-business-apis/backdated-asset-lifecycle.md`).
- An evergreen line needs `PeriodBoundary: Anniversary` (without it the order fails: "Evergreen order products must have an
  Anniversary period boundary") and a billing treatment.
- Use **Quote** output for these recipes. `outputRecordType: Order` failed on the test org with *"We couldn't fetch the data
  for RLM_SalesTransactionContext context definition"* for every action, ramps or not (undiagnosed, org-specific until
  reproduced elsewhere).

## `Product2.CanRamp`

Line-ramp flag only; group ramps need none. On the test org it describes as `createable=false, updateable=false` and direct
writes were refused through REST, `sf data update record`, Bulk API and Apex, so a line-ramped bundle's amend could not be
tested by flipping it. The four QB simple products that carry it true came from the qb-pcm plan (its Product2 CSV has a
`CanRamp` column); how that load sets it was not re-verified.

## Runbook: group-ramped bundle with a one-time or evergreen child

Measured on one 264 scratch org, API only. Run it on a disposable org. Check each response body, not the status.

1. **Create the quote and an empty first-year group.** `placeSalesTransaction` create: Quote (`Status` Draft,
   `CurrencyIsoCode` set to the account currency) plus one empty `QuoteLineGroup`. Poll `Quote.CalculationStatus` to settled.
2. **Ramp the group.** `groupRampAction: EditGroup` with `IsRamped`, `SegmentType` Yearly. Clone the last segment's group
   until there are N segments (Connect clone, one group per call). Poll between calls.
3. **Add the bundle to each segment.** One `AddProducts` call per segment group, or one call for all segments, with the
   root bundle line, the term child line, the one-time or evergreen child line, and a `QuoteLineRelationship` per child
   (with `AssociatedQuoteLinePricing`). Do not add `groupIds`.
4. **Optional: remove the child from later segments.** `DeleteProducts` of the one-time child's lines in the segments
   you do not want it in. The root and term child stay stamped.
5. **Order and activate.** `createOrdersFromQuote` with the quote id. Find the order by its `QuoteId`. Copy the account's
   Billing and Shipping address and a contact onto the order as `BillToContactId`, then set `Status` Activated.
   Evergreen lines also need `PeriodBoundary: Anniversary` and a billing treatment.
6. **Lifecycle action.** Connect `assets/actions/amend` with `assetIds`, `amendmentStartDate`, `quantityChange`,
   `outputRecordType: Quote`. Connect `cancel` with `cancellationDate`. Connect `renew` with `renewalStartDate`.
   Use Quote output for every recipe. On the test org, Order output failed for every action with a
   `RLM_SalesTransactionContext` fetch error.
7. **Expect the amend failure when a one-time or evergreen child is present.** The body comes back `success:false` with
   `PlaceSalesTransactionPersistException`. Record it as the result; do not retry on a different status code.
8. **Ramped renewal.** `initiateRenewal` with `renewAssetIds`, `renewOutputType`, `renewStartDate`, `renewEndDate`
   (dates as `yyyy-MM-dd'T'HH:mm:ss`), and `rampOptionsDetails` `{segmentType: Yearly, durationInMonths}`. The duration
   is the total ramp length. Early ramped renewal of a bundle with a one-time or evergreen child is rejected by the platform.
9. **Verify.** For the bundle asset, count Assets per child: one Asset with N AssetStatePeriods for the term child; for
   the one-time child, one Asset per segment with one period each and no end date. Count AssetRelationships to the
   bundle. Check that the order lines match the segments.
