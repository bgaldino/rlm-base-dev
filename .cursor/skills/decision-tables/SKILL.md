---
name: decision-tables
description: >-
  Inspect, author, deploy, refresh, and verify Revenue Cloud decision tables. Use when
  lookup data is stale, pricing differs from source data, adding table definitions or
  CSV uploads, comparing orgs, or wiring refresh after catalog, pricing, rate, or
  contract changes.
---

# Decision Tables — Manage, Refresh and Verify

Decision tables are materialised lookups. A refresh reads their source objects and
**copies** rows in; nothing re-reads the source afterwards. So a decision table is a
cache with no invalidation, and every symptom below is the same bug:

> pricing is right in the data and wrong in the quote · a tier does not apply · a
> contracted price is ignored · a new SKU prices as if it did not exist

Use this skill when refreshing, diagnosing, adding, or wiring a decision table, and
whenever an agent is maintaining an org this toolchain built and needs to know whether
its lookups still reflect the data.

It also routes definition authoring, cross-org comparison, CSV upload, and explicit
lifecycle work through the standalone `scripts/decision_tables/` toolkit. Read
`authoring-and-data-model.md` for the definition layer and API vocabularies; read
`lifecycle-and-refresh.md` for deploy, activation, data loading, and refresh details.

## Quick Rules

1. **Refresh after any catalog, pricing, rate or contract change.** `prepare_rlm_org`
   ends with `refresh_all_decision_tables` then `rebuild_search_index` for this reason.
   A build that loads data after those steps leaves stale tables behind.
   **The refresh flow returns before the tables are fresh, so wait before pricing**: rerun
   `check_decision_table_freshness` until the tables your pricing reads are no longer Stale
   (see *Refreshing*).
   Rating setup, qualification and tax tables have no runtime refresh: after editing that
   setup data, use the Manager's **Refresh stale only**, or its **Reads object** filter.
   The exception is the tables the order-activation flow queues itself, and Asset Action Source
   Entries V2 can still read Stale minutes after an activation (`refresh-permissions.md` →
   *The order-activation flow*; wait, then poll before pricing an amendment).
   **The Refresh Decision Table action is admin-only, with measured exceptions**: it queues
   only for a user with Modify All Data *and* Customize Application, unless the flow runs in
   system context without sharing (the contract- and order-activation flows do). The refusal
   is a generic fault that names no permission. Setup's Refresh button, the Connect route,
   Sync Pricing Data and the Manager each have their own gate; the measured matrix is in
   `refresh-permissions.md`.
2. **Check freshness headlessly** — `cci task run check_decision_table_freshness --org "your-cci-alias"`.
   Add `-o param1 strict` to fail a build on any stale table, or `-o param1 json` for the
   dependency map as JSON (`examples-and-platform-facts.md`). Without `strict` the task exits 0 even when tables
   are Stale, so read the counts it prints [Repo: scripts/apex/checkDecisionTableFreshness.apex]. On a Trialforce-spun org,
   `cci flow run check_org_readiness --org "your-cci-alias"` also checks that the search
   index was built in this org (`check_search_index_readiness`).
3. **Freshness is measured against EVERY object a table reads**, not just its source
   object. A table that pulls a column across a lookup goes stale when that lookup's
   record changes, with no row of its own touched.
4. **A refresh must fire when the table's source CRITERIA become true**, not when the
   triggering row is written. See *The timing rule*.
5. **Discover tables from the org; do not trust a hardcoded list** as an inventory.
   `cumulusci.yml`'s `dt_*_decision_tables` lists are refresh *instructions* scoped by
   feature flag, not a census of what exists. `manage_decision_tables -o operation validate_lists`
   compares them to the org and attributes each missing name to the `when:` of the flow
   step that uses its list: a flag-off absence reads as expected, a flag-on one as
   unexpected (`-o strict true` fails on those).
6. **"Not comparable" is a refusal, not a failure.** It means the freshness check
   declined to guess. Only **Stale** is a positive finding.
7. **Definition and data are separate layers.** Editing columns or source bindings does
   not synchronize source rows; refresh (or CSV upload, where applicable) updates the
   materialized data layer.
8. **Deactivate before modifying an Active definition.** Run deactivate, update, and
   activate as separate commands so each platform failure returns independently. All
   mutators preview by default and require `--confirm` to write.

## DO NOT

- **DO NOT** `insert`/`update`/`delete` a `DecisionTable` from Apex. It is a setup object
  and DML on it is rejected **at compile time**, not at runtime — `DML operation Update
  not allowed on List<DecisionTable>`. There is no exception to catch and no runtime
  fallback to write: the class will not deploy. Use Setup, the Metadata API, or the REST
  API.
