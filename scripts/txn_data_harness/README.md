# Transaction Data Harness

Generate realistic, high-volume Revenue Cloud demo data by driving the **real
transaction lifecycle** against a target org. Three scenario kinds:

```text
kind: sales_txn_quote (default) — (Opportunity) → Quote → Order (createOrderFromQuote) → Activate → Draft Invoice → Posted Invoice
kind: sales_txn_order           — (Opportunity) → Order (PST direct-place) → Activate → Draft Invoice → Posted Invoice
kind: invoice_ingestion         — POST /commerce/invoicing/.../actions/ingest → Draft Invoice (CreationMode=External)
```

The two PST kinds share the same post-Order tail (Activate → Invoice → Post);
only the head differs. `sales_txn_order` places an Order via PST directly (no
Quote), then writes the `AppUsageAssignment(AppUsageType =
RevenueLifecycleManagement)` row that gates the Revenue Cloud assetization
pipeline — without it, activation is a silent no-op (no BillingSchedule, no
Asset, no AsyncOperationTracker). See
[`docs/contracts-sales-txn-order.md`](docs/contracts-sales-txn-order.md) for
the live-verified contract and
[`scenarios/16-direct-orders.yaml`](scenarios/16-direct-orders.yaml) for a
ready-to-run example.

`Invoice`, `InvoiceLine`, and `BillingSchedule` are **system-generated** by the
billing engine (`createable: false`) — they cannot be bulk-loaded via SFDMU. The
only way to mint them is to call the same Connect/Business APIs the product uses.
This tool does exactly that, scenario by scenario, and records every id it creates
in a per-run manifest.

The `invoice_ingestion` path is **standalone billing** — it skips PST/Order/
Activate/BillingSchedule entirely and mints a Draft `Invoice` (with
`CreationMode = External`) plus its `InvoiceLine`s in a single typed
Composite-Graph call. Use it for demo orgs that need invoice volume without
the PST chain; see [`scenarios/15-standalone-billing-draft.yaml`](scenarios/15-standalone-billing-draft.yaml)
and [`CONTRACTS.md`](CONTRACTS.md) → *Invoice Ingestion*. Posted ingestion is
not an operator-supported scenario today because taxable `TaxTreatment` rows
require an `InvoiceLineTax` graph record; see [`docs/followups.md`](docs/followups.md).

It is **standalone** — not part of `prepare_rlm_org`. Each run is **additive**
(new records every time, tagged with a run id). With no config it auto-discovers a
billing-ready account and a billable product; config lets one run mix shapes.

> Full how-to (verification steps, troubleshooting, cleanup recipes) lives in
> [`docs/guides/txn-data-harness.md`](../../docs/guides/txn-data-harness.md).
> The live-verified endpoint/body/async contracts are locked in
> [`CONTRACTS.md`](CONTRACTS.md) — read it before changing `lifecycle.py`.

## Quick start

```bash
# Dry run — resolve auth + discovery and print the plan; NO writes.
python -m scripts.txn_data_harness.generate --org <your-sf-alias> --dry-run

# Equivalent composable CLI form.
python -m scripts.txn_data_harness.cli plan --org <your-sf-alias>

# One full chain to a Posted invoice.
python -m scripts.txn_data_harness.generate --org <your-sf-alias> --count 1 --target-stage invoice_posted

# Equivalent composable CLI form.
python -m scripts.txn_data_harness.cli run --org <your-sf-alias> --count 1 --target-stage invoice_posted

# 25 transactions, 4 in parallel.
python -m scripts.txn_data_harness.generate --org <your-sf-alias> --count 25 --concurrency 4

# Config-driven mixed run (billable + pipeline-only accounts).
python -m scripts.txn_data_harness.generate --org <your-sf-alias> --config scripts/txn_data_harness/config.example.yaml
```

The `generate` module is the single-command entry point. The subcommand CLI in
`cli.py` exposes the same run behavior plus `plan`, `inspect`, `step`, `report`,
and `prune` commands for humans and AI agents that need smaller composable
actions:

