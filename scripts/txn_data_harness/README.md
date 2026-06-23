# Transaction Data Harness

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
> [`docs/guides/txn-data-harness.md`](../../docs/guides/txn-data-harness.md).
> The live-verified endpoint/body/async contracts are locked in
> [`CONTRACTS.md`](CONTRACTS.md) — read it before changing `lifecycle.py`.

## Quick start

```bash
# Dry run — resolve auth + discovery and print the plan; NO writes.
python -m scripts.txn_data_harness.generate --org rlm-base__jun17_1 --dry-run

# One full chain to a Posted invoice.
python -m scripts.txn_data_harness.generate --org rlm-base__jun17_1 --count 1 --target-stage post

# 25 transactions, 4 in parallel.
python -m scripts.txn_data_harness.generate --org rlm-base__jun17_1 --count 25 --concurrency 4

# Config-driven mixed run (billable + pipeline-only accounts).
python -m scripts.txn_data_harness.generate --org rlm-base__jun17_1 --config scripts/txn_data_harness/config.example.yaml
```

## ⚠ `--org` takes an *sf CLI* alias, not a CCI alias

CCI and the `sf` CLI use **different alias registries**. This tool talks to the
`sf` CLI only, so `--org` must be an **sf alias or username**. The CCI alias
`beta` maps to the sf alias `rlm-base__beta` — pass the **sf** one:

```bash
python -m scripts.txn_data_harness.generate --org rlm-base__beta ...   # ✅ sf alias
python -m scripts.txn_data_harness.generate --org beta ...             # ❌ CCI alias — won't resolve
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

### Output & progress

A startup line announces the batch, then one line prints **as each scenario
completes** (completion order, not submission order):

```
Running 10 scenario(s) across 1 spec(s), concurrency=3, run base DEMO-20260622T... ...
[1/10] DEMO-...-001: OK reached=post order=00000123 manifest=.../out/....json
[2/10] DEMO-...-004: FAILED reached=order order=00000126 manifest=.../out/....json
...
Done: 9/10 scenario(s) succeeded. Manifests in .../out/
```

With `-v` (INFO) / `-vv` (DEBUG) each lifecycle step also logs, **prefixed with the
emitting scenario's run id** (`DEMO-...-004 | order 801... activated`) so interleaved
output from concurrent workers stays attributable. Lines outside any scenario
(discovery, etc.) use `-` as the prefix. Errors always print regardless of `-v`.

## Lifecycle stages

`target_stage` is hierarchical — each stage runs everything before it.

| Stage | Produces | Needs a BillingAccount? |
|-------|----------|--------------------------|
| `opportunity` | Opportunity (opt-in head) | no |
| `quote` | Quote (+ line) via Place Sales Transaction | no |
| `order` | Order via createOrderFromQuote | no |
| `activate` | Activated Order → BillingSchedule(s) + Asset(s) | **yes** |
| `invoice` | Draft Invoice (+ lines), tagged | **yes** |
| `post` | Posted Invoice (InvoiceNumber assigned) | **yes** |

An account **without** a BillingAccount still goes `quote → order` (useful
pipeline + order demo data), but **activation** generates BillingSchedules and
Assets that require the account's billing setup, so the tool **auto-caps** such
scenarios at `order` and warns, rather than failing the run. This lets one config
mix billable Infinitech invoices with Global Media pipeline orders. (In QB, only
**Infinitech** is pre-wired with a BillingAccount.)

## Config

All fields optional — anything omitted is auto-discovered. Precedence
(most-specific wins):

```
per-scenario field  >  CLI flag  >  config `defaults`  >  built-in default
```

**Full scenario schema** (every field, types, defaults) and **what makes an
account/product a valid target** are documented in
[`scenarios/README.md`](scenarios/README.md), alongside ready-to-run example
configs (smoke test, pipeline quotes, draft/posted invoices, mixed stages,
multi-account, product/quantity spreads, randomized discounts). Start there.

[`config.example.yaml`](config.example.yaml) is the original single-file worked
example. With no `scenarios:` block, a single spec runs and `volume.scenarios`
sets its count.

### Targets, bundles, and usage (at a glance)

- **Account** — exists by Name to reach `quote`/`order`; needs a
  **`BillingAccount`** to reach `activate`/`invoice`/`post` (else auto-capped at
  `order`). In QB only **Infinitech** is billable; **Global Media** is pipeline-only.
- **Product** — needs an active `PricebookEntry` on the **standard** pricebook.
- **Multi-line via a product pool** — a scenario's `products:` list is a pool; each
  transaction places a random non-empty subset as flat lines (per-line qty/discount
  ranges). One SKU per quote is just a one-entry pool.
- **Bundles are not supported** — each line is flat, so pin simple SKUs like
  `QB-API-FLEX`; bundles (`QB-COMPLETE`, `QB-BDL-*`) need a component graph this
  tool doesn't build.
- **Usage / consumption is not supported** — metered/commit SKUs (`*-BLNG`,
  token/quantity/monetary commit) would invoice with no usage behind them.

See [`scenarios/README.md`](scenarios/README.md) → *Not handled yet* for detail.

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

Every scenario writes `scripts/txn_data_harness/out/<run_id>.json` listing all ids it
created (quote, order, billing schedules, assets, invoice). This directory is
**git-ignored** — it's runtime output, not source. The manifest is the source of
truth for verification and cleanup.

The manifest is **checkpointed after every lifecycle stage** (write-then-rename, so
the file on disk is always valid JSON), not just on completion. If the process is
killed or crashes mid-run, every scenario that had started still leaves a manifest
recording the ids created so far — so the partial org records can be found and
cleaned up. There is no resume: re-running starts a fresh batch (clean up the
partials from their manifests first).

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

See [`docs/guides/txn-data-harness.md`](../../docs/guides/txn-data-harness.md)
→ *Cleanup* for copy-paste recipes. There is no dedup/idempotency — re-running adds
a fresh batch with a new run id (by design).

## Known limitations

- **Flat lines only (no bundle component graph).** Multi-line quotes **are**
  supported — a scenario's `products:` pool is placed as a random non-empty subset
  of flat lines per transaction, each with its own quantity/discount (see
  `scenarios/README.md`). What's *not* supported is a single line that expands into
  a configured **bundle** (component/attribute graph); each line stays flat.
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
scripts/txn_data_harness/
  generate.py          # CLI entry: argparse, spec resolution, concurrency loop
  auth.py              # SfRestClient: transport-agnostic REST (requests | cli)
  discovery.py         # org introspection: accounts, products, pricebook, legal entity
  lifecycle.py         # the 6 lifecycle steps + async polling (transcribed from CONTRACTS.md)
  config.py            # YAML/JSON spec load + validate + merge
  config.example.yaml  # worked example
  CONTRACTS.md         # live-verified endpoint/body/async contracts (read before editing lifecycle.py)
  out/                 # per-run manifests (git-ignored)
```