- **DO NOT** call the `refreshDecisionTable` action from Apex. It is invocable from
  **Flow and REST only**. Apex must bridge through a flow —
  `Flow.Interview.createInterview(...).start()` — which is what
  `RLM_Refresh_Decision_Tables_Bulk` exists for.
- **DO NOT** identify a table by `MasterLabel`. On `DecisionTable` that field is the
  constant string `"Decision Tables"` for every row. Use `DeveloperName` (API name) or
  `SetupName` (display label).
- **DO NOT** hook a refresh to a record's creation when the table's source criteria
  filter on a state that record reaches later.
- **DO NOT** treat a `LastSyncDate` as proof the table holds current rows if the sync
  predates the org. A Trialforce spin inherits the template's timestamps.
- **DO NOT** add a name to a `dt_*_decision_tables` list without confirming the table
  exists in an org **built with that feature flag on**.
- **DO NOT** run destructive toolkit probing against `beta`; use a disposable scratch
  org. Read-only list/describe/diff/trace operations are safe.
- **DO NOT** pass access tokens to toolkit scripts. They delegate authentication to the
  `sf` CLI and take an SF CLI alias via `--target-org`, not a CCI alias.
- **DO NOT** use the raw Connect Definitions POST/PATCH/DELETE resources as a
  toolkit authoring path. Definition writes are Metadata/Tooling-only; Connect is
  used for CSV data/version resources.

## Entry Conditions

Use this skill when you are:

- refreshing decision tables, or deciding whether a refresh is needed
- diagnosing pricing/rating that is correct in the data and wrong at runtime
- adding a decision table, or wiring one into `cumulusci.yml`
- building automation that must fire a refresh at the right moment
- maintaining an org headlessly and needing its readiness state
- inspecting, diffing, tracing, creating, updating, activating, or deleting a definition
- sampling source-backed rows or uploading data to a `CsvUpload` table
- changing `manage_decision_tables` or the `refresh_dt_*` task code (read
  `lifecycle-and-refresh.md` → *The CCI refresh tasks* first)

Not this skill: authoring the pricing procedures that *consume* a lookup
(`.cursor/skills/pricing-wiring/SKILL.md`), or expression-set overlays
(`.cursor/skills/expression-sets/SKILL.md`).

## Toolkit and authoring routes

The standalone toolkit complements the CCI org-build tasks; it does not replace them.
All mutators preview by default and write only with `--confirm`.

| Goal | Route |
|---|---|
| Inventory or inspect definitions | `list_decision_tables.py`, `describe_decision_table.py` |
| Compare orgs/specs | `diff_decision_tables.py` |
| Trace recipe-table mappings | `trace_decision_table.py` |
| Sample the materialized data layer | `dump_decision_table_data.py` |
| Upload `CsvUpload` rows | `upload_decision_table_data.py` |
| Create/update/activate/deactivate/delete | Preview-by-default Tooling commands under `scripts/decision_tables/` |
| Build-critical deploy and refresh | CCI tasks and flows in `cumulusci.yml` |

Start with:

```bash
SF_ORG="your-sf-alias"
TABLE="your-decision-table-api-name"

python scripts/decision_tables/list_decision_tables.py --target-org "$SF_ORG"
python scripts/decision_tables/describe_decision_table.py \
  --target-org "$SF_ORG" --developer-name "$TABLE"
```

Decision tables have two independently managed layers:

1. **Definition** — columns, source binding, criteria, hit policy, and execution shape.
   Metadata API represents it as `.decisionTable-meta.xml`; Tooling spreads it across
   five setup objects. The toolkit writes org definitions through Tooling;
   source-controlled definitions use native Metadata XML with standard `sf` or
   CCI deployment.
2. **Data** — rows copied from source sObjects, uploaded from CSV, or hydrated from a
   Context Definition. The engine does not re-read those rows after materialization.

The complete setup-object model, ID prefixes, metadata shape, and enums are in
`authoring-and-data-model.md`. Deployment paths, active-edit
restrictions, CSV upload, async refresh, and recipe mapping validation are in
`lifecycle-and-refresh.md`. Exhaustive API/error detail lives in
`docs/references/decision-table-api-reference.md`.

## Discovery — what this org actually has

Never trust a hardcoded table list as an inventory. `discovery.md` has the queries that list
the org's tables, their source objects, criteria and columns, and the `DecisionTableParameter`
edge cases (`DomainObject` holding the literal string `'null'`, and naming only the final
field of a path).

## Freshness — what the verdicts mean

`check_decision_table_freshness` and the **Decision Table Manager** component share one
implementation (`RLM_DecisionTableManagerController`); the task calls the same method the
component does, so they cannot disagree.

