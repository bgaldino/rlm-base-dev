# Transaction Data Harness — example scenario configs

Ready-to-run `--config` files for common demo-data shapes. Each is a small,
commented YAML you can run as-is or copy and tweak.

```bash
python -m scripts.txn_data_harness.generate --org <sf-alias> \
    --config scripts/txn_data_harness/scenarios/01-smoke-test.yaml [--dry-run]
```

Always `--dry-run` first — it resolves auth + discovery and prints the plan
(account, product, stages, any auto-caps) **without writing anything**.

> `<sf-alias>` is an **sf** CLI alias or username, not a CCI alias.

## The examples

| File | Stage | Volume | What it's for |
| ---- | ----- | ------ | -------------- |
| `01-smoke-test.yaml` | `post` | 1 | Fastest end-to-end proof: one full chain to a Posted invoice. **Run this first** on a new org. |
| `02-pipeline-quotes.yaml` | `quote` | 40 | Opportunities + quotes only (no billing). Cheap, fast pipeline data; works on any account. |
| `03-activated-orders.yaml` | `activate` | 15 | Activated orders → Assets + BillingSchedules, but not invoiced. Installed-base / asset demos. |
| `04-draft-invoices.yaml` | `invoice` | 10 | Draft (unposted) invoices — demo the review/approval step; Draft invoices are deletable. |
| `05-posted-invoices-volume.yaml` | `post` | 50 | Bulk billed invoices. The heavy one — run with `--concurrency`. |
| `06-mixed-stages.yaml` | mixed | 55 | A realistic spread: lots of pipeline, fewer activated, fewest billed. "Lived-in" org. |
| `07-multi-account.yaml` | `post`/capped | 30 | Billable + pipeline-only accounts; shows the auto-cap to `order` for accounts without `BillingAccount`. |
| `08-product-mix.yaml` | `post` | 30 | Posted invoices across several SKUs so invoices aren't all one line item. |
| `09-quantity-spread.yaml` | `post` | 35 | Same product, varied quantities → a range of invoice amounts (small/medium/large deals). |
| `10-randomized-discounts.yaml` | `post` | 35 | Per-line discounts drawn from a range → a spread of discounted invoice amounts. |
| `11-randomized-product-mix.yaml` | `post` | 25 | A product **pool** placed as a random non-empty subset → varied multi-line invoices (1–N lines, mixed SKUs, per-line qty + discount ranges). |
| `12-usage-consumption.yaml` | `usage` | 5 | Usage-based products (`QB-DB`, `QB-TOKENS-PACK`) with `TransactionJournal` consumption rows against each activated asset. Stops at `usage`; kick off org-wide rating separately. |
| `13-multi-year-terms.yaml` | `post` | 5 | Multi-year and non-month subscription cadences: 1-Annual, 3-Annual, bare-int (count-only) form, PSM-default fallback, and mixed terms on one quote. Exercises the per-line `(count, unit)` term model. |
| `14-end-date-overrides.yaml` | `post` | 5 | Explicit `EndDate` override examples for co-terming and off-cycle spans: absolute anchors, day/month/quarter/year offsets, per-line overrides, and mixed cadence quotes. |
| `15-standalone-billing-draft.yaml` | `invoice` (ingest) | 5 | **Standalone billing path** — `kind: invoice_ingestion`. Skips the PST chain entirely; each transaction is a single typed Composite-Graph `POST` to `/commerce/invoicing/.../actions/ingest` that creates a **Draft** invoice (`CreationMode = External`) directly. Targets a billing-ready account (Infinitech) and a pipeline-only account (Global Media) to exercise the no-BillingAccount path. Phase 1 invariant: every line stays `taxable: false`. Live-verified on R262 — see [`../CONTRACTS.md`](../CONTRACTS.md) → *Invoice Ingestion*. Draft ingested invoices are deletable. |
| `15-standalone-billing.yaml` | `post` (ingest) | 5 | **Phase 2 — deferred.** Same ingest path as the Draft scenario above, but `target_stage: post`. The Posted code paths are in place, but live verification is blocked: the ingest API rejects Posted invoices whose lines reference a taxable `TaxTreatment` unless an `InvoiceLineTax` graph record accompanies each line, and the QB org currently exposes only taxable treatments. Don't run this scenario until either a non-taxable `TaxTreatment` is seeded or the `InvoiceLineTax` graph payload lands. See [`../FOLLOWUPS.md`](../FOLLOWUPS.md) → *Standalone-billing ingestion (Phase 2)*. |

