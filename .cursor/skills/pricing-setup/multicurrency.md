# Multicurrency pricing: the wrong-currency price

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. What to load per currency:
> [`import-export-and-bulk-data.md` → Adding a currency](import-export-and-bulk-data.md#adding-a-currency).
> This repo's currency flows and rate refresh: [`../pricing-wiring/multicurrency-build.md`](../pricing-wiring/multicurrency-build.md).

## Wrong-currency price returned (multicurrency orgs)

A lookup step that does **not** pass `CurrencyIsoCode` does not match on currency [inferred]. What an
omitted required input does was not traced. If the
table has rows for the product in more than one currency, a single-output lookup fails with a
duplicate-value error; with output resolution on, a List Price or Price Tracking step picks the final
row(s) from the candidates by its resolution strategy (for example minimum or maximum price
[Help]) and candidate priority (traced for the procedure lookup path only) [Platform behaviour, traced],
and the chosen row can be another currency's, because the lookup returns every currency's row
[inferred]. A Price
Adjustment Matrix with Stack or Sequence resolution applies every matched row
(see [price-adjustment-matrix.md](../pricing-procedures/elements/price-adjustment-matrix.md))
[Core]; if its Use As List column stays unique with per-currency rows,
every currency's row may apply, which usually gives a visibly wrong
price [inferred, not traced]. A Volume Discount lookup has no output resolution, so several currency rows give the
duplicate-value error [Core]; a Tier Discount lookup returns the overlapping bands and logs
`OVERLAPPING_ADJUSTMENT_TIERS` [Core]. The table shape behind that Tier result is inferred. If the only row is in another
currency, the line prices from it [inferred]. In the resolution-pick and lone-row cases the
symptom is a *plausible* price, not an error.

Where the step does pass `CurrencyIsoCode` (the shipped recipe tables take it as a required
Equals input) and the table has no row for that currency, the lookup returns no match: an
adjustment or tier step leaves the earlier price unchanged, a list-price step sets no list price
(a new line then has none), no error is raised in the traced path, and there is no conversion from the corporate currency [Platform behaviour, traced]. That trace covers the
procedure lookup path only; for a List Price or Price Tracking step with output resolution on,
Help says the line stops instead.

**Fix:** add `CurrencyIsoCode` as an input on **every** lookup step that resolves a
currency-denominated value — list price, adjustment schedule, and adjustment tier
lookups alike. Missing it on the tier step alone still breaks tier pricing: with rows in several currencies, a
duplicate-value error on Volume or overlapping bands logged on Tier; with one row in another
currency, that row's values.

Records created by quick actions and flows default to the **running user's** currency, not the
account's, so currency must also *reach* the record the step filters on: wire currency
inheritance explicitly. The repo's two flows that do it:
[`../pricing-wiring/multicurrency-build.md`](../pricing-wiring/multicurrency-build.md).
