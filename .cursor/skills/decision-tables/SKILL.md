# Decision Tables — Inspect, Author & Manage (BRE)

Use this skill when reading, authoring, or managing a Business Rules Engine
**Decision Table** — the lookup tables a pricing recipe (or any BRE expression
set) consults to resolve an output value from a set of input conditions.
Covers the **definition** layer (columns + source binding, across three
authoring APIs), the **data** layer (source rows + async refresh), and the
lifecycle (deploy / activate / deactivate / refresh). Consumable by any AI agent
(Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

For where Decision Tables fit the **pricing** layering model (recipes →
recipe-table mappings → procedure plans), read
`.cursor/skills/pricing-wiring/SKILL.md`. For the **expression sets** that
*consume* a table's output, see `.cursor/skills/expression-sets/SKILL.md`.

> **Pinned to Release 262 / API v67.0.** Re-verify enums and behavior on the
> target release at merge time. This `SKILL.md` is the task-level entry point;
> deep detail lives in two companion files (read on demand):
> - **`authoring-and-data-model.md`** — the 5 Tooling setup objects + ID
>   prefixes + the `Metadata` complexvalue; the `.decisionTable-meta.xml` shape;
>   the three authoring paths + the field-name divergence table; full enum
>   catalog; the definition-vs-data two-layer model in depth.
> - **`lifecycle-and-refresh.md`** — deploy paths + source locations;
>   active-edit restriction → deactivate/exclude/restore; activate/deactivate;
>   refresh in depth (full vs incremental, the live-verified payload field name,
>   async + 100/hr); recipe-table mappings + `validate_lists`; a brief runtime
>   note.
>
> The exhaustive object/ID/enum/error reference is
> `docs/references/decision-table-api-reference.md`; the ops/task cookbook is
> `docs/references/decision-table-examples.md`; the standalone helper toolkit
> lives at **`scripts/decision_tables/`** (see its `README.md` and the
> [script routing table](#script-routing) below).

## <a name="two-layer-model"></a>The two-layer model (read this first)

A Decision Table is **two layers**, and every task below is really about one of
them:

1. **Definition** — the columns (INPUT / OUTPUT / ROWCRITERIA), the source
   binding, the hit policy, and the row-filter criteria. Lives in **Metadata
   API** (`.decisionTable-meta.xml`) and, equivalently, across **5 Tooling API
   setup objects**. `describe` / `diff` / `trace` operate here.
2. **Data** — the rows the engine actually evaluates: records in the
   `sourceObject` (`SingleSobject` / `MultipleSobjects`), an uploaded CSV
   (`CsvUpload`), or runtime-hydrated rows (`ContextDefinition`). Rows are synced
   into the BRE engine cache by the **async `refreshDecisionTable` action**
   (~100/hr). `dump` samples this layer; for `CsvUpload`, `upload` loads it (a
   two-phase ContentVersion → Connect `/file` POST — see `lifecycle-and-refresh.md`).

**Editing the definition ≠ refreshing the data.** A definition change is
deployed; a data change is picked up by a refresh. A definition change is not
live to the engine until a refresh completes.

## <a name="dt-shapes"></a>Decision Table shapes (usageType × dataSourceType × executionType)

Three orthogonal axes describe any table. Grounded live (`rlm-base__beta` +
scratch, 2026-07-09); observed values in **bold**.

| Axis | Field (MD / Tooling · Connect) | Values | What it controls |
|---|---|---|---|
| **What consumes it** | `usageType` | **DefaultPricing**, **DefaultRating**, **PricingDiscovery**, **RatingDiscovery**, **RevenueStandardTax**, Bre, ProductQualification, … | Which engine/recipe reads the table (pricing vs rating vs discovery vs tax). |
| **Where the rows come from** | `dataSourceType` · `sourceType` | **SingleSobject**, **MultipleSobjects**, CsvUpload, ContextDefinition | The data layer + which read/refresh path applies. |
| **How it's executed** | `executionType` | **HBASE**/`Hbase`, **DLO** (v67.0+, replaces DMO), HBPO, SOLR, SOQL | The engine/storage backend evaluating lookups. |

Two more definition-level knobs: the **hit policy**
(`filterResultBy` · `decisionResultPolicy`: **OutputOrder**, FirstMatch,
Priority, RuleOrder, UniqueValues, CollectOperator, AnyValue) decides which
matching row(s) win; the **condition** (`conditionType` **All**/Any/Custom +
`conditionCriteria` boolean logic over INPUT `sequence` numbers) decides how
INPUT columns combine. Full enum catalog in `authoring-and-data-model.md`.

## Quick Rules

1. **`--target-org` is the SF CLI alias, never the CCI alias.** CCI alias `beta`
   → SF CLI alias `rlm-base__beta`. Toolkit + `sf` commands take the SF CLI
   alias; CCI tasks take the CCI alias. No access token is ever passed — auth is
   delegated to the `sf` CLI.
2. **The 5 setup objects are Tooling API only** (`DecisionTable` `0lD`,
   `DecisionTableParameter` `0lP`, `DecisionTableDatasetLink` `0lX`,
   `DecisionTblDatasetParameter` `0lZ`, `DecisionTableSourceCriteria` `0VT`).
   They are **not** on the normal REST `/sobjects` surface — read them via
   `/tooling/query` + `/tooling/sobjects`. `PricingRecipeTableMapping` and
   source-object rows *are* normal REST.
3. **Definition ≠ data.** Deploying/editing the definition does not sync rows;
   only the async `refreshDecisionTable` action does — capped **~100/hr**. See
   [the two-layer model](#two-layer-model).
4. **An Active table can't be edited in place.** Modifying or deleting an
   existing artifact on an **Active** table is platform-blocked (consistent with
   Context Service's `RECORD_UPDATE_FAILED` deactivate-first rule). Deactivate →
   edit → reactivate. Add-only inserts may apply in place — confirm per path.
5. **Three authoring paths, three vocabularies.** Metadata/Tooling use
   `dataSourceType` / `filterResultBy` / `decisionTableParameters` /
   `usage=INPUT`; **Connect** uses `sourceType` / `decisionResultPolicy` /
   `parameters` / `usage=Input` + a **15-char** id. Never read Metadata-API keys
   off a Connect response (`dataSourceType` comes back `null`). See the
   field-name divergence table in `authoring-and-data-model.md`.
6. **The refresh flag is `isDecisionTableIncremental`** (the action's accepted
   input), **not** `isIncremental` — which the current CCI tasks
   (`rlm_refresh_decision_table.py`, `rlm_manage_decision_tables.py`) send. The
   toolkit's `refresh_decision_table.py` uses the correct name (live-verified);
   the tasks are a candidate follow-up fix. See `lifecycle-and-refresh.md`.
7. **Inspector reads are safe; mutators are preview-by-default.** The inspectors
   (`list` / `describe` / `diff` / `trace` / `dump`) only ever GET/SOQL — safe on
   any org, including `beta`. The mutators (`create` / `update` / `activate` /
   `deactivate` / `refresh` / `delete` / `upload`) run dry-run unless `--confirm`,
   and an
   **update never lets the spec's `status` drive the table's lifecycle** — the
   lifecycle engine alone owns activate/deactivate. (A Tooling `Metadata` PATCH
   *requires* `status`, so the `update` CLI stamps the table's **current live**
   status — during a deactivate-first sequence, the already-deactivated
   `Inactive` — never the spec's; the Connect path simply drops it.) Destructive
   testing on **scratch orgs only**.
8. **CCI tasks remain the org-build path.** `deploy_decision_tables`,
   `manage_decision_tables`, `refresh_decision_table`,
   `configure_pricing_recipe_table_mappings`, and the `.skip/` exclude pattern
   own the build. The toolkit is for **ad-hoc inspection and one-off lifecycle
   outside** the build — it doesn't duplicate the tasks' logic. Route, don't
   rebuild (see [The CCI tasks](#cci-tasks)).
9. **CsvUpload data layer: append only, and it's async + silent about bad rows.**
   `deleteAllRows:true` (`upload --overwrite`) is **BROKEN on 262/v67.0** (loads 0
   rows, `uploadStatus=Failed`, existing rows kept) — to replace rows, create a
   fresh version/table and append. Re-uploading does **not** mint a v2. Rows whose
   cell fails the column's `dataType` coercion **drop silently** →
   `CompletedWithErrors`; encodings are strict (**DateTime** needs
   `YYYY-MM-DDTHH:MM:SS.sssZ`, **Boolean** only `true`/`false`, **Percent** stored
   verbatim — no ×100). `upload --wait-for-status` is the only signal rows were
   dropped. Read back with `dump --filter FIELD:VALUE` (exact/case-sensitive; a
   bad field name → 0 rows, no error) / `--version-number N`. Detail in
   `authoring-and-data-model.md` → *CSV Based tables*.

## DO NOT

- **DO NOT** run destructive probing (create / update / activate / deactivate /
  refresh / delete) against the shared `beta` org — use a **disposable scratch
  org** only. Read-only smoke (`list`/`describe`/`trace`/`dump`) is fine on
  `beta`.
- **DO NOT** confuse the **CCI alias** with the **SF CLI alias** (Quick Rule 1).
  A toolkit CLI given a bare CCI alias like `beta` will fail to resolve the org.
- **DO NOT** modify or delete an existing artifact on an **Active** table
  (Quick Rule 4) — deactivate first. Watch for `RECORD_UPDATE_FAILED`-style
  "cannot modify an active…" errors as the signal you skipped this.
- **DO NOT** read Metadata-API field names (`dataSourceType`, `filterResultBy`,
  `isVersioned`) off a **Connect** Definitions response — Connect returns them
  `null` and populates its own (`sourceType`, `decisionResultPolicy`). Use the
  divergence table.
- **DO NOT** send `isIncremental` to `refreshDecisionTable` expecting an
  incremental sync — the accepted flag is `isDecisionTableIncremental`
  (Quick Rule 6).
- **DO NOT** assume `PricingRecipeTableMapping` has a `DecisionTableId` field —
  it does not. Correlate on `LookupTableId` (== `DecisionTable.Id`, SObject-backed)
  or `FileBasedDecisionTableName` (== DeveloperName, file/CSV-backed).
- **DO NOT** edit the `.decisionTable-meta.xml` `executionType` casing to match
  an API read — source XML uses `Hbase`, the APIs return `HBASE`; keep each
  representation's native casing.
- **DO NOT** treat a deployed/edited definition as live to the engine without a
  successful **refresh** (Quick Rule 3); it is rate-limited and async.

## Entry Conditions

| Situation | Use |
|---|---|
| List / describe / diff / trace / dump a table without mutating it | This skill → [script routing](#script-routing) (read-only inspectors) |
| Create / update / activate / deactivate / refresh / delete a table (one-off) | The [toolkit mutators](#script-routing) (preview-by-default; `--confirm`, scratch orgs only); build path = the CCI tasks |
| The 5 setup objects, `Metadata` complexvalue, metadata XML shape, enum catalog, field-name divergence, two-layer model in depth | `authoring-and-data-model.md` |
| Deploy / activate / deactivate / refresh / recipe-mapping / `validate_lists` detail | `lifecycle-and-refresh.md` |
| Where DTs fit in the **pricing** setup order (recipes, table mappings, plans) | `.cursor/skills/pricing-wiring/SKILL.md` |
| The expression sets that **consume** a table's output | `.cursor/skills/expression-sets/SKILL.md` |
| Object/ID model, full enums, **every error + resolution**, verification checklist | `docs/references/decision-table-api-reference.md` |
| `manage_decision_tables` / refresh **ops examples** (CCI task command lines) | `docs/references/decision-table-examples.md` |
| Writing the Python task class itself | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |

## <a name="quick-start"></a>Quick Start

List → describe → trace → dump, using the standalone toolkit (`--target-org` is
the **SF CLI** alias, never the CCI alias):

```bash
ORG=rlm-base__beta

# 1. What's in the org, grouped by usageType.
python scripts/decision_tables/list_decision_tables.py --target-org $ORG

# 1a. Filter to active pricing tables.
python scripts/decision_tables/list_decision_tables.py --target-org $ORG \
    --status Active --usage-type DefaultPricing

# 2. Pretty-print one table's full definition (columns / dataset links / criteria).
python scripts/decision_tables/describe_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries

# 2a. Also show the Connect Definitions vocabulary side by side.
python scripts/decision_tables/describe_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries --connect

# 3. Which pricing recipes reference this table?
python scripts/decision_tables/trace_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries

# 4. Diff the same table across two orgs (e.g. a scratch clone vs beta).
python scripts/decision_tables/diff_decision_tables.py \
    --target-org rlm-base__scratch --developer-name RLM_CostBookEntries \
    --other RLM_CostBookEntries --other-org $ORG

# 5. Sample the data layer (branches on dataSourceType).
python scripts/decision_tables/dump_decision_table_data.py --target-org $ORG \
    --developer-name RLM_CostBookEntries --limit 5
```

## <a name="script-routing"></a>Task + script routing

Two independent surfaces cover Decision Table work — the **CCI tasks** (build
work) and the standalone **`scripts/decision_tables/` toolkit** (read-only
inspection + guarded, one-off lifecycle mutators; `sf`-CLI transport, no access
token). They share no code; the toolkit mirrors the tasks' live-verified rules.
Full toolkit detail: `scripts/decision_tables/README.md`.

| I need to… | Use |
|---|---|
| List every DT in an org, grouped by usageType | `python scripts/decision_tables/list_decision_tables.py --target-org <sf_alias>` (read-only) |
| Pretty-print one table's full definition | `python scripts/decision_tables/describe_decision_table.py --target-org <sf_alias> --developer-name <name> [--connect]` (read-only) |
| Structurally diff two tables (or one across two orgs) | `python scripts/decision_tables/diff_decision_tables.py --target-org <sf_alias> --developer-name <a> --other <b> [--other-org <sf_alias2>]` (read-only) |
| **Trace** which pricing recipes reference a table | `python scripts/decision_tables/trace_decision_table.py --target-org <sf_alias> --developer-name <name>` (read-only) |
| Sample the **data layer** (branches on dataSourceType) | `python scripts/decision_tables/dump_decision_table_data.py --target-org <sf_alias> --developer-name <name> --limit 5` (read-only); for a `CsvUpload` table also `--filter FIELD:VALUE` (exact/case-sensitive; drops `--limit`) / `--version-number N` |
| **Upload CSV rows** into a `CsvUpload` table's data layer (two-phase) | `python scripts/decision_tables/upload_decision_table_data.py --target-org <sf_alias> --developer-name <name> --csv rows.csv [--activate-version N] [--wait-for-status]` (preview; `--confirm` to write). **Append is the only reliable write — `--overwrite` FAILS on 262/v67.0**; `--wait-for-status` surfaces silent per-row drops (`CompletedWithErrors`). |
| Create / update / activate / deactivate / refresh / delete a DT (one-off) | `python scripts/decision_tables/{create,update,activate,deactivate,refresh,delete}_decision_table.py --target-org <sf_alias> …` (preview; `--confirm` to write; **scratch orgs only** for destructive verbs) |
| List / query / refresh / activate / deactivate / validate mappings **in the build** | The CCI tasks — see [The CCI tasks](#cci-tasks) |

---

## <a name="cci-tasks"></a>The CCI tasks (route here for build work)

These own the org-build lifecycle. The toolkit complements them; it does not
replace them. `--org` here is the **CCI alias**.

| Task / flow | Does | Notes |
|---|---|---|
| `deploy_decision_tables` | Deploys `.decisionTable-meta.xml` from `unpackaged/pre/5_decisiontables/` | The shipped definition-deploy path. |
| `deploy_post_prm_pricing_decision_tables` | Deploys PRM-pricing tables (`unpackaged/post_prm_pricing/decisionTables/`) | Uses `replace_record_id_query` to resolve `DecisionTable` Ids. |
| `manage_decision_tables` | `-o operation list\|query\|refresh\|activate\|deactivate\|validate_lists` | `validate_lists` compares the org to the project list anchors — the authoritative recipe/table validator. |
| `refresh_decision_table` | Invokes `refreshDecisionTable` for named tables | ⚠ Sends `isIncremental` (see Quick Rule 6 — accepted flag is `isDecisionTableIncremental`). |
| `deactivate_decision_tables` | Apex `deactivateDecisionTables.apex` | Bulk deactivate. |
| `exclude_active_decision_tables` | Moves active tables' XML into `.skip/` before a deploy | The active-edit-restriction workaround (deactivate-then-redeploy). |
| `configure_pricing_recipe_table_mappings` | Ensures `PricingRecipeTableMapping` rows (Tooling API, no deploy) | The recipe→table wiring `trace` reads. |

Full command-line examples: `docs/references/decision-table-examples.md`.

---

## Definition + data + lifecycle (summary)

The **definition** spans three APIs with divergent vocabularies (Metadata /
Tooling `Metadata` complexvalue / Connect Definitions), assembled across the 5
Tooling setup objects; the **data** layer branches on `dataSourceType`; and the
lifecycle is deploy → activate → (edit needs deactivate-first) → refresh (async,
100/hr). The setup-object model + ID prefixes + `Metadata` keys + the metadata
XML shape + the full enum catalog + the field-name divergence table + the
two-layer model in depth live in **`authoring-and-data-model.md`**; the deploy
paths + activate/deactivate + refresh depth + recipe-table mappings +
`validate_lists` live in **`lifecycle-and-refresh.md`** — read the relevant one
before authoring or a lifecycle change.

---

## Performance Expectations

- **Read CLIs** (`list` / `describe` / `diff` / `trace` / `dump`): a few seconds
  each (one or a handful of Tooling/REST round-trips).
- **Refresh** is **async and rate-limited to ~100/hr** — it returns a tracker,
  not a synchronous result; the rows are not live until it completes. Do not
  loop refreshes in a tight build step.
- **Definition deploy** is a normal Metadata API deploy; activation may report
  `ActivationInProgress` briefly.

---

## Examples

- **Read-only cookbook:** the [Quick Start](#quick-start) above and
  `scripts/decision_tables/README.md`.
- **CCI task command lines** (list/query/refresh/activate/deactivate/
  validate_lists): `docs/references/decision-table-examples.md`.
- **A real shipped definition** to model an author against:
  `unpackaged/pre/5_decisiontables/RLM_CostBookEntries.decisionTable-meta.xml`
  (annotated in `authoring-and-data-model.md`).

---

## Validation Checks

Run before a PR that touches the toolkit, the skill, or the reference doc:

```bash
# Offline toolkit unit tests (self-contained check() runner — no org, no sf, no pytest)
python tests/test_decision_tables_toolkit.py        # expect: all pass

# Live read-only smoke (safe on beta or a scratch org)
ORG=rlm-base__beta
python scripts/decision_tables/list_decision_tables.py --target-org $ORG
python scripts/decision_tables/describe_decision_table.py --target-org $ORG --developer-name RLM_CostBookEntries
python scripts/decision_tables/trace_decision_table.py  --target-org $ORG --developer-name RLM_CostBookEntries
python scripts/decision_tables/dump_decision_table_data.py --target-org $ORG --developer-name RLM_CostBookEntries --limit 5

# Skill manifest well-formed + decision-tables listed
python scripts/ai/skill_manifest.py --check
python scripts/ai/skill_manifest.py --list-skills foundations
```

Checklist:

- [ ] `--target-org` is the **SF CLI** alias, not the CCI alias.
- [ ] Read CLIs run clean; `dump` on a `CsvUpload` table reads the Connect
      `/data` GET (rows land via `upload_decision_table_data.py`; an empty or
      gated table degrades to a note).
- [ ] Any destructive probing ran on a **scratch org**, never `beta`.
- [ ] After `cumulusci.yml` task/option edits:
      `python scripts/ai/generate_cci_reference.py` and commit the regenerated
      reference.
- [ ] Doc consistency: the reference doc, `decision-table-examples.md`, and this
      skill cross-link each other (`.cursor/skills/doc-consistency/SKILL.md`).

---

## Related References

- **Sub-files (progressive disclosure):** `authoring-and-data-model.md` (setup
  objects, metadata shape, enums, two-layer model) and `lifecycle-and-refresh.md`
  (deploy, activate/deactivate, refresh, recipe mappings).
- **Standalone toolkit (inspect / diff / trace / dump + guarded lifecycle
  mutators, preview-by-default, no access token):** `scripts/decision_tables/README.md`.
- **Exhaustive detail (object/ID model, enum catalog, field-name divergence,
  Connect endpoints, refresh field name, every error + resolution):**
  `docs/references/decision-table-api-reference.md`.
- **CCI ops examples:** `docs/references/decision-table-examples.md`.
- **CCI tasks:** `tasks/rlm_manage_decision_tables.py`,
  `tasks/rlm_refresh_decision_table.py`,
  `tasks/rlm_exclude_active_decision_tables.py`,
  `tasks/rlm_configure_pricing_recipe_table_mappings.py`.
- **Pricing layering model (recipes → recipe-table mappings → plans → context):**
  `.cursor/skills/pricing-wiring/SKILL.md`.
- **Expression sets that consume a table's output** (via a
  `GetOutputsFromDecisionTable` step): `.cursor/skills/expression-sets/SKILL.md`.
- **Context Service** — a table with `dataSourceType=ContextDefinition` draws its
  rows from a Context Definition hydrated at runtime (no static table to `dump`),
  and a decision table is itself one of the consumers that can block a context
  definition's deactivation. When the `context-service` skill is present in the
  repo, see its `SKILL.md` for that side of the relationship.
- **Writing the Python task class:**
  `.cursor/skills/cci-orchestration/custom-task-authoring.md`.