These are tuned for the **QuantumBit (QB)** demo org. The only values that are
org-specific are the **account names** (`Infinitech`, `Global Media`) and the
**product SKUs** (`QB-…`). Change those for a different org — everything else
(pricebook, legal entity, opportunity stage) is auto-discovered.

## Scenario schema

A config file has up to three top-level keys, **all optional**:

```yaml
defaults:     # broad settings applied to every scenario (a mapping)
volume:       # used ONLY when there is no `scenarios:` block
scenarios:    # an explicit list of shapes; each entry runs `count` times
```

### Per-scenario fields (and `defaults`)

Every field below is valid in a `scenarios:` entry **and** in the `defaults`
block (where it applies to all scenarios unless the scenario overrides it).

| Field | Type | Default | Meaning |
| ----- | ---- | ------- | ------- |
| `kind` | enum | `sales_transaction` | Scenario handler. Use `sales_transaction` for the PST lifecycle, or `invoice_ingestion` for standalone-billing Draft invoice ingestion. `transaction` is not an alias. |
| `account` | string | auto | Account **Name** (not id). Omit → first billing-ready account discovered. A pinned account need not be billing-ready (it caps at `order`). |
| `target_stage` | enum | `post` | How far to run: `opportunity` \| `quote` \| `order` \| `activate` \| `usage` \| `invoice` \| `post`. Hierarchical — each stage runs all stages before it. `usage` writes TransactionJournals for any line that declares a `usage:` block (skipped silently otherwise); see [Usage-based products](#usage-based-products) below. |
| `with_opportunity` | bool | `false` | Prepend an Opportunity the quote links to. (`target_stage: opportunity` implies one even if this is false.) |
| `opportunity_stage` | string | first open | Pin the Opportunity `StageName`. Must be a valid **open** stage in the org or the run errors with the valid list. |
| `product` | string | auto (QB-preferred) | Product **SKU** for a single-product pool. Shorthand for a one-entry `products:` list. |
| `products` | list | — | The line **pool**: a list of `{sku, quantity?, discount?}` entries. Each transaction places a **random non-empty subset** of the pool as **multiple** quote lines (a 3-entry pool yields 1–3 lines; if the dice exclude everything, one entry is forced so every quote has ≥1 line). Per-entry `quantity`/`discount` override the scenario-level values for that entry. |
| `quantity` | int ≥ 1, or `[min, max]` | `1` | Line quantity. A scalar fixes it; a `[min, max]` range draws an integer **per line** (so a pool/`count > 1` yields a spread). A `products[].quantity` overrides this for that entry. |
| `count` | int ≥ 1 | `1` | How many times to run this shape. |
| `discount` | number or `[min, max]` | none | Line-discount **percent** (0..100). A scalar (`10`) fixes it; a range draws a value **per line** (so `count > 1` yields a spread). May sit on the scenario or on a `products[]` entry (per-product wins, like `quantity`). |
| `start_date` | date / range / window | today | The quote line **StartDate** (the platform anchors the line's `EndDate` off this + the term). One date is drawn **per transaction** and applied to all of that quote's lines, so a range spreads quotes over time. Forms: exact (`"2026-03-15"`, `today`, `"+30"`/`"-15"` relative days); range list `["2026-01-01", "+90"]` or map `{from:…, to:…}`; window `{around: <anchor>, plus_or_minus: N}` (anchor ± N days, anchor defaults to today). |
| `term` | int, or `{count, unit}` | PSM default → `{12, Months}` | Subscription cadence for **TermDefined** lines only. Drives `QuoteLineItem.SubscriptionTerm` / `SubscriptionTermUnit`; the platform derives `EndDate` from those + `StartDate`. A bare int (`term: 36`) overrides count only — unit follows the resolved PSM. A map (`{count: 3, unit: Annual}`) sets both; `unit` must match the resolved PSM's `PricingTermUnit`. Picklist: `Months`, `Quarterly`, `Semi-Annual`, `Annual`. Alias: `Years -> Annual`. Range 1–120. Rejected on `Evergreen` / `OneTime` products. Falls back through line → scenario → `ProductSellingModel.PricingTerm` → `(12, Months)`. May sit on the scenario (default for all lines) or on a `products[]` entry (per-line wins). |
| `end_date` | ISO date, int (days), or `"<n><unit>"` | unset (platform derives) | **Optional** explicit `EndDate` override for **TermDefined** lines only. Requires an accompanying `term:` — a cadence is still needed for `SubscriptionTerm` / billing-schedule derivation. Forms: absolute (`"2027-01-14"` or a YAML date), bare int = days (`364`), suffixed offset (`"364d"`, `"12mo"`, `"3q"`, `"1y"`). Supported units: `d` (days), `mo` (calendar months, day-clamped), `q` (3 months), `y` (12 months). Bare `"m"` is **rejected** as ambiguous. Forward-only (zero/negative reject). Range 1d–20y. The override is resolved against the line's drawn `StartDate` at place time, so a scenario-level `end_date:` co-terms every line on the quote to the same calendar anchor. The platform honors the explicit date and prorates `PricingTermCount` against the actual span (~0.27% drift vs the derived 365/366-day default). |
| `selling_model` | string | auto | Pin the `ProductSellingModel.Name` for SKUs that have **multiple** active PBEs (e.g. one Annual + one Quarterly). Required only when a SKU is ambiguous; the resolver errors with the candidate list otherwise. Omit when the SKU has a single active PBE on the standard pricebook (the common case). |

### `defaults` vs `volume` vs `scenarios`

- **`scenarios:` present** → each list entry is one shape. `defaults` supplies
  anything an entry omits. `volume` is ignored.
- **No `scenarios:`** → a single shape is built from `defaults` (+ CLI flags),
  and `volume.scenarios` sets its `count` (unless `--count` overrides).

### Precedence (most specific wins)

```text
per-scenario field  >  CLI flag  >  config `defaults`  >  built-in default
```

So `--target-stage quote` on the CLI overrides a `defaults.target_stage: post`,
but a scenario that pins `target_stage: post` still wins over the CLI flag.
(`--with-opportunity` is a store_true flag — it can only *enable*; pin
`with_opportunity: false` on a scenario to opt it out.)

**Common gotcha — `--count` and per-scenario `count:`.** Passing `--count 1` to
smoke-test a config whose scenarios pin `count: 100` does **not** shrink the run:
the per-scenario value wins. To smoke a multi-scenario config, edit the
per-scenario `count:` (or temporarily comment out scenarios) rather than passing
`--count`. `--count` only takes effect when no `--config` is given, or against a
config whose `count` lives in `defaults:` (not on a scenario).

This table is the same contract enforced in
[`config.py`](../config.py) (`_coerce_spec` / `load_scenarios`).

### Discounts

`discount` sets the QuoteLineItem `Discount` percent on the placed line. Because
PST prices with `pricingPref: "System"`, the engine **applies** it to the derived
net prices and it flows through to the **posted invoice** — live-verified: a 25%
discount drove a $450 line to a `NetUnitPrice` of 337.50 and a Posted invoice
`TotalAmount` to match (see [`../CONTRACTS.md`](../CONTRACTS.md) → *Line discounts*).

⚠️ **Verify a discount by the net price, not the `Discount` field.** The engine
consumes the input but reads `QuoteLineItem.Discount` back as `0` post-place — the
discount lives in `NetUnitPrice`/`NetTotalPrice` (and `Invoice.TotalAmount` /
`InvoiceLine.ChargeAmount`), not that column.

### Subscription terms

For TermDefined products, `term` is the **author input** that drives the line's
cadence — it writes `QuoteLineItem.SubscriptionTerm` + `SubscriptionTermUnit`
and the **platform** derives `EndDate` from `StartDate` + those two fields
(inclusive `start + term - 1 day` — e.g. a 1×Annual line starting 2026-01-15
ends 2027-01-14). `PricingTerm` / `PricingTermCount` are **auto-calculated**
by the platform from these inputs and the PBE; the harness writes none of
them.

```yaml
# 3-year deal -- explicit (count, unit). Unit must match the PSM bound to
# the PBE (i.e. the SKU must actually be sold under an Annual selling model;
# pin selling_model: if the SKU has more than one).
- sku: QB-LIC-CLOUD
  term: {count: 3, unit: Annual}

# 4-quarter deal on a Quarterly SOM.
- sku: QB-LIC-QTR
  term: {count: 4, unit: Quarterly}

# Bare int -- count only. The harness fills in the unit from the resolved
# PSM ("give me 24 of whatever this product is measured in").
- sku: QB-API-FLEX
  term: 24

# No `term` -- harness uses the PSM's discovered PricingTerm / PricingTermUnit
# (and falls back to (12, Months) if the PSM declares none).
- sku: QB-API-FLEX
```

Rules:

- **Unit must match the PSM.** An explicit `term.unit` that disagrees with the
  resolved `ProductSellingModel.PricingTermUnit` raises `ConfigError`. Pin a
  matching `selling_model:` instead — the harness will not implicitly switch
  PBEs.
- **`Years` alias.** `unit: Years` is accepted and mapped to `Annual`. Other
  unit names (e.g. `Days`) are rejected.
- **Bounds.** `1 <= count <= 120`. The cap catches typos like `360`.
- **Evergreen / OneTime products reject `term`** at config-load time —
  `createOrderFromQuote` rejects `EndDate` (and `SubscriptionTerm`) on those
  selling models. Omit the key entirely; the line places without a term.
- **Multi-PBE SKUs.** If a SKU has more than one active PBE on the standard
  pricebook, the resolver fails fast with the candidate `ProductSellingModel`
  names — set `selling_model:` to disambiguate.

See [`13-multi-year-terms.yaml`](13-multi-year-terms.yaml) for a worked example
covering the bare-int form, an explicit Annual cadence, PSM-default fallback,
and a mixed-term quote.

### Explicit `EndDate` overrides (co-terming)

When you want a specific calendar `EndDate` — for co-terming a multi-line
quote to the same anchor, or for off-cycle ramp deals — pin `end_date:`
alongside `term:`. The platform honors the explicit date and prorates
`PricingTermCount` against the actual span (a 366-day span on a 1×Annual
line yields `PricingTermCount = 1.0027` vs the derived 1.0; accepted drift).

```yaml
# Absolute calendar anchor at scenario level -- every TermDefined line on
# the quote co-terms to 2027-01-14 regardless of cadence.
scenarios:
  - end_date: "2027-01-14"
    term: {count: 1, unit: Annual}
    products:
      - sku: QB-LIC-CLOUD
      - sku: QB-API-FLEX

# Per-line relative offsets. Units: d / mo / q / y.
- sku: QB-API-FLEX
  term: 12
  end_date: "12mo"     # 12 calendar months from StartDate (day-clamped)

- sku: QB-LIC-CLOUD
  term: {count: 1, unit: Annual}
  end_date: "1y"       # equivalent to 12mo

- sku: QB-LIC-QTR
  term: {count: 4, unit: Quarterly}
  end_date: "3q"       # 9 calendar months from StartDate

- sku: QB-API-FLEX
  term: 12
  end_date: 364        # bare int -> days. Lands on platform's inclusive
                       # convention (start + 364 days for a "1-year" line).
```

Rules:

- **Requires a `term:`** — line, scenario, or PSM. `end_date` without a
  cadence raises `ConfigError` (`SubscriptionTerm` is still needed for
  billing-schedule derivation, and silently falling through to
  `Term(12, Months)` would be surprising).
- **TermDefined only.** `Evergreen` / `OneTime` products reject `EndDate`
  at place time; the harness fails fast at resolve time instead.
- **Forward-only.** Zero and negative offsets are rejected.
- **`m` is ambiguous** between months/minutes/meters; spell it `mo`.
  Other unit suffixes (`w`, `h`, …) are rejected.
- **Day clamp on months.** Jan 31 + `1mo` lands on Feb 28 (or 29 in a
  leap year); Aug 31 + `1mo` lands on Sep 30.
- **Line wins over scenario.** A scenario-level `end_date:` is co-term
  shorthand; any line that pins its own overrides for just that line.
- **`EndDate` wins the pricing math.** When `end_date:` is set, the
  platform computes `PricingTermCount` as `(EndDate − StartDate) / 365`
  days — *not* from `SubscriptionTerm`. If you pin `term: {count: 2,
  unit: Annual}` and an `end_date` only one year out, the line is
  billed for one year and `SubscriptionTerm` is stored verbatim as 2
  (no cross-validation). Author both fields consistently if you want
  them to agree. See `../CONTRACTS.md` → *Probed edge cases* for the live
  evidence behind this rule.
- **`EndDate` carries through to `BillingSchedule.TotalAmount`.**
  Activation emits **one** `BillingSchedule` row per `OrderItem`
  spanning the full deal — it is **not** fanned out into per-period
  rows at activation. Periodic invoicing advances `NextBillingDate`
  lazily as invoices post. `BillingTerm` is the period length
  (always `1`, with `BillingTermUnit` taking the PSM cadence —
  `Year` for Annual, `Month` for Monthly), and `TotalAmount` is
  prorated against the actual `(EndDate − StartDate)` span using
  the same 365-day math as `PricingTermCount`. `Quantity`
  multiplies `BillingPeriodAmount`, not `UnitPrice`. **Caveat for
  Monthly SOMs:** short spans (28- and 30-day) both billed
  `1548.39` against `BillingPeriodAmount = 1500` — Monthly
  proration appears to use an internal day denominator (~30.97),
  not calendar days. See `../CONTRACTS.md` →
  *BillingSchedule fan-out across `end_date` scenarios*.

## What makes an account / product a valid target

Discovery (in [`discovery.py`](../discovery.py)) resolves targets against the
**live org** — there is no fixture to set up beyond having the right records
exist. Requirements, by what you want to reach:

### Accounts

| To reach… | The account needs… | How it's checked |
| --------- | ------------------ | ----------------- |
| `quote` / `order` | just to **exist** (by Name) | `Account WHERE Name = '…'` |
| `activate` / `invoice` / `post` | a **`BillingAccount`** (`BillingAccount.AccountId` → the Account) | `BillingAccount WHERE AccountId = '…'` |

An account with **no** BillingAccount still runs `quote → order`, then is
auto-capped at `order` with a warning — the run doesn't fail. (Activation
generates BillingSchedules/Assets, which need the account's billing setup.) The
bundled QB examples use **Infinitech** as the billing-ready account and **Global
Media** as the pipeline-only account. To make another account billable, create a
`BillingAccount` (plus the billing setup it implies) for it.

### Products

A product is a valid target when it has an **active `PricebookEntry` on the
standard pricebook** and an **active `Product2`**:

```sql
SELECT Id FROM PricebookEntry
WHERE Pricebook2.IsStandard = true AND IsActive = true
  AND Product2.IsActive = true AND Product2.StockKeepingUnit = '<SKU>'
```

If you pin a SKU with no such PBE, the run errors clearly (exit 3).

> ⚠️ **A clean PricebookEntry is necessary but not sufficient for every product.**
> The tool places one or more **flat lines** (each Product2 + PBE + Quantity +
> dates + optional Discount) — multiple lines per quote when a `products:` pool is
> given, but every line is still flat. Simple term/one-time/evergreen products like
> **`QB-API-FLEX`** and **`QB-API`** place cleanly (the line's `EndDate` is set only
> for **term-defined** selling models — evergreen/one-time reject it; see
> [`../CONTRACTS.md`](../CONTRACTS.md) → *Selling models*). Products that require
> component/attribute wiring to configure/price do **not** — see below.

## Bundles — default-configured only

Bundles **do work** for SKUs whose components are all defaultable. The harness still
sends a single flat line per `products:` entry, but PST expands the bundle
server-side using its default component graph and returns a fully configured set of
child `QuoteLineItem`s wired to the parent via `ParentQuoteLineItemId`. Activation,
billing schedule generation, invoice draft, and posting all succeed.

Live-verified on a Revenue Cloud R262 scratch org with `QB-COMPLETE` → 5 lines
(1 root Bundle + 4 child Simple) on the quote, the resulting order activated,
and the invoice posted at $91,000.

Caveats:

- **Configuration is whatever the bundle defaults to.** You cannot influence
  attribute values, selling-model choices on child slots, or component selection
  from the YAML. `quantity:` and `discount_percent:` apply to the **root line**
  only; child quantities/prices come from the bundle definition.
- **Bundles whose components require user choice** (mandatory attributes with no
  default, or required slots with multiple optional components) will likely fail
  to place. Only default-configured bundles like `QB-COMPLETE` are confirmed.

## Usage-based products

Usage SKUs (`QB-DB`, `QB-TOKENS-PACK`, the token/quantity/monetary commit
products, etc.) are opted in per-line by adding a `usage:` block to a product
entry. After activation, the new `usage` stage writes
`TransactionJournal` consumption rows against the line's asset, one set per
`ProductUsageResource` binding the product carries (so `QB-DB` writes rows for
both `UR-DATASTORAGE` and `UR-CPUTIME` by default).

```yaml
products:
  - sku: QB-DB
    quantity: 1
    usage:
      quantity: [100, 500]      # per-row quantity (scalar or [min, max])
      records_per_line: [5, 10] # journals per binding, per asset
      days_back: 30             # spread ActivityDate across N days back
      resource: UR-CPUTIME      # optional UsageResource.Code; omit for all bindings
      unit_of_measure: hr       # optional UoM.UnitCode; requires explicit resource
```

Every TJ row is tagged with a deterministic
`UniqueIdentifier = txn-harness-<run_id>-<asset_id>-<target_idx>-<row_idx>`,
so a retried run dedupes against rows the prior attempt already wrote.

The rating/billing job that turns these into `UsageSummary` / liable-summary
records runs across **every** usage product in the org and takes ~15 minutes,
so the harness exposes it as a one-shot top-level command instead of a
per-scenario stage:

```bash
python -m scripts.txn_data_harness.cli rate --org <sf-alias>
```

Run rating once after the batch of `usage`-stage scenarios completes; the
example config above is at `scenarios/12-usage-consumption.yaml`.

### Not handled yet — verifying rated output

Tooling for confirming the rating job *finished* (polling
`AsyncOperationTracker` for the orchestration flow, checking
`UsageSummary.Status`) is not in scope; the `rate` subcommand fires the flow
and exits. Monitor progress in **Setup → Monitor Workflow Services**, then
verify rated output by SOQL (see the harness guide).

## See also

- [`../README.md`](../README.md) — CLI flags, exit codes, auth/transport, output.
- [`../config.example.yaml`](../config.example.yaml) — the original worked example.
- [`../../../docs/guides/txn-data-harness.md`](../../../docs/guides/txn-data-harness.md)
  — operational how-to: verification SOQL, cleanup recipes, troubleshooting.
- [`../CONTRACTS.md`](../CONTRACTS.md) — the live-verified lifecycle contracts.
