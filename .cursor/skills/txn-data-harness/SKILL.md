# Transaction Data Harness — Sales Demo Data Workflows

Use this skill when a user asks to plan, generate, inspect, continue, verify, or
clean up Revenue Cloud transaction demo data with the Transaction Data Harness.
The harness drives the real Opportunity → Quote → Order → Activate → Invoice →
Post lifecycle against a Salesforce org and records every created id in a
manifest.

## Quick Rules

1. **Plan before writes:** run `cli plan` or `generate --dry-run` before creating
   records.
2. **Use an sf alias, not a CCI alias:** `--org rlm-base__beta`, not `--org beta`.
3. **Use manifests as truth:** inspect and verify by ids in
   `scripts/txn_data_harness/out/<run_id>.json`.
4. **Start with smoke:** run one small scenario before any volume or concurrency.
5. **Treat runs as additive:** re-running creates a new batch; there is no
   idempotency or dedup.
6. **Verify posted invoices in the org:** do not claim a Posted invoice exists
   until the manifest and SOQL verification agree.
7. **Read `CONTRACTS.md` before changing lifecycle code:** endpoint shapes and
   async barriers are live-verified there.
8. **Usage products are opt-in:** add a `usage:` block to a `products[]` entry
   to write `TransactionJournal` consumption rows after activation. The new
   `usage` stage sits between `activate` and `invoice` and is a no-op for
   lines that don't declare a `usage:` block.
9. **Tag TJ rows with `UniqueIdentifier`, never `Description`:** the v262
   `TransactionJournal` object has no `Description` field. The harness writes
   `UniqueIdentifier = txn-harness-<run_id>-<asset_id>-<target_idx>-<row_idx>`
   so retries dedupe and bulk cleanup filters cleanly.
10. **Run `cli rate` separately, once per batch:** rating
    (`RLM_OrchestrateUsageManagement`) is asynchronous, takes ~15 minutes,
    and rates **every** usage product in the org. It is intentionally not a
    per-scenario stage and not a CCI task.

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

## Entry Conditions

| User intent | Use this skill? | Notes |
| ----------- | --------------- | ----- |
| Generate Sales/Revenue Cloud demo transactions | Yes | Plan first, then run a smoke scenario. |
| Inspect or continue a partial harness run | Yes | Use manifest-driven `inspect` / `step`. |
| Verify orders/invoices created by the harness | Yes | Query by manifest ids. |
| Clean up harness-created records | Yes | Explain non-deletable leftovers. |
| Modify harness lifecycle/API behavior | Yes | Also read `CONTRACTS.md` and run tests. |
| Create SFDMU data plans | No | Use `sfdmu-data-plans/SKILL.md`. |
| Use general Revenue Cloud REST APIs | Maybe | Use `rlm-business-apis/SKILL.md` for API reference. |

## Source Files

| Need | File |
| ---- | ---- |
| AI command recipes and stop conditions | `scripts/txn_data_harness/AI_TOOLS.md` |
| CLI/config reference | `scripts/txn_data_harness/README.md` |
| Operational guide, verification, cleanup | `docs/guides/txn-data-harness.md` |
| Live-verified API contracts | `scripts/txn_data_harness/CONTRACTS.md` |
| Composable CLI | `scripts/txn_data_harness/cli.py` |
| Compatibility CLI | `scripts/txn_data_harness/generate.py` |
| Unit tests | `tests/txn_data_harness/` |

## Standard Workflow

1. Confirm the target org is an `sf` alias:

   ```bash
   sf org display --target-org <sf-alias> --json
   ```

2. Plan with no writes:

   ```bash
   python -m scripts.txn_data_harness.cli plan --org <sf-alias> \
     --config scripts/txn_data_harness/scenarios/01-smoke-test.yaml
   ```

3. Run one smoke scenario:

   ```bash
   python -m scripts.txn_data_harness.cli run --org <sf-alias> \
     --config scripts/txn_data_harness/scenarios/01-smoke-test.yaml \
     --concurrency 1 -v
   ```

4. Inspect the manifest:

   ```bash
   python -m scripts.txn_data_harness.cli inspect --latest
   ```

5. Verify by manifest ids with SOQL before reporting success. For a posted
   invoice:

   ```bash
   sf data query --target-org <sf-alias> -q "
     SELECT Id, InvoiceNumber, Status, TotalAmount
     FROM Invoice WHERE Id = '<invoiceId>'"
   ```

6. Scale only after the smoke run verifies cleanly. Increase `--concurrency`
   gradually.

## Continuing Partial Runs

Use `step` to continue from a manifest's `reached_stage`:

```bash
python -m scripts.txn_data_harness.cli step --org <sf-alias> \
  --manifest scripts/txn_data_harness/out/<run_id>.json \
  --account Infinitech \
  --to-stage invoice
```

Pass `--account` explicitly for older manifests or when ambiguity would be risky.
The command uses the shared step registry, so it preserves the same sequencing
barriers as full runs.

## Cleanup

Drive cleanup from manifest ids. Delete what is deletable child → parent:
assets/orders, then quote, then opportunity. Activated orders must be reverted to
Draft before deletion. Posted invoices and BillingSchedules are not cleanly
deletable; tell the user before attempting cleanup.

For copy-paste cleanup recipes, use `docs/guides/txn-data-harness.md`.

## Examples

### User asks: "Create a few posted invoices in beta"

1. Translate `beta` to the `sf` alias, usually `rlm-base__beta`.
2. Run `cli plan` with a smoke scenario.
3. If the plan targets the expected account/product and no unexpected cap appears,
   run `cli run --concurrency 1`.
4. Inspect the manifest and verify the invoice with SOQL.

### User asks: "Why did my run stop at order?"

Inspect the manifest and plan output. Non-billing accounts cap at `order` because
activation creates BillingSchedules/Assets and needs billing setup. Recommend a
billing-ready account such as Infinitech in the QB org.

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
