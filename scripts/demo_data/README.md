# Demo Data Generator

Generate realistic, high-volume Revenue Cloud demo data by driving the **real
transaction lifecycle** against a target org:

```
(Opportunity) → Quote → Order → Activate → Invoice (Draft) → Post
```

`Invoice`, `InvoiceLine`, and `BillingSchedule` are **system-generated** by the
billing engine (`createable: false`) — they cannot be bulk-loaded via SFDMU. The
only way to mint them is to call the same Connect/Business APIs the product uses.
This tool does exactly that, scenario by scenario, and records every id it creates
in a per-run manifest.

It is **standalone** — not part of `prepare_rlm_org`. Each run is **additive**
(new records every time, tagged with a run id). With no config it auto-discovers a
billing-ready account and a billable product; config lets one run mix shapes.

> Full how-to (verification steps, troubleshooting, cleanup recipes) lives in
> [`docs/guides/demo-data-generator.md`](../../docs/guides/demo-data-generator.md).
> The live-verified endpoint/body/async contracts are locked in
> [`CONTRACTS.md`](CONTRACTS.md) — read it before changing `lifecycle.py`.

## Quick start

```bash
# Dry run — resolve auth + discovery and print the plan; NO writes.
python -m scripts.demo_data.generate --org rlm-base__jun17_1 --dry-run

# One full chain to a Posted invoice.
python -m scripts.demo_data.generate --org rlm-base__jun17_1 --count 1 --target-stage post

# 25 transactions, 4 in parallel.
python -m scripts.demo_data.generate --org rlm-base__jun17_1 --count 25 --concurrency 4

# Config-driven mixed run (billable + pipeline-only accounts).
python -m scripts.demo_data.generate --org rlm-base__jun17_1 --config scripts/demo_data/config.example.yaml
```

## ⚠ `--org` takes an *sf CLI* alias, not a CCI alias

CCI and the `sf` CLI use **different alias registries**. This tool talks to the
`sf` CLI only, so `--org` must be an **sf alias or username**. The CCI alias
`beta` maps to the sf alias `rlm-base__beta` — pass the **sf** one:

```bash
python -m scripts.demo_data.generate --org rlm-base__beta ...   # ✅ sf alias
python -m scripts.demo_data.generate --org beta ...             # ❌ CCI alias — won't resolve
```

## CLI flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--org` | *(required)* | Target org: sf alias or username (NOT a CCI alias). |
| `--config` | — | YAML/JSON config file (all fields optional). |
| `--count` | 1 | Transactions to generate (overrides config). |
| `--target-stage` | `post` | How far to run: `opportunity`\|`quote`\|`order`\|`activate`\|`invoice`\|`post`. |
| `--account` | auto | Pin the account by **Name**. |
| `--product` | auto (QB-preferred) | Pin the product by **SKU**. |
| `--with-opportunity` | off | Prepend an Opportunity the quote links to. |
| `--opportunity-stage` | first open | Pin the Opportunity `StageName`. |
| `--concurrency` | 4 | Parallel scenario workers (thread pool). |
| `--poll-timeout` | 180 | Async poll timeout (seconds) per billing step. |
| `--api-version` | `67.0` | API version; `latest` queries the org for newest. |
| `--transport` | `requests` | `requests` (native) or `cli` (`sf api request rest` proxy). |
| `--no-probe` / `--keep-probes` | — | **Reserved, currently no-ops** (the discovery PST probe is not implemented — see Limitations). |
| `--dry-run` | off | Resolve + print the plan; no writes. |
| `-v` / `-vv` | warn | INFO / DEBUG logging. |

Exit codes: `0` success · `1` one or more scenarios failed · `2` auth ·
`3` discovery/resolution · `4` bad config.

## Lifecycle stages

`target_stage` is hierarchical — each stage runs everything before it.

| Stage | Produces | Needs a BillingAccount? |
|-------|----------|--------------------------|
| `opportunity` | Opportunity (opt-in head) | no |
| `quote` | Quote (+ line) via Place Sales Transaction | no |
| `order` | Order via createOrderFromQuote | no |
| `activate` | Activated Order → BillingSchedule(s) + Asset(s) | no |
| `invoice` | Draft Invoice (+ lines), tagged | **yes** |
| `post` | Posted Invoice (InvoiceNumber assigned) | **yes** |