| Verdict | Means |
|---|---|
| **Fresh** | The last sync — full or incremental, whichever is later — is later than the newest change **visible to the running user** in *every* object the table reads. Scoped on purpose — see limit 3 below. The reason says which sync it rests on. |
| **Stale** | Something the table reads changed **at or after** the sync. The reason names the object that drove it, and says so explicitly when the two timestamps tie. |
| **Not comparable** | The check refused to guess — a source criterion it could not faithfully reproduce, a dependency it could not check, sharing that can hide rows of an object it reads from the running user (limit 3), or no sObject behind the table at all (`CsvUpload`, `ContextDefinition`, whose freshness is the upload or the Context Definition, not a record timestamp). Compare by hand. |
| **Unknown** | The source could not be read: no source object recorded, the object missing from this org, no permission on it, or its probe failed. |

Two limits apply to **every** verdict, by construction. A third is listed and **closed**,
so it is not reintroduced:

1. A **deleted** source row leaves no timestamp behind.
2. ✅ **Closed.** A row edited **out of** a filter takes its timestamp with it, so a
   filtered probe stops seeing it while the table still holds the copy made before the
   edit — a false Fresh. The unfiltered probe is now folded into the change comparison,
   so the edit is seen. The cost is over-reporting Stale when a row the table *excludes*
   changes, which is the sanctioned direction. A filtered table's **row count** still
   covers only matching rows; its **change comparison** covers the whole object.
3. Probes run in `USER_MODE`, so they see only rows the running user can see. ⚠ **Run the
   check as an operator with org-wide read.** A row hidden from the caller by sharing and
   modified after the sync is invisible to the probe, and the failure direction is the bad
   one — Fresh while stale. Every verdict says "visible" for this reason. The Manager is on
   the shared Home page, so a restricted persona can run it and get a verdict scoped to
   their own view. **Narrowed:** Fresh is withdrawn to Not comparable, naming the object,
   when a table reads an object whose sharing can hide rows from the caller (Private, or
   controlled by a Private master) and the caller lacks View All. On 264 that is IndexRate
   and BindingObjectRateCardEntry for the salesrep persona (7 tables). Every probed object
   counts, including those a source criterion traverses. Still unchecked: restriction rules
   and external users' sharing.

Within what its probes can observe, the design deliberately trades coverage for not
guessing: an unnecessary refresh is cheap, a false all-clear is not. Over-refusing into
"Not comparable" is the intended failure direction.

⚠ **That is a scoped claim, not a guarantee, and the two open limits above are exactly
why.** A deleted source row and a row hidden from the caller by sharing are both invisible
to a timestamp probe, so either can leave a genuinely stale table reported **Fresh**. No
amount of refusing helps there — the check never sees the change to refuse over it. Treat
a Fresh verdict as a readiness signal about what the caller can see, not as proof the
table is current, and **do not present it as one**: it is not a substitute for refreshing
after a known data load or a deletion. The same principle settles the boundary:
a sync stamped at the **same instant** as the newest change reads **Stale**, because a
tie establishes no ordering — nothing says whether the sync's read snapshot included
that write. The reasoning behind each refusal is documented in the controller's class
header — read it there rather than re-deriving it.

## Refreshing