```bash
python -m scripts.txn_data_harness.cli inspect --latest
python -m scripts.txn_data_harness.cli step --org <your-sf-alias> \
  --manifest <run-id-or-path> --account "<account-name>" --to-stage invoice_draft
python -m scripts.txn_data_harness.cli report <base-run-id>           # batch summary from disk
python -m scripts.txn_data_harness.cli prune --older-than 7d          # dry run; --yes to delete
```

## ⚠ `--org` takes an *sf CLI* alias, not a CCI alias

CCI and the `sf` CLI use **different alias registries**. This tool talks to the
`sf` CLI only, so `--org` must be an **sf alias or username**. If a CCI alias
maps to a differently named sf alias, pass the **sf** alias:

```bash
python -m scripts.txn_data_harness.generate --org <sf-alias> ...       # sf alias or username
python -m scripts.txn_data_harness.generate --org <cci-alias> ...      # fails if not also an sf alias
```

## CLI flags

| Flag | Default | Purpose |
| ------ | ------- | ------- |
| `--org` | *(required)* | Target org: sf alias or username (NOT a CCI alias). |
| `--config` | — | YAML/JSON config file (all fields optional). |
| `--count` | 1 | Transactions to generate. Overrides `defaults.count` in a config, but **per-scenario `count:` wins** (precedence: builtins < config `defaults` < CLI < per-scenario). To shrink a multi-scenario config for a smoke run, edit the per-scenario `count:` rather than passing `--count`. |
| `--target-stage` | `invoice_posted` | How far to run: `opportunity_created`\|`quote_placed`\|`order_draft`\|`order_activated`\|`usage_upload`\|`invoice_draft`\|`invoice_posted`. |
| `--account` | auto | Pin the account by **Name**. |
| `--product` | auto (QB-preferred) | Pin the product by **SKU**. |
| `--with-opportunity` | off | Prepend an Opportunity the quote links to. |
| `--opportunity-stage` | first open | Pin the Opportunity `StageName`. |
| `--concurrency` | 4 | Parallel scenario workers (thread pool). |
| `--poll-timeout` | 180 | Async poll timeout (seconds) per billing step. |
| `--max-retries` | 2 | Retries for **transient** scenario failures (resumes from last checkpoint); `0` disables. |
| `--api-version` | `67.0` | API version; `latest` queries the org for newest. |
| `--transport` | `requests` | `requests` (native) or `cli` (`sf api request rest` proxy). |
| `--no-probe` / `--keep-probes` | — | **Reserved, currently no-ops** (the discovery PST probe is not implemented — see Limitations). |
| `--dry-run` | off | Resolve + print the plan; no writes. |
| `-v` / `-vv` | warn | INFO / DEBUG logging. |

Exit codes: `0` success · `1` one or more scenarios failed · `2` auth ·
`3` discovery/resolution · `4` bad config.

### Output & progress

A startup line announces the batch, then one line prints **as each scenario
completes** (completion order, not submission order):

```text
Running 10 scenario(s) across 1 spec(s), concurrency=3, run base DEMO-<timestamp> ...
[1/10] DEMO-<timestamp>-001: OK reached=post order=<order-id> manifest=.../out/....json
[2/10] DEMO-<timestamp>-004: FAILED reached=order order=<order-id> manifest=.../out/....json
...
Done: 9/10 scenario(s) succeeded. Manifests in .../out/
```

With `-v` (INFO) / `-vv` (DEBUG) each lifecycle step also logs, **prefixed with the
emitting scenario's run id** (`DEMO-<timestamp>-004 | order <order-id> activated`)
so interleaved output from concurrent workers stays attributable. Lines outside
any scenario (discovery, etc.) use `-` as the prefix. Errors always print
regardless of `-v`.

After the batch, a report is written to `out/<base_run_id>-report.json` (and a
`.md` companion) with success/failure counts, a histogram of how far each scenario
got, poll/link warnings, and a failure-signature rollup. Regenerate it later with
`cli report <base_run_id>`.

