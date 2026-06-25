# Transaction Data Harness — Sales Demo Data Workflows

Use this skill when a user asks to plan, generate, inspect, continue, verify, or
clean up Revenue Cloud transaction demo data with the Transaction Data Harness.
The skill routes agents to the right command surface and safety checks; detailed
copy-paste recipes live in `scripts/txn_data_harness/AI_TOOLS.md` and
`docs/guides/txn-data-harness.md`.

## Quick Rules

1. **Plan before writes:** run `cli plan` or `generate --dry-run` before creating
   records.
2. **Use an sf alias, not a CCI alias:** `--org <sf-alias>`, not a CCI-only alias.
3. **Use manifests as truth:** inspect and verify by ids in
   `scripts/txn_data_harness/out/<run_id>.json`.
4. **Start with smoke:** run one small scenario before any volume or concurrency.
5. **Treat runs as additive:** re-running creates a new batch; there is no
   idempotency or dedup.
6. **Verify in Salesforce before claiming success:** `--dry-run` and unit tests
   do not prove lifecycle behavior.
7. **Usage is two-step:** `target_stage: usage_upload` writes `TransactionJournal`
   rows; `cli rate` starts the separate org-wide async rating flow once per
   batch.
8. **Lifecycle/API changes require contracts:** read `CONTRACTS.md`, update
   tests, and live-verify the changed behavior before presenting it as verified.
9. **Completed-stage checkpoints:** `reached_stage` records durable stage
   completion, not "step started"; activation reaches `order_activated` only
   after BillingSchedule and asset polling finish.
10. **`--count` does NOT override per-scenario `count:`** in a config. Precedence is
   per-scenario > CLI > `defaults` > builtins, so passing `--count 1` against a
   config whose scenarios pin `count: 100` runs all 100. To smoke a multi-scenario
   config, edit the per-scenario `count:` (or comment scenarios out) instead.
11. **Three scenario kinds:**
    - `kind: sales_txn_quote` (default) — Opportunity → Quote → Order
      (`createOrderFromQuote`) → Activate → Draft Invoice → Posted Invoice.
    - `kind: sales_txn_order` — Opportunity (optional) → Order (PST direct-place)
      → `AppUsageAssignment(RevenueLifecycleManagement)` → Activate → Draft
      Invoice → Posted Invoice. Skips the Quote; the post-Order tail is
      identical to the quote path. The AppUsageAssignment row is the
      assetization-pipeline gate — without it, activation can silently skip
      downstream BillingSchedule/Asset work. Live-verified contract:
      `scripts/txn_data_harness/docs/contracts-sales-txn-order.md`. Reference
      config: `scenarios/16-direct-orders.yaml`.
    - `kind: invoice_ingestion` skips PST and `POST`s a typed Composite-Graph
      payload to `/commerce/invoicing/.../actions/ingest`, minting a Draft
      `Invoice` (`CreationMode = External`) directly. Use the ingestion path
      only for **Draft** today; Posted ingestion is not operator-supported until
      tax graph support is implemented and verified.
      Reference config: `scenarios/15-standalone-billing-draft.yaml`.
    Legacy `sales_transaction` and `transaction` kind names are rejected at
    config-load time with a hint pointing at the new names.

## DO NOT

- **DO NOT** pass a CCI alias to `--org`; this harness uses the `sf` CLI alias
  registry.
- **DO NOT** run a write command without a successful plan/dry-run first.
- **DO NOT** use `Order.Description` in SOQL filters for cleanup; it is not
  filterable. Use manifest ids.
- **DO NOT** promise full cleanup for Posted Invoices or BillingSchedules; they
  are platform-managed leftovers.
- **DO NOT** present `--dry-run` or unit tests as Salesforce lifecycle
  verification. A behavioral claim needs a live smoke run.
- **DO NOT** edit lifecycle payloads from memory; check
  `scripts/txn_data_harness/CONTRACTS.md` and update it with any verified change.
- **DO NOT** copy org aliases, run ids, invoice numbers, or order numbers from
  `CONTRACTS.md` / `docs/followups.md` into operator docs. Those files are
  evidence notebooks; reusable docs should use placeholders or explicitly
  labeled example data.

## Entry Conditions

| User intent | Use this skill? | Notes |
| ----------- | --------------- | ----- |
| Generate Sales/Revenue Cloud demo transactions | Yes | Plan first, then run one smoke scenario. |
| Mint standalone-billing Draft invoices (no PST chain) | Yes | Use `scenarios/15-standalone-billing-draft.yaml` (`kind: invoice_ingestion`). Posted ingestion is not operator-supported today. |
| Inspect or continue a partial harness run | Yes | Use manifest-driven `inspect` / `step`. |
| Verify orders/invoices created by the harness | Yes | Query by manifest ids. |
| Clean up harness-created records | Yes | Explain non-deletable leftovers. |
| Modify harness lifecycle/API behavior | Yes | Also read `CONTRACTS.md` and run tests. |
| Add or revise scenario YAML examples | Yes | Also update `scenarios/README.md`. |
| Change skill guidance itself | Maybe | Also read `skill-authoring/SKILL.md`. |
| Create SFDMU data plans | No | Use `sfdmu-data-plans/SKILL.md`. |
| Use general Revenue Cloud REST APIs | Maybe | Use `rlm-business-apis/SKILL.md` for API reference. |