| Path | Use when |
|---|---|
| `cci flow run refresh_all_decision_tables --org "your-cci-alias"` | After a build, a data load, or any catalog/pricing change. Flag-scoped. |
| The **Decision Table Manager** component (Home page, utilities accordion) | Interactive: per-table refresh (admin only, see rule 1), status polling, why a table is stale. |
| Setup → Decision Tables | One Active table, manually. Refresh worked for Customize Application plus one of Modify All Data, Rule Engine Designer or Salesforce Pricing Design Time User (with a designer set, the user also needed read access to the table's source object); neither admin permission alone worked, with or without read access (rule 1). |
| `RLM_Refresh_Decision_Tables_Bulk` flow | From Apex or another flow — the only way Apex can reach the refresh action. Measured from a `with sharing` Apex class that starts it as the Manager does: queued for an admin, not for a user with neither admin permission; from `without sharing` Apex it queued for that user (rule 1). |

An **incremental** sync advances `LastIncrementalSyncDate` and usually does not move
`LastSyncDate` (a first incremental was measured stamping both). ⚠ In Release 264 a **request that did not ask for incremental can run as incremental**: unless
incremental is requested, the platform chooses the type itself (org preference
`AutoSelectRefreshDT`, whose Setup toggle is an opt-out). So judge a refresh by the
later of the two stamps; see `lifecycle-and-refresh.md` → *Release 264 chooses the
refresh type*.

### Wait for fresh tables before pricing

`refresh_all_decision_tables` returns before the tables are fresh. The table refreshes it
queues finish later (`lifecycle-and-refresh.md` → *Queued is not refreshed*), and so did the
cost book table, which none of those refreshes names.
Measured on two fresh 264 `ent-sb0` scratch orgs on 2026-11-11:

- On one, the tier, bundle-adjustment and cost tables stayed Stale for about three minutes after
  the flow returned, then reached zero Stale.
- On the other, a quote priced about half a minute after the flow returned got empty volume and
  cost lookups, while its bundle adjustment applied. The volume step ran and left the price
  unchanged, the line had no unit cost, and no error was raised.

Why a lookup returns nothing while a refresh runs is not established. Source reading shows each
refresh's data is kept separately, keyed by table and refresh time, and the superseded copy is
normally removed after the new one completes (purging is disabled in some paths). It did not show whether a lookup during a refresh reads the
old, an empty or a partial copy. `[Platform behaviour, traced in part]` Treat the empty result
above as measured only, and do not assume stale-but-complete data while a refresh is running.

Before pricing, rerun `check_decision_table_freshness` until the tables your pricing reads (here
the volume tier, bundle adjustment and cost book tables) are no longer Stale.

## The timing rule

> **A refresh must fire when the table's source criteria become TRUE — not when the
> triggering row is written.**

For example, if a table filters on
`...ContractId.StatusCode = 'Activated'`, refreshing at contract creation excludes
those rows and still advances `LastSyncDate`. Refresh when the contract becomes
Active instead.

Before wiring any automatic refresh:

1. Read the table's `DecisionTableSourceCriteria`.
2. Ask what state a source row must be in to satisfy them.
3. Fire the refresh when a row **reaches** that state, not when it is created.

⚠ Also: an unhandled fault in a record-triggered **after-save** flow rolls back the
triggering DML. A refresh that fails must not take the contract with it.

## Wiring a new table into the build

1. Add the metadata under the appropriate `unpackaged/post_*/decisionTables/`.
2. Add its **`DeveloperName`** to the matching `dt_*_decision_tables` anchor in
   `cumulusci.yml` — the one whose feature flag gates the same functionality.
3. Verify against an org built **with that flag on**. A name in a flag-gated list is
   absent from an org where the flag is off, and that is correct, not drift.
4. Regenerate the CCI reference: `python scripts/ai/generate_cci_reference.py`.

## Platform facts and worked examples

`examples-and-platform-facts.md` holds the platform-facts table (setup-object DML,
`MasterLabel`, source counts, Trialforce stamps) and worked examples: readiness check, strict
gate, the table-to-object map, "pricing looks wrong and the data looks right".

## Validation Checks

- `python tests/test_decision_tables_toolkit.py` passes offline.
- `python scripts/ai/skill_manifest.py --check` resolves this skill and its sub-files.
- `cci task run check_decision_table_freshness --org "your-cci-alias"` reports every table with a
  verdict, and the count matches the `DecisionTable` row count in the org.
- After `refresh_all_decision_tables` and its refreshes finish, no table is Stale.
- A table you deliberately made stale (edit any object it reads) flips to Stale and the
  reason names that object.
- Any name added to a `dt_*_decision_tables` list resolves to a real `DeveloperName` in
  an org built with that feature flag on.

## Related

- `.cursor/skills/decision-tables/authoring-and-data-model.md` — Tooling setup objects,
  metadata shape, enums, and the definition/data model.
- `.cursor/skills/decision-tables/discovery.md` — queries that inventory an org's tables.
- `.cursor/skills/decision-tables/refresh-permissions.md` — who can refresh, by surface and user,
  and the order-activation flow.
- `.cursor/skills/decision-tables/examples-and-platform-facts.md` — platform facts, worked examples.
- `.cursor/skills/decision-tables/lifecycle-and-refresh.md` — explicit lifecycle,
  deployment, upload, refresh, and recipe-table mappings. Its *The CCI refresh tasks*
  section is the one record of why `manage_decision_tables` and `refresh_dt_*` are built
  as they are; read it before changing either task.
- `scripts/decision_tables/README.md` — standalone toolkit commands and safety model.
- `docs/references/decision-table-api-reference.md` — exhaustive API and error reference.
- `docs/references/decision-table-examples.md` — CCI operations cookbook.
- `.cursor/skills/pricing-wiring/SKILL.md` — the procedures and plans that consume these
  lookups, and the timing rule in its pricing context.
- `.cursor/skills/troubleshooting/SKILL.md` — build and deploy failures.
- `RLM_DecisionTableManagerController` class header — the freshness reasoning in full,
  including why each refusal exists.
