# Expression Sets — Programmatic CRUD & Overlay Authoring

Use this skill when reading or mutating a BRE **Expression Set** (pricing
procedure, constraint procedure, qualification/discovery/rating procedure, …)
programmatically — via the **Connect API** (runtime/programmatic CRUD) or the
**Metadata API** (source-controlled authoring) — including building declarative
overlays that add/remove/update steps and variables. It is consumable by any AI
agent (Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

Expression Sets back more than pricing — Revenue Cloud uses **six**
`interfaceSourceType` values (see [Expression Set types](#expression-set-types)),
so this skill is generic to the Expression Set engine. For where Expression Set
CRUD fits into the **pricing** layering model (recipes, recipe-table mappings,
procedure plans, context definitions), read
`.cursor/skills/pricing-wiring/SKILL.md`.

> **Pinned to Release 262 / API v67.0.** Re-verify enums and behavior on the
> target release at merge time. This `SKILL.md` is the task-level entry point;
> deep detail lives in three companion files (read on demand):
> - **`authoring-and-overlays.md`** — building/applying overlays, capturing a
>   step's three dependency scopes, safe step removal.
> - **`metadata-vs-connect.md`** — the two authoring paths, the Connect mutation
>   lifecycle, verb-specific field rules, GET serializer gotchas, Metadata API
>   authoring, create-with-content.
> - **`docs/references/expression-set-connect-api-reference.md`** — the
>   exhaustive object/ID model, OAS-confirmed schema enums, every known error +
>   resolution, and the verification checklist.
>
> The standalone helper toolkit lives at **`scripts/expression_sets/`** (see its
> `README.md` and the [script routing table](#script-routing) below).

## <a name="expression-set-types"></a>Expression Set types (Revenue Cloud)

Every Expression Set carries an `interfaceSourceType` (the consuming-cloud
discriminator, on the runtime `ExpressionSet` object) paired with a `usageType`.
The engine enum has 11 members (see the [full enum](#the-full-enum) below), but
**Revenue Cloud uses six** — grounded against the live org
(`SELECT InterfaceSourceType, UsageType, COUNT(Id) FROM ExpressionSet …`) and the
Release 262 dev-guide/Help snapshots:

| `interfaceSourceType` | What it computes / when it runs | Paired `usageType` (live) | Shipped example(s) in this repo | Authoring |
|---|---|---|---|---|
| **PricingProcedure** | The pricing waterfall — list price → discounts → derived/rounded net price. Runs on quote/order repricing. | `DefaultPricing` | `RLM_DefaultPricingProcedure`, `RLM_ProductDiscoveryPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Price_Distribution_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | Step graph (this skill) |
| **DiscoveryProcedure** | Product Discovery pricing — computes prices shown while browsing/adding products (pre-quote). | `PricingDiscovery` | `RLM_DefaultPricingDiscoveryProcedure`, `Salesforce_Pricing_Discovery_Procedure` | Step graph (this skill) |
| **RatingProcedure** | Usage/consumption rating — turns usage into rated amounts. | `DefaultRating` | `RLM_DefaultRatingProcedure`, `Negotiable_Rating_Procedure` | Step graph (this skill) |
| **RatingDiscoveryProcedure** | Rating discovery — the discovery-phase counterpart for rating. | `RatingDiscovery` | `RLM_DefaultRatingDiscoveryProcedure` | Step graph (this skill) |
| **QualificationProcedure** | Product qualification/disqualification — eligibility gating in Product Discovery. | `ProductQualification` | `RLM_ProductDiscoveryQualificationProcedure` | Step graph (this skill) |
| **Constraint** ⚠ | Product Configurator constraint rules — compatibility/recommendation logic (GA 262 "Product Discovery with Constraint Rules"). | `Constraint` | *(shipped as constraint models, not `expressionSetDefinition` step XML)* | **CML** — see note |

> ⚠ **Constraint is CML-based, not a step graph.** Unlike the other five,
> Constraint expression sets are authored in **CML** (Constraint Modeling
> Language) via the Configurator Constraint Builder / CML editor, not as a flat
> `steps[]` graph. The Connect-overlay tooling and `steps[]`/`parentStep` model
> in this skill **do not apply** to Constraint sets. They surface in the same
> `ExpressionSet`/`interfaceSourceType` enum, so they
> are listed here for completeness; deep CML authoring guidance is **deferred to
> future work** (see the CML docs under `docs/salesforce/262/dev-guide/` —
> `cml_*` articles — and the Configurator Help suite).

### <a name="the-full-enum"></a>The full enum vs. Revenue Cloud

The `interfaceSourceType` enum (`INTERFACE_SOURCE_TYPES` in
`tasks/expression_set_schema.py` — **the single source of truth**) has 11 members.
The five **not** used by Revenue Cloud belong to other clouds/verticals and are
listed only so an unexpected value isn't mistaken for RC:

- **Not Revenue Cloud:** `EventOrchestration`, `GpaCalculationProcedure`,
  `IntelligentDecisionStudio`, `ItServiceManagement`.
- **Doc/test placeholder (not a real RC type):** `Sample` — appears only as the
  dev-guide's own "Declarative Metadata Sample Definition" example; **0** live
  instances. Do not author RC procedures with it (`usageType: sample` also keeps
  the ES from surfacing in the pricing UI).

Ground truth: the code enum (`tasks/expression_set_schema.py`) →
`validate_expression_set` errors on an out-of-enum value. The
`docs/references/expression-set-connect-api-reference.md` enum list mirrors it.

## Quick Rules

1. **Choose the path by use case.** **Metadata API** (`expressionSetDefinition`
   XML + deploy) for source-controlled, git-tracked changes; **Connect API**
   (`tasks/rlm_expression_set_connect.py`) for runtime/programmatic CRUD. The
   step/param/variable shapes are identical, so a step authored once works for
   both.
2. **Every Connect mutation must HTML-unescape the payload before sending**
   (`normalize_html_entities`, default on). Raw GET output is HTML-escaped
   (`&quot;`/`&#39;`) and the engine rejects the entities. The Metadata path
   needs no equivalent — the XML parser decodes entities before the engine sees
   them.
3. **Run the pre-flight validator on any payload before a Connect call**
   (`validate_expression_set`, or `python scripts/ai/validate_expression_set.py`).
4. **The step graph is flat.** One `steps[]` array; hierarchy is encoded by
   `parentStep` (a step **name**), not nested arrays. Read `sequenceNumber` for
   execution order — GET returns top-level steps **alphabetically by name**, and
   `sequenceNumber` is **scoped per parent** (children restart at 1).
5. **Build `addSteps` overlays by capturing from a live GET**, not hand-authoring.
   Slice top-level steps and child steps differently (see `authoring-and-overlays.md`).
6. **Capture a step's dependencies, not just the step** — classify every
   referenced name into one of three scopes (version variable → `addVariables`;
   custom external dep → `externalDependencies`; standard context → nothing).
7. **Mutations run deactivate → modify → reactivate**, in a guarded `finally`;
   the tasks enforce this, including the procedure-plan cascade.
8. **Test Connect CRUD on a disposable clone** (POST-create a renamed copy),
   never the shipped procedure — except for an intentional, approved change.

## DO NOT

- **DO NOT** send raw Connect GET output back in a PATCH/POST without
  HTML-unescaping it first — the escaped `&quot;`/`&#39;` values make engine parsing fail
  (flat: `Syntax error. Found '&'`; nested: opaque `INVALID_INPUT: Error
  processing JSON`). The mutation tasks do this automatically; only set
  `normalize_html_entities: false` to reproduce the failure.
- **DO NOT** keep the version-level `id` on a POST-create payload, and DO NOT
  drop it on a PATCH-replace. Create omits it; replace keeps it (the tasks
  handle this — `import_expression_set` strips it on create).
- **DO NOT** drop `contextDefinitions[].id` on a POST-create — context-node
  parameter data types fail to resolve without it (`Specify a valid data type
  for the … variable`).
- **DO NOT** change `resourceInitializationType` on an existing ES — it is
  **immutable once set**. Set it correctly at POST-create time (`Default` is
  common).
- **DO NOT** mutate a shipped/production Expression Set to experiment — test
  Connect CRUD against a disposable clone, except for an intentional, approved
  change.
- **DO NOT** treat a `removeSteps` (or any PATCH) that reactivates as proof it
  is correct — engine validation is **structural, not functional**. Removing a
  producer element can leave its consumers/filters orphaned and **silently
  misbehave** with no error. See `authoring-and-overlays.md` → *Removing steps*.
- **DO NOT** ship an `addSteps` overlay without accounting for **all three**
  dependency scopes (see `authoring-and-overlays.md`). The
  validator warns on an undeclared **custom** (`__c`/`__r`) reference — declare
  it rather than suppressing the signal. Don't put `__std`/standard fields in
  `externalDependencies`; they aren't custom.
- **DO NOT** append a step to an existing version via a Tooling `Metadata`
  PATCH — it returns `FIELD_INTEGRITY_EXCEPTION`. Use create-with-content or a
  Metadata API deploy.

## Entry Conditions

| Situation | Use |
|---|---|
| Export, create, replace, overlay, or delete an Expression Set at runtime | This skill → [script routing](#script-routing) / Connect API tasks |
| Inspect / trace / diff a live procedure without mutating it | The read-only toolkit CLIs → [script routing](#script-routing) |
| Author/modify a procedure in git (source-controlled) | `metadata-vs-connect.md` → Metadata API authoring |
| The Connect mutation lifecycle, verb-specific field rules, GET gotchas | `metadata-vs-connect.md` |
| Capture a known-good element from one org and add it to another | `authoring-and-overlays.md` |
| Classify a step's dependency scopes; remove a step safely | `authoring-and-overlays.md` |
| Where ES CRUD fits in the **pricing** setup order (recipes, plans, context) | `.cursor/skills/pricing-wiring/SKILL.md` |
| Object/ID model, full schema enums, **every error + resolution**, verification checklist | Detail file: `docs/references/expression-set-connect-api-reference.md` |
| An opaque Connect failure (a code/message you don't recognize) | Reference doc → **Known errors & conditions** section |
| Writing the Python task class itself | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |

## <a name="quick-start"></a>Quick Start

Export → trace → slice a validated overlay → apply to a **disposable clone** —
using the standalone toolkit (`--target-org` is the *SF CLI* alias, never the CCI
alias):

```bash
ORG=rlm-base__beta

# 1. What's in the org, grouped by Revenue Cloud type.
python scripts/expression_sets/list_expression_sets.py --target-org $ORG

# 2. Export a procedure (import-ready: stripped + HTML-unescaped).
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --for-import --out /tmp/pp.json

# 3. Trace a variable: who produces it, who consumes it (safe-removal view).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

# 4. Slice a step into a validated overlay (three scopes pre-classified).
python scripts/expression_sets/export_expression_set_overlay.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --step "Apply Discount" \
    --out /tmp/apply_discount.overlay.json

# 5. Preview applying it to a clone (no --confirm = no write), then apply.
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json --confirm
```

## <a name="script-routing"></a>Task + script routing

Two independent surfaces cover Expression Set CRUD — the **CCI tasks** (build
work) and the standalone **`scripts/expression_sets/` toolkit** (inspection +
one-off lifecycle, `sf`-CLI transport, no access token). They share no code; the
toolkit mirrors the tasks' live-verified rules. Full toolkit detail:
`scripts/expression_sets/README.md`.

| I need to… | Use |
|---|---|
| List every ES in an org by type / active version | `python scripts/expression_sets/list_expression_sets.py --target-org <sf_alias>` (read-only) |
| Pretty-print one procedure's steps in execution order | `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>` (read-only) |
| Export a definition to JSON (snapshot, or `--for-import`) | `python scripts/expression_sets/export_expression_set.py --target-org <sf_alias> --developer-name <name> --out <path>` (read-only) |
| **Trace** who produces/consumes a variable; classify a step's dependency scopes; find orphans | `python scripts/expression_sets/trace_expression_set.py --target-org <sf_alias> --developer-name <name> --variable <v> \| --step <s> \| --field <f> \| --orphans` (read-only) |
| Diff a procedure org-vs-org or org-vs-JSON | `python scripts/expression_sets/diff_expression_set.py --target-org <sf_alias> --developer-name <name> --right-org <sf_alias2> \| --right-file <path>` (read-only) |
| Slice step(s) into a validated overlay with scoped deps | `python scripts/expression_sets/export_expression_set_overlay.py --target-org <sf_alias> --developer-name <name> --step <s> --out <path>` (read-only; writes a local file) |
| Create/replace a whole ES from JSON | `import_expression_set` (CCI, build) **or** `python scripts/expression_sets/import_expression_set.py --target-org <sf_alias> --input-file <path>` (preview; `--confirm` to write) |
| Apply a declarative overlay | `apply_expression_set_overlay` (CCI, build) **or** `python scripts/expression_sets/apply_expression_set_overlay.py --target-org <sf_alias> --expression-set <name> --overlay <path>` (preview; `--confirm`) |
| Activate / deactivate a version (+ procedure-plan cascade) | `python scripts/expression_sets/activate_expression_set.py --target-org <sf_alias> --expression-set <name> --activate \| --deactivate` (preview; `--confirm`) |
| Delete a whole ES or one version | `delete_expression_set` (CCI) **or** `python scripts/expression_sets/delete_expression_set.py --target-org <sf_alias> --expression-set <name> [--version <v>] --confirm` (destructive) |
| Pre-flight a JSON file offline (no org) | `python scripts/ai/validate_expression_set.py <path> [--definition\|--overlay]` |

---

## The CCI tasks

`tasks/rlm_expression_set_connect.py` wraps
`/connect/business-rules/expression-set` and handles the activation lifecycle,
HTML-entity normalization, version-id rules, and the procedure-plan cascade.

| Task | Verb | Use |
|---|---|---|
| `export_expression_set` | GET | Export a definition to JSON (`-o expression_set_api_name <DevName> -o output_file <path>`). |
| `import_expression_set` | POST create / PATCH replace | Create a new ES or replace an existing one whole (`-o input_file <path>`). Auto-detects create vs replace from whether the ES already exists. |
| `apply_expression_set_overlay` | declarative PATCH | Add/remove/update/reorder steps & variables without rewriting the whole definition (`-o overlay_file <path>`). |
| `delete_expression_set` | DELETE | Destructive; requires `-o confirm true`. Whole ES, or one version via `-o version_api_name`. |
| `validate_expression_set` | — (org-less) | Pre-flight a JSON file offline: `-o file <path> -o kind definition\|overlay`. CLI form: `python scripts/ai/validate_expression_set.py <file> [--definition\|--overlay]`. |

Common options on the mutation tasks: `dry_run` (log without mutating),
`skip_validation` (bypass the pre-flight — avoid), `normalize_html_entities`
(default true — leave on), `activate_after_import`/`activate_after_apply`,
`cascade_deactivate_procedure_plan`, `max_wait_seconds`/`poll_interval_seconds`.

---

## Mutation lifecycle & authoring paths (summary)

Every Connect mutation runs **deactivate → PATCH/POST → reactivate** in a guarded
`finally` (an enabled version can't be modified/deleted), including the
`ProcedurePlanDefinitionVersion` cascade; a failed PATCH is **left deactivated and
raised** (non-atomic). Verb-specific field rules (version `id` omit-on-create /
keep-on-replace, `contextDefinitions[].id`, immutable `resourceInitializationType`,
`usageType`), the GET serializer gotchas (alphabetical top-level order,
per-parent `sequenceNumber`, HTML-escaped string leaves), and the **Metadata API**
source-controlled path (nested graphs, no lifecycle, create-with-content) all live
in **`metadata-vs-connect.md`** — read it before any Connect mutation or
source-controlled edit.

## Overlays & dependency capture (summary)

Overlays declare placement by **anchor** (`afterStep`/`beforeStep`), not numeric
sequence; capture them from a live GET (don't hand-author) — the toolkit's
`export_expression_set_overlay.py` slices a step and pre-classifies its dependencies. Every
referenced name is one of **three scopes**: version variable → `addVariables`;
custom (`__c`/`__r`) → `externalDependencies` (the overlay can't create it);
standard context → nothing. Top-level and child steps are sliced differently
(placement vs `parentStep` + `sequenceNumber`). And **validation is structural,
not functional** — a `removeSteps` that reactivates can still leave a consumer
orphaned and silently misbehave. The full slicing table, the three-scope
classifier, the `externalDependencies` block shape, and safe-removal guidance
live in **`authoring-and-overlays.md`**.

---

## Examples

Shipped overlays in `datasets/expression_set_overlays/` are generally
applicable examples. Environment-specific examples live under
`docs/references/expression-set-overlay-examples/` so they remain available for
study without looking like safe default overlays. Capture each from a live GET,
HTML-unescape, validate, cross-check, then apply to a **disposable clone** before
any real target.

| Overlay | Shape | Dependency scopes demonstrated |
|---|---|---|
| `map_line_item.json` | flat, single step (`actionType: BreakdownLineMapping`; maps `SalesTransactionItem` → `SalesTransactionItemDetail`, 18 `sectionJsonStringN` field-mappings) | standard context only — no `addVariables`, no `externalDependencies` |
| `discount_distribution.json` | **nested** — 3 `ListGroup` parents (each with an `AdvancedListFilter` + `AssignmentElement` child) feeding a `DiscountDistributionService` element | ships 4 `Constant_DDS_*` constants in `addVariables`; rest standard context (incl. `__std` discount fields) → no `externalDependencies` |
| `docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json` | **Environment-specific reference** — 2 `ListGroup` blocks, incl. a `FormulaBasedPricing` child computing `SalesTransaction_Hospitals__c - ItemStartQuantity` | **all three scopes**: `HospitalPrice` in `addVariables`; the custom field `SalesTransaction_Hospitals__c` (mapped into `RLM_SalesTransactionContext`) in `externalDependencies`; `ItemProductCode`/`ItemStartQuantity`/etc. standard context |

The facility-quantity example is intentionally not in
`datasets/expression_set_overlays/`: it depends on an org-specific custom field,
context mapping, and procedure-shape anchor. It also shows that a custom field
can be referenced inside a `Formula` string, not just a `Parameter`, so the
dependency scan must tokenize formula text, which the validator does.

### Map Line Item — special case

Salesforce's **documented** authoring path is the **UI paste** (the
`lds-adapters-industries-rule-builder` BKM `BreakdownLineMapping` blob). The
Connect overlay at `map_line_item.json` is the supported programmatic form and
should place the Map Line Item element right after Pricing Setting. Author the
`sectionJsonStringN` values **unescaped**.
Alternative: author it as an `expressionSetDefinition` `<steps>` block and deploy
via the Metadata API (identical shape).

---

## Validation Checks

Run before any Connect mutation and before a PR that touches overlays, the
tasks, or the validator:

```bash
# Pre-flight a payload offline (definition or overlay)
cci task run validate_expression_set -o file <path> -o kind overlay
python scripts/ai/validate_expression_set.py <path> --overlay   # CLI form

# Validator/schema unit tests (self-contained check() runner, no pytest)
python tests/test_expression_set_schema.py        # expect: all pass

# Token for manual API checks
yes | sf org auth show-access-token --target-org <sf_alias>
```

Checklist:

- [ ] Payload HTML-unescaped (or `normalize_html_entities` left on).
- [ ] Validator reports 0 errors; resolve or consciously accept warnings.
- [ ] Overlay `addSteps` account for all three dependency scopes; custom
      (`__c`/`__r`) refs declared in `externalDependencies`.
- [ ] Top-level vs child steps sliced correctly (placement vs `parentStep` +
      `sequenceNumber`).
- [ ] POST omits version `id` and keeps `contextDefinitions[].id`; PATCH keeps
      version `id`.
- [ ] `resourceInitializationType` matches the stored value (or set correctly at
      create).
- [ ] Applied + verified on a **disposable clone** before any real target; for a
      removal, verified functionally (test run), not just "it reactivated."
- [ ] After `cumulusci.yml` task/option edits:
      `python scripts/ai/generate_cci_reference.py` and commit the regenerated
      reference.

---

## Related References

- **Sub-files (progressive disclosure):** `authoring-and-overlays.md` (overlays,
  three-scope dependency capture, safe step removal) and `metadata-vs-connect.md`
  (authoring paths, mutation lifecycle, verb-specific field rules, GET gotchas,
  Metadata API authoring).
- **Standalone toolkit (inspect / trace / diff / export + guarded mutators, no
  access token):** `scripts/expression_sets/README.md`.
- **Exhaustive detail (object/ID model, OAS schema enums, every error +
  resolution, Metadata authoring, verification checklist):**
  `docs/references/expression-set-connect-api-reference.md`
- **Pricing layering model (recipes, recipe-table mappings, procedure plans,
  context definitions) — where ES CRUD fits in pricing setup:**
  `.cursor/skills/pricing-wiring/SKILL.md`
- **Connect CRUD tasks:** `tasks/rlm_expression_set_connect.py`; pre-flight
  validator `tasks/expression_set_schema.py`; tests
  `tests/test_expression_set_schema.py`.
- **External doc link index:**
  `docs/salesforce/262/dev-guide/expression-set-business-apis-links.md`.
- **Writing the Python task class:**
  `.cursor/skills/cci-orchestration/custom-task-authoring.md`.