### Transient-failure retries

A flaky lifecycle (async billing polls, row locks, rate limits) is the common
failure mode. Failures are classified (`failure.py`): **transient** ones — network
timeouts, `UNABLE_TO_LOCK_ROW`, `REQUEST_LIMIT_EXCEEDED`, HTTP 429/5xx — are
retried up to `--max-retries` times (default 2) with exponential backoff,
**resuming from the last checkpointed stage** rather than redoing completed steps.
**Deterministic** failures (a missing field, a precondition like "quote_id is
required before order") fail fast and are never retried. The manifest records the
`attempts` count and the final `failure_class`.

Activation is checkpointed only after both derived-record barriers complete:
BillingSchedule polling and asset polling. Draft invoice ingestion retries only
when a transient failure occurs before any invoice id is observed; once an invoice
id is known, the manifest records it and the run stops instead of replaying the
ingest graph.

## Lifecycle stages

The PST chain (`kind: sales_txn_quote`, the default — `sales_txn_order` shares
the same stage list minus `quote_placed`) progresses through these stages. The
ingestion path (`kind: invoice_ingestion`) runs a single `ingest_invoice` step
that creates a Draft `Invoice` directly and stops at `target_stage:
invoice_draft`; it has no Quote/Order/Activate/BillingSchedule.

`target_stage` is hierarchical — each stage runs everything before it.

| Stage | Produces | Needs a BillingAccount? |
| ----- | -------- | ------------------------ |
| `opportunity_created` | Opportunity (opt-in head) | no |
| `quote_placed` | Quote (+ line) via Place Sales Transaction (`sales_txn_quote` only) | no |
| `order_draft` | Order — `sales_txn_quote` via `createOrderFromQuote`; `sales_txn_order` via PST direct-place + `AppUsageAssignment` | no |
| `order_activated` | Activated Order → BillingSchedule(s) + Asset(s) | **yes** |
| `usage_upload` | TransactionJournal consumption rows for opted-in usage lines | **yes** |
| `invoice_draft` | Draft Invoice (+ lines), tagged | **yes** |
| `invoice_posted` | Posted Invoice (InvoiceNumber assigned) | **yes** |

An account **without** a BillingAccount still goes `quote → order` (useful
pipeline + order demo data), but **activation** generates BillingSchedules and
Assets that require the account's billing setup, so the tool **auto-caps** such
scenarios at `order` and warns, rather than failing the run. This lets one config
mix billable-account invoices with pipeline-only-account orders in the same run.
The bundled QB example configs use **Infinitech** as the billing-ready account
and **Global Media** as the pipeline-only account; substitute equivalent account
names for another dataset.

## Config

All fields optional — anything omitted is auto-discovered. Precedence
(most-specific wins):

```text
per-scenario field  >  CLI flag  >  config `defaults`  >  built-in default
```

**Full scenario schema** (every field, types, defaults) and **what makes an
account/product a valid target** are documented in
[`scenarios/README.md`](scenarios/README.md), alongside ready-to-run example
configs (smoke test, pipeline quotes, draft/posted invoices, mixed stages,
multi-account, product/quantity spreads, randomized discounts, usage
consumption, and term/end-date examples). Start there.

[`config.example.yaml`](config.example.yaml) is a single-file worked example.
With no `scenarios:` block, a single spec runs and `volume.scenarios` sets its
count.

### Targets, bundles, and usage (at a glance)

- **Account** — exists by Name to reach `quote`/`order`; needs a
  **`BillingAccount`** to reach `activate`/`invoice`/`post` (else auto-capped at
  `order`). The bundled QB examples use `Infinitech` for a billing-ready account
  and `Global Media` for a pipeline-only account; substitute equivalents for
  your dataset.
- **Product** — needs an active `PricebookEntry` on the **standard** pricebook.
- **Subscription term** — per-line `term: {count, unit}` (or bare int) for
  `TermDefined` products drives `SubscriptionTerm` / `SubscriptionTermUnit`;
  the platform derives `EndDate` from those + `StartDate`. Defaults to the
  PSM's discovered
  `PricingTerm`/`PricingTermUnit`; falls back to `(12, Months)`. Multi-PBE SKUs
  need an explicit `selling_model:`. Evergreen / OneTime lines reject `term`.
  See `scenarios/README.md` → *Subscription terms* for the rules and
  `scenarios/13-multi-year-terms.yaml` for worked examples.
- **Explicit `end_date` override** (optional) — when set, the harness
  writes a calendar `EndDate` on the line and the platform prorates
  `PricingTermCount` against the actual span. Forms: absolute ISO date
  (`"2027-01-14"`), bare int days (`364`), or suffixed offset
  (`"364d"` / `"12mo"` / `"3q"` / `"1y"`). Supported units: `d`/`mo`/`q`/`y`
  (bare `m` is rejected as ambiguous — spell it `mo`). Co-term shorthand:
  pin `end_date:` at scenario level and every TermDefined line anchors to
  the same date. Requires an accompanying `term:`; TermDefined-only. See
  `scenarios/README.md` → *Explicit `EndDate` overrides*.
- **Multi-line via a product pool** — a scenario's `products:` list is a pool; each
  transaction places a random non-empty subset as flat lines (per-line qty/discount
  ranges). One SKU per quote is just a one-entry pool.
- **Bundles work for default configurations** — the tool sends one flat line, but
  PST expands the bundle's default component graph server-side and returns the
  configured child lines. `QB-COMPLETE` is the confirmed bundled-QB example. You
  cannot influence attribute or selling-model choices from YAML; bundles that
  require user input on mandatory slots will fail to place. See **Bundles caveat**
  below for the known invoice-poller workaround.
- **Usage / consumption is opt-in** — add a per-product `usage:` block to write
  `TransactionJournal` rows after activation. `target_stage: usage_upload` stops
  after journals so you can run `cli rate --org <sf-alias>` once for the batch;
  rating is org-wide and asynchronous. See `scenarios/README.md` →
  *Usage-based products* and `scenarios/12-usage-consumption.yaml`.

## Auth & transport

- **Token + instance URL** come from two `sf` CLI calls — the token from
  `sf org auth show-access-token`, the (non-secret) instance URL from
  `sf org display`. The token is held in memory for the run only: never written
  to disk, never logged, and **never passed *to* the `sf` CLI** (we read it out,
  we don't feed it in).
- **`requests` (default)** — native `requests.Session` with connection pooling and
  bounded retry/backoff. Sessions aren't thread-safe, so each worker gets its own
  (thread-local); all workers share the read-only token + instance URL.
- **`cli` fallback** (`--transport cli`) — shells out to `sf api request rest`, so
  our process never sees a token. Maximally stable if the CLI ever stops surfacing
  tokens, at the cost of a process spawn per call. JWT/connected-app auth is
  outside the current command surface.

## Manifests & cleanup

Every scenario writes `scripts/txn_data_harness/out/<run_id>.json` listing all ids it
created (quote, order, billing schedules, assets, invoice). This directory is
**git-ignored** — it's runtime output, not source. The manifest is the source of
truth for verification and cleanup.

The manifest is **checkpointed after every completed lifecycle stage**
(write-then-rename, so the file on disk is always valid JSON), not just on
completion. If the process is
killed or crashes mid-run, every scenario that had started still leaves a manifest
recording the ids created so far — so the partial org records can be found and
cleaned up. Within a run, a **transient** failure is retried from that last
checkpoint (see *Transient-failure retries*). Across invocations there is no
automatic resume — re-running `generate`/`cli run` starts a fresh batch — but the
`cli step --manifest <id> --to-stage <stage>` command will continue a specific
manifest from its `reached_stage` (clean up unwanted partials from their manifests
first).

Old manifests accumulate in `out/`; prune them by age with
`cli prune --older-than 7d` (dry run by default; `--yes` to delete — only `out/`
is ever touched).

**Drive cleanup from the manifest ids** — delete the ids the run recorded
(child → parent: assets/order, then quote, then opportunity). Records carry the
run id in `Description` for ad-hoc inspection, but standard description fields
are not a reliable SOQL cleanup key across orgs. In particular,
`Order.Description` is not filterable in this flow. Filter by manifest ids, not
by `Description`.

Deletability to assume:

- **Opportunities, Quotes, Assets** — deletable.
- **Activated Orders** — must be reverted to `Status=Draft` first (`sf data update
  record --sobject Order --record-id <id> --values "Status=Draft"`), then deletable.
- **Posted Invoices** — **not** deletable (only Draft/Canceled are; `Invoice.Status`
  isn't directly writable to Canceled). A `--target-stage invoice_draft` Draft invoice is.
- **BillingSchedules** — **not** deletable (system-managed: "insufficient access
  rights on object id").

See [`docs/guides/txn-data-harness.md`](../../docs/guides/txn-data-harness.md)
→ *Cleanup* for copy-paste recipes. There is no dedup/idempotency — re-running adds
a fresh batch with a new run id (by design).

## Known limitations

- **Bundles — default configuration only.** The harness submits one flat input
  line per `products:` entry; PST expands a bundle's default component graph
  server-side, so default-configured bundle SKUs (example: `QB-COMPLETE`) place,
  activate, and post cleanly in the bundled QB dataset. You cannot drive
  attribute values or selling-model choices for child slots — only
  default-configured bundles succeed.
- **`--no-probe` / `--keep-probes` are no-ops.** The discovery PST probe (place a
  throwaway quote to prove a product before fanning out volume) was scoped but not
  implemented; the flags are reserved for it. Discovery currently surfaces
  candidates by `PricebookEntry` only — a clean PBE is necessary but not sufficient
  for a complex bundle to *place*. Pin a known-good SKU (example: `QB-API-FLEX`
  in the QB demo dataset; substitute any term-defined SKU on the standard
  pricebook for your dataset) if a product fails to place.
- **Concurrency is lightly tested.** Verified at `--concurrency 3`. Higher values
  are untested against Salesforce API limits and billing-engine async contention —
  raise gradually for large volume runs.
- **Designed for admin invocation.** The harness is verified end-to-end as an
  org **admin** — that is the assumed invoker. The minimal PSL/PS for a
  non-admin/integration user is out of scope and intentionally not specified
  here.
- **Composite batching intentionally skipped.** The lifecycle is async-poll-bound,
  not request-bound, so Composite would save negligible wall-clock;
  scenario-level concurrency is the real win. See `CONTRACTS.md` for the
  rationale.

## Layout

```text
scripts/txn_data_harness/
  cli.py               # subcommands: plan/run/step/inspect/report/prune
  generate.py          # CLI entry: argparse, spec resolution, concurrency loop
  auth.py              # SfRestClient: transport-agnostic REST (requests | cli)
  discovery.py         # org introspection: accounts, products, pricebook, legal entity
  lifecycle.py         # lifecycle API calls, usage journals, and async polling contracts
  models.py            # shared execution models (Manifest, LineItem, resolved specs)
  runner.py            # resolved-plan execution, batching, checkpoint + retry policy
  steps.py             # composable step registry over lifecycle.py calls
  failure.py           # transient/deterministic/unknown failure classifier (retry decisions)
  report.py            # batch report: counts, stage histogram, failure-signature rollup
  manifests.py         # manifest write/load/list/inspect + retention prune helpers
  config.py            # YAML/JSON spec load + validate + merge
  config.example.yaml  # worked example
  AI_TOOLS.md          # AI-safe command recipes and verification rules
  CONTRACTS.md         # live-verified endpoint/body/async contracts (read before editing lifecycle.py)
  docs/followups.md    # open questions / anomalies / probes that would generalize a finding
  out/                 # per-run manifests + batch reports (git-ignored)
```
