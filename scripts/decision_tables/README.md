# Decision Table toolkit

Standalone commands for inspecting and managing Revenue Cloud BRE Decision
Tables. They use the authenticated `sf` CLI, not CumulusCI, and default to API
v67.0.

- Pass an **SF CLI alias or username** to `--target-org`.
- Read commands never mutate the org.
- Write commands preview by default and require `--confirm`.
- Definition writes use Metadata API or Tooling API. Connect is used only for
  CSV data and CSV-version lifecycle operations.

Use the CCI tasks for repeatable org builds. Use this toolkit for inspection,
diagnosis, and deliberate one-off changes. Conceptual guidance lives in
`.cursor/skills/decision-tables/`; detailed API contracts and platform caveats
live in `docs/references/decision-table-api-reference.md`.

## Model

A Decision Table has two independently managed layers:

1. **Definition** — columns, source binding, criteria, hit policy, and status.
   Metadata API and the five Tooling setup objects represent this layer.
2. **Data** — source records, uploaded CSV rows, or runtime context data.
   Definition changes do not update this layer; refresh or upload it separately.

## Commands

### Read-only

| Command | Purpose |
|---|---|
| `list_decision_tables.py` | List tables; filter by status, usage type, or developer name. |
| `describe_decision_table.py` | Show one complete Tooling definition. |
| `diff_decision_tables.py` | Compare two definitions in one org or across two orgs. |
| `trace_decision_table.py` | Find pricing recipe mappings that reference a table. |
| `dump_decision_table_data.py` | Sample the materialized data layer. `--filter FIELD:VALUE` is available for CSV tables. |

### Mutating, preview by default

| Command | Purpose |
|---|---|
| `create_decision_table.py` | Create from a canonical JSON spec through Metadata or Tooling. `--generate-only` writes Metadata XML without deploying. |
| `update_decision_table.py` | Replace an existing Tooling definition with one PATCH. Active tables are rejected by Salesforce. |
| `activate_decision_table.py` | Activate a table and wait for the terminal status. CSV tables activate their unambiguous file-import version. |
| `deactivate_decision_table.py` | Deactivate a table and confirm the terminal status. |
| `refresh_decision_table.py` | Queue a full or incremental refresh. Versioned CSV tables require `--version-number`. |
| `upload_decision_table_data.py` | Append CSV rows and wait for `Completed`, `CompletedWithErrors`, or `Failed`. |
| `delete_decision_table.py` | Delete with one Tooling request. Active or referenced tables are rejected by Salesforce. |

Every command supports `--help`. Commands that support structured output use
`--json`; controlled failures then return a nonzero exit and a JSON `error`.

## Inspect

```bash
ORG=<sf_alias>

python scripts/decision_tables/list_decision_tables.py \
  --target-org "$ORG"

python scripts/decision_tables/describe_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName>

python scripts/decision_tables/diff_decision_tables.py \
  --target-org "$ORG" --developer-name <TableA> --other <TableB>

python scripts/decision_tables/trace_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName>

python scripts/decision_tables/dump_decision_table_data.py \
  --target-org "$ORG" --developer-name <DeveloperName> --limit 5
```

For a cross-org diff, add `--other-org <sf_alias>`. For a CSV data sample,
`--filter Region:North` performs exact, case-sensitive matching. The command
omits `--limit` when a filter is present because the platform rejects some
filter/limit combinations.

## Mutate

Use a disposable org for destructive experiments.

```bash
ORG=<disposable_sf_alias>

# Preview, then create through Tooling.
python scripts/decision_tables/create_decision_table.py \
  --target-org "$ORG" --spec table.json --path tooling
python scripts/decision_tables/create_decision_table.py \
  --target-org "$ORG" --spec table.json --path tooling --confirm

# Edit an Active table with explicit lifecycle commands.
python scripts/decision_tables/deactivate_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName> --confirm
python scripts/decision_tables/update_decision_table.py \
  --target-org "$ORG" --spec table.json --confirm
python scripts/decision_tables/activate_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName> --confirm

# Append CSV data, then activate.
python scripts/decision_tables/upload_decision_table_data.py \
  --target-org "$ORG" --developer-name <CsvTable> --csv rows.csv --confirm
python scripts/decision_tables/activate_decision_table.py \
  --target-org "$ORG" --developer-name <CsvTable> --confirm

# Queue a refresh.
python scripts/decision_tables/refresh_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName> --confirm

# Delete after deactivation and dependency removal.
python scripts/decision_tables/delete_decision_table.py \
  --target-org "$ORG" --developer-name <DeveloperName> --confirm
```

Lifecycle commands are intentionally separate. Update and delete do not
deactivate or reactivate on the caller's behalf; they return Salesforce's own
lifecycle and dependency errors.

## Safety

- Never pass an access token. Authentication belongs to the `sf` CLI.
- Never treat an SF CLI alias as a CCI org alias; their registries are separate.
- Preview mutators before adding `--confirm`.
- Deactivate before updating or deleting an Active table.
- CSV upload is append-only. Replace data with a fresh table rather than relying
  on overwrite behavior.
- Refresh is asynchronous. Confirm completion from `LastSyncDate` or
  `LastIncrementalSyncDate`, not from the queued response alone.

## Verification

```bash
python tests/test_decision_tables_client.py
python tests/test_decision_tables_toolkit.py
python -m compileall -q scripts/decision_tables
```
