# Demo Data Generator — example scenario configs

Ready-to-run `--config` files for common demo-data shapes. Each is a small,
commented YAML you can run as-is or copy and tweak.

```bash
python -m scripts.demo_data.generate --org <sf-alias> \
    --config scripts/demo_data/scenarios/01-smoke-test.yaml [--dry-run]
```

Always `--dry-run` first — it resolves auth + discovery and prints the plan
(account, product, stages, any auto-caps) **without writing anything**.

> `<sf-alias>` is an **sf** CLI alias (e.g. `rlm-base__jun17_1`), not a CCI alias.

## The examples

| File | Stage | Volume | What it's for |
|------|-------|--------|----------------|
| `01-smoke-test.yaml` | `post` | 1 | Fastest end-to-end proof: one full chain to a Posted invoice. **Run this first** on a new org. |
| `02-pipeline-quotes.yaml` | `quote` | 40 | Opportunities + quotes only (no billing). Cheap, fast pipeline data; works on any account. |
| `03-activated-orders.yaml` | `activate` | 15 | Activated orders → Assets + BillingSchedules, but not invoiced. Installed-base / asset demos. |
| `04-draft-invoices.yaml` | `invoice` | 10 | Draft (unposted) invoices — demo the review/approval step; Draft invoices are deletable. |
| `05-posted-invoices-volume.yaml` | `post` | 50 | Bulk billed invoices. The heavy one — run with `--concurrency`. |
| `06-mixed-stages.yaml` | mixed | 55 | A realistic spread: lots of pipeline, fewer activated, fewest billed. "Lived-in" org. |
| `07-multi-account.yaml` | `post`/capped | 30 | Billable + pipeline-only accounts; shows the auto-cap (Global Media → `activate`). |
| `08-product-mix.yaml` | `post` | 30 | Posted invoices across several SKUs so invoices aren't all one line item. |
| `09-quantity-spread.yaml` | `post` | 35 | Same product, varied quantities → a range of invoice amounts (small/medium/large deals). |
| `10-randomized-discounts.yaml` | `post` | 35 | Per-line discounts drawn from a range → a spread of discounted invoice amounts. |
| `11-randomized-product-mix.yaml` | `post` | 25 | A product **pool** placed as a random non-empty subset → varied multi-line invoices (1–N lines, mixed SKUs, per-line qty + discount ranges). |

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
|-------|------|---------|---------|
| `account` | string | auto | Account **Name** (not id). Omit → first billing-ready account discovered. A pinned account need not be billing-ready (it caps at `activate`). |
| `target_stage` | enum | `post` | How far to run: `opportunity` \| `quote` \| `order` \| `activate` \| `invoice` \| `post`. Hierarchical — each stage runs all stages before it. |
| `with_opportunity` | bool | `false` | Prepend an Opportunity the quote links to. (`target_stage: opportunity` implies one even if this is false.) |
| `opportunity_stage` | string | first open | Pin the Opportunity `StageName`. Must be a valid **open** stage in the org or the run errors with the valid list. |
| `product` | string | auto (QB-preferred) | Product **SKU** for a single-product pool. Shorthand for a one-entry `products:` list. |
| `products` | list | — | The line **pool**: a list of `{sku, quantity?, discount?}` entries. Each transaction places a **random non-empty subset** of the pool as **multiple** quote lines (a 3-entry pool yields 1–3 lines; if the dice exclude everything, one entry is forced so every quote has ≥1 line). Per-entry `quantity`/`discount` override the scenario-level values for that entry. |
| `quantity` | int ≥ 1, or `[min, max]` | `1` | Line quantity. A scalar fixes it; a `[min, max]` range draws an integer **per line** (so a pool/`count > 1` yields a spread). A `products[].quantity` overrides this for that entry. |
| `count` | int ≥ 1 | `1` | How many times to run this shape. |
| `discount` | number or `[min, max]` | none | Line-discount **percent** (0..100). A scalar (`10`) fixes it; a range draws a value **per line** (so `count > 1` yields a spread). May sit on the scenario or on a `products[]` entry (per-product wins, like `quantity`). |

### `defaults` vs `volume` vs `scenarios`

- **`scenarios:` present** → each list entry is one shape. `defaults` supplies
  anything an entry omits. `volume` is ignored.
- **No `scenarios:`** → a single shape is built from `defaults` (+ CLI flags),
  and `volume.scenarios` sets its `count` (unless `--count` overrides).

### Precedence (most specific wins)

```
per-scenario field  >  CLI flag  >  config `defaults`  >  built-in default
```

So `--target-stage quote` on the CLI overrides a `defaults.target_stage: post`,
but a scenario that pins `target_stage: post` still wins over the CLI flag.
(`--with-opportunity` is a store_true flag — it can only *enable*; pin
`with_opportunity: false` on a scenario to opt it out.)

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

## What makes an account / product a valid target

Discovery (in [`discovery.py`](../discovery.py)) resolves targets against the
**live org** — there is no fixture to set up beyond having the right records
exist. Requirements, by what you want to reach:

### Accounts

| To reach… | The account needs… | How it's checked |
|-----------|--------------------|-------------------|
| `quote` / `order` / `activate` | just to **exist** (by Name) | `Account WHERE Name = '…'` |
| `invoice` / `post` | a **`BillingAccount`** (`BillingAccount.AccountId` → the Account) | `BillingAccount WHERE AccountId = '…'` |

An account with **no** BillingAccount is auto-capped at `activate` with a
warning — the run doesn't fail. In the QB org, **only Infinitech** is pre-wired
with a BillingAccount; **Global Media** is pipeline-only. To make another account
billable, create a `BillingAccount` (plus the billing setup it implies) for it.

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

## Not handled yet — bundles and usage

These are real limitations, not config you're missing:

- **Bundle products are NOT supported.** A bundle (e.g. `QB-COMPLETE`,
  `QB-BDL-*`) needs its **component lines** sent in the PST graph (child
  QuoteLineItems wired to the parent, plus attribute/selling-model configuration).
  The tool emits only one flat line, so a bundle would either fail to place or
  produce an incomplete/unconfigured quote. **Pin a simple SKU** (`QB-API-FLEX`)
  for now. Adding bundle support means extending `place_sales_transaction` in
  [`lifecycle.py`](../lifecycle.py) to build the component graph.
- **Usage / consumption is NOT supported.** Usage-priced products (the `*-BLNG`
  metered SKUs, token/quantity/monetary **commit** products, etc.) bill from
  **usage feeds / consumption schedules** that this tool does not create. It
  places a term line with start/end dates and lets the billing engine generate a
  schedule — so a usage product would invoice with **no consumption behind it**,
  not realistic usage data. Generating usage records is a separate feature
  (would post `UsageInput`/consumption data after activation).

If you need bundle or usage demo data today, build those quotes through the UI or
a dedicated flow — this generator is for the flat-line Opportunity→…→Invoice
spine at volume.

## See also

- [`../README.md`](../README.md) — CLI flags, exit codes, auth/transport, output.
- [`../config.example.yaml`](../config.example.yaml) — the original worked example.
- [`../../../docs/guides/demo-data-generator.md`](../../../docs/guides/demo-data-generator.md)
  — operational how-to: verification SOQL, cleanup recipes, troubleshooting.
- [`../CONTRACTS.md`](../CONTRACTS.md) — the live-verified lifecycle contracts.