## Source Files

| Need | File | Read when... |
| ---- | ---- | ------------ |
| AI command recipes and stop conditions | `scripts/txn_data_harness/AI_TOOLS.md` | Running or recovering harness jobs. |
| CLI/config reference | `scripts/txn_data_harness/README.md` | Explaining flags, stages, auth, manifests, limitations. |
| Scenario schema and examples | `scripts/txn_data_harness/scenarios/README.md` | Editing YAML examples or config fields. |
| Operational guide, verification, cleanup | `docs/guides/txn-data-harness.md` | Giving user-facing runbooks or cleanup steps. |
| Live-verified API contracts | `scripts/txn_data_harness/docs/README.md` | Changing lifecycle payloads, polling, or sequencing. |
| Open probes and anomalies | `scripts/txn_data_harness/docs/followups.md` | Investigating behavior not yet safe to generalize. |
| Unit tests | `tests/txn_data_harness/` | Changing code, config parsing, manifests, steps, or docs examples. |

## Command Selection

| Need | Prefer |
| ---- | ------ |
| Show what would happen without writes | `python -m scripts.txn_data_harness.cli plan ...` |
| Create records | `python -m scripts.txn_data_harness.cli run ...` |
| Keep compatibility with older instructions | `python -m scripts.txn_data_harness.generate ...` |
| Inspect the latest or a specific manifest | `python -m scripts.txn_data_harness.cli inspect ...` |
| Continue a partial manifest | `python -m scripts.txn_data_harness.cli step ...` |
| Rebuild a batch summary | `python -m scripts.txn_data_harness.cli report ...` |
| Prune old local manifests | `python -m scripts.txn_data_harness.cli prune ...` |
| Start usage rating after `target_stage: usage_upload` | `python -m scripts.txn_data_harness.cli rate ...` |

## Standard Workflow

1. Confirm the target org is an `sf` alias:

   ```bash
   sf org display --target-org <sf-alias> --json
   ```

1. Plan with no writes:

   ```bash
   python -m scripts.txn_data_harness.cli plan --org <sf-alias> \
     --config scripts/txn_data_harness/scenarios/01-smoke-test.yaml
   ```

1. Run one smoke scenario. Pick a config whose scenarios already have a small
   `count:` (e.g. `01-smoke-test.yaml`); `--count` will NOT shrink a config that
   pins `count:` per scenario (see Quick Rule 10). For a high-volume config,
   edit the per-scenario `count:` to 1 (or copy the scenario out) before
   smoking.

   ```bash
   python -m scripts.txn_data_harness.cli run --org <sf-alias> \
     --config scripts/txn_data_harness/scenarios/01-smoke-test.yaml \
     --concurrency 1 -v
   ```

1. Inspect the manifest:

   ```bash
   python -m scripts.txn_data_harness.cli inspect --latest --json
   ```

1. Verify by manifest ids with SOQL before reporting success. For a posted
   invoice:

   ```bash
   sf data query --target-org <sf-alias> -q "
     SELECT Id, InvoiceNumber, Status, TotalAmount
     FROM Invoice WHERE Id = '<invoiceId>'"
   ```

1. Scale only after the smoke run verifies cleanly. Increase `--concurrency`
   gradually.

## Continuing Partial Runs

Use `step` to continue from a manifest's `reached_stage`. Pass `--account`
explicitly for older manifests or whenever ambiguity would be risky:

```bash
python -m scripts.txn_data_harness.cli step --org <sf-alias> \
  --manifest scripts/txn_data_harness/out/<run_id>.json \
  --account "<billing-ready-account-name>" \
  --to-stage invoice_draft
```

The command uses the shared step registry, so it preserves the same sequencing
barriers as full runs.

## Cleanup

Drive cleanup from manifest ids. Delete what is deletable child → parent:
assets/orders, then quote, then opportunity. Activated orders must be reverted to
Draft before deletion. Posted invoices and BillingSchedules are not cleanly
deletable; tell the user before attempting cleanup.

For copy-paste cleanup recipes, use `docs/guides/txn-data-harness.md`.

## Examples

### User asks: "Create a few posted invoices in my demo org"

1. Confirm the target is an `sf` alias or username, not a CCI-only alias.
2. Run `cli plan` with a smoke scenario.
3. If the plan targets the expected account/product and no unexpected cap appears,
   run `cli run --concurrency 1`.
4. Inspect the manifest and verify the invoice with SOQL.

### User asks: "Why did my run stop at order?"

Inspect the manifest and plan output. Non-billing accounts cap at `order_draft` because
activation creates BillingSchedules/Assets and needs billing setup. Recommend a
billing-ready account for the target dataset.

### User asks: "Change the PST payload"

Read `scripts/txn_data_harness/CONTRACTS.md` first, update tests in
`tests/txn_data_harness/test_lifecycle_payloads.py`, and live-verify the changed
contract before presenting it as verified.

## Validation Checks

For harness code or docs changes, run:

```bash
python -m pytest tests/txn_data_harness/
python -m compileall scripts/txn_data_harness
python -m scripts.txn_data_harness.generate --help
python -m scripts.txn_data_harness.cli --help
python -m scripts.txn_data_harness.cli step --help
```

For behavioral lifecycle changes, also run a live smoke scenario against a
scratch/sandbox org and verify the manifest ids in Salesforce.