An account **without** a BillingAccount can't reach `invoice`/`post`; the tool
**auto-caps** such scenarios at `activate` and warns, rather than failing the run.
This lets one config mix billable Infinitech orders with Global Media pipeline
quotes. (In QB, only **Infinitech** is pre-wired with a BillingAccount.)

## Config

All fields optional — anything omitted is auto-discovered. Precedence
(most-specific wins):

```
per-scenario field  >  CLI flag  >  config `defaults`  >  built-in default
```

See [`config.example.yaml`](config.example.yaml) for a worked example. With no
`scenarios:` block, a single spec runs and `volume.scenarios` sets its count.

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
  tokens, at the cost of a process spawn per call. (JWT/connected-app is the
  documented long-term escalation; not implemented.)

## Manifests & cleanup

Every scenario writes `scripts/demo_data/out/<run_id>.json` listing all ids it
created (quote, order, billing schedules, assets, invoice). This directory is
**git-ignored** — it's runtime output, not source. The manifest is the source of
truth for verification and cleanup.

**Drive cleanup from the manifest ids** — delete the ids the run recorded
(child → parent: assets/order, then quote, then opportunity). Every record also
carries the run id in `Description` for ad-hoc inspection, but note **`Order.Description`
is not SOQL-filterable** ("field 'Description' can not be filtered in a query
call"), so a `WHERE Description LIKE 'DEMO-%'` sweep on Order fails — filter orders
by id. `Quote.Description` *is* filterable.

Deletability (verified live):

- **Opportunities, Quotes, Assets** — deletable.
- **Activated Orders** — must be reverted to `Status=Draft` first (`sf data update
  record --sobject Order --record-id <id> --values "Status=Draft"`), then deletable.
- **Posted Invoices** — **not** deletable (only Draft/Canceled are; `Invoice.Status`
  isn't directly writable to Canceled). A `--target-stage invoice` Draft invoice is.
- **BillingSchedules** — **not** deletable (system-managed: "insufficient access
  rights on object id").

See [`docs/guides/demo-data-generator.md`](../../docs/guides/demo-data-generator.md)
→ *Cleanup* for copy-paste recipes. There is no dedup/idempotency — re-running adds
a fresh batch with a new run id (by design).

## Known limitations

- **Single line per quote.** A scenario's `products:` list accepts multiple
  entries, but only the **first** is placed today (the rest are logged and
  ignored). Multi-line orders/invoices are not yet supported.
- **`--no-probe` / `--keep-probes` are no-ops.** The discovery PST probe (place a
  throwaway quote to prove a product before fanning out volume) was scoped but not
  implemented; the flags are reserved for it. Discovery currently surfaces
  candidates by `PricebookEntry` only — a clean PBE is necessary but not sufficient
  for a complex bundle to *place*. Pin a known-good SKU (e.g. `QB-API-FLEX`) if a
  product fails to place.
- **Concurrency is lightly tested.** Verified at `--concurrency 3`. Higher values
  are untested against Salesforce API limits and billing-engine async contention —
  raise gradually for large volume runs.
- **Permission set unconfirmed.** Verified only as an org **admin**. The minimal
  PSL/PS for a non-admin/integration running user is an open `TODO` (see
  `CONTRACTS.md`).
- **Composite batching intentionally skipped** (Phase 5). The lifecycle is
  async-poll-bound, not request-bound, so Composite would save negligible
  wall-clock; scenario-level concurrency is the real win. See `CONTRACTS.md`
  → *Phase 5 (Composite) — DECIDED: skipped* for the rationale.

## Layout

```
scripts/demo_data/
  generate.py          # CLI entry: argparse, spec resolution, concurrency loop
  auth.py              # SfRestClient: transport-agnostic REST (requests | cli)
  discovery.py         # org introspection: accounts, products, pricebook, legal entity
  lifecycle.py         # the 6 lifecycle steps + async polling (transcribed from CONTRACTS.md)
  config.py            # YAML/JSON spec load + validate + merge
  config.example.yaml  # worked example
  CONTRACTS.md         # live-verified endpoint/body/async contracts (read before editing lifecycle.py)
  out/                 # per-run manifests (git-ignored)
```
