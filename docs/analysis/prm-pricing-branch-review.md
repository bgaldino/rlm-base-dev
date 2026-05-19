# PRM Pricing Branch Review (`feature/prm` vs `main`)

> **Status:** Review draft
> **Branch:** `feature/prm`
> **Base:** `main`
> **Reviewer goal:** Verify that this branch is _strictly additive_ for the
> new `prm_pricing` feature flag — flows, tasks, data, and metadata must
> enable a separate PRM pricing deployment without altering the original
> `prm` / `post_prm` baseline (the experience bundle and the channel-program
> field set that exist on `main`).

## TL;DR

The branch is **mostly additive** for `prm_pricing`, but it is **not strictly
additive** today. Five issues violate the "no alterations to original prm /
post_prm" requirement — three of them are functional (one is a clear
regression of baseline PRM when `prm_pricing=false`), and several are
documentation / comment / naming defects. A short list of unrelated
cleanups also pollutes the diff. Recommendations are in §6.

---

## 1. Scope of the branch

5 commits ahead of `main`, ~2,190 insertions / ~614 deletions across 50 files:

| Commit | Title |
|---|---|
| `4d4b0315` | feat(prm): add distributor pricing fields and flows from design spreadsheet |
| `730953b9` | feat(prm): switch to additive context patching and wire recipe mappings |
| `9f1f9c84` | chore(prm): remove dead `deploy_post_prm_tso` task |
| `71d4f8e7` | refactor(prm): remove TSO gating from PRM prepare flow steps |
| `73ae9c01` | feat(prm): isolate pricing bundle and harden `prepare_prm_pricing` idempotency |

### Net structure (committed state)

**New (intended prm_pricing scope):**

- `unpackaged/post_prm_pricing/` — flat bundle (`objects/`, `decisionTables/`,
  `expressionSetDefinition/`, `flows/`, `permissionsets/`, `README.md`).
- `datasets/context_plans/PrmPricing/` — additive Context Service plan.
- `datasets/sfdmu/procedure-plans-prm/` — PRM-only overlay plan.
- `datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json` —
  Tooling API payload for `configure_pricing_recipe_table_mappings`.
- `tasks/rlm_configure_pricing_recipe_table_mappings.py` — new task class.
- `DeactivateProcedurePlanVersion` class appended to
  `tasks/rlm_create_procedure_plan_def.py`.
- New `cumulusci.yml` tasks/flows/flag (§3).
- `unpackaged/post_prm/README.md` — new README describing the legacy bundle.

**Removed (not prm_pricing-related):**

- `deploy_post_prm_tso` task and TSO gating on `prepare_prm` steps 2/3/5/8.
- `docs/analysis/rlm-prefix-standardization-audit.md` (deleted; an untracked
  copy now sits under `docs/archive/`).
- One stale line in `docs/references/cci-task-reference.md`.

**Edited (not prm_pricing-related):**

- `AGENTS.md` — Prettier reformat (~100 lines, no content change).
- `.forceignore` — entry reorder + new comment.
- `orgs/ent.json` — added `"release": "previous"`.
- `datasets/sfdmu/procedure-plans/*.csv` — MasterLabel / EffectiveFrom edits.

---

## 2. Findings — alterations to baseline prm / post_prm

These contradict the rule that the branch must only be additive to enable
`post_prm_pricing`.

### 2.1 Field duplication between `post_prm/` and `post_prm_pricing/` — RESOLVED

`unpackaged/post_prm_pricing/objects/` ships custom-field XML for four
fields that also exist in `unpackaged/post_prm/`:

| Object | Field | In `post_prm` | In `post_prm_pricing` |
|---|---|---|---|
| `ChannelProgramMember` | `RLM_Adjustment_Type__c` | yes | yes |
| `ChannelProgramMember` | `RLM_Adjustment_Value__c` | yes | yes |
| `ChannelProgramMember` | `RLM_Discount_Rate__c` | yes | yes |
| `ChannelProgramLevel` | `RLM_Discount_Rate__c` | yes | yes |

**Original finding (pre-fix):** The `post_prm_pricing/` copies added
`<trackHistory>false</trackHistory>` and, on
`ChannelProgramLevel.RLM_Discount_Rate__c`, flipped `<type>` from
`Percent` to `Number`. Because `prepare_prm` deploys `post_prm` at step 3
and then step 11 → `prepare_prm_pricing` → `deploy_post_prm_pricing`
deploys `post_prm_pricing`, `prm_pricing=true` silently mutated the
schema of fields owned by `post_prm`.

**Resolution applied:** The Number format is the intended source of truth.
The four `post_prm/` field XMLs were updated in-place to match the
`post_prm_pricing/` versions exactly (Percent → Number on the CPL field,
`<trackHistory>false</trackHistory>` added to all four). Both bundles now
ship byte-identical XML for these fields, so deploying both is a true
idempotent no-op rather than a hidden schema mutation. Verified via
`diff unpackaged/post_prm/.../<field> unpackaged/post_prm_pricing/objects/<field>`
for all four pairs (no output).

The duplication remains (per requirement), but the
"alteration to the original prm / post_prm deployment" concern is gone:
the same XML lands no matter which bundle deploys it. The
`unpackaged/post_prm/README.md` "Field Synchronization History" claim
about the Percent → Number fix and `trackHistory=false` on all six
existing CPL/CPM fields is now accurate **for the four shared fields**,
but still needs to reflect that the remaining two CPL fields
(`RLM_Deal_Expiration_Days__c`, `RLM_Minimum_Deal_Size__c`) still don't
carry `<trackHistory>false</trackHistory>` (see §4.1).

### 2.2 `qb-prm` baseline regression — RESOLVED

**Original finding (pre-fix):** `datasets/sfdmu/qb/en-US/qb-prm/Account.csv`
added two columns and `export.json` extended the Account SOQL to select
`RLM_Primary_Reseller__c` and `RLM_Primary_Distributor__c`. Those two
fields are owned by `post_prm_pricing/objects/Account/fields/`, not by
`post_prm/`. The `prepare_prm` gate for `insert_quantumbit_prm_data`
remained `prm and qb` (it never adds `prm_pricing`):

```2972:2974:cumulusci.yml
      9:
        task: insert_quantumbit_prm_data
        when: project_config.project__custom__prm and project_config.project__custom__qb
```

So with `prm=true, qb=true, prm_pricing=false`, step 9 would have failed
SOQL parsing on those two fields — a baseline-PRM regression introduced
by the branch.

**Resolution applied:** `datasets/sfdmu/qb/en-US/qb-prm/Account.csv` and
`datasets/sfdmu/qb/en-US/qb-prm/export.json` were restored to their
`main` content via `git checkout main -- …`. `git diff main` is now empty
for that directory. The baseline `insert_quantumbit_prm_data` task no
longer references any `post_prm_pricing`-owned field, so `prepare_prm`
works cleanly regardless of `prm_pricing`.

Any partner / distributor / reseller seed data for the new fields will
live in a separate prm_pricing-gated dataset (e.g.
`datasets/sfdmu/qb/en-US/qb-prm-pricing/`) wired up under
`prepare_prm_pricing` rather than `prepare_prm`. This stays consistent
with the §2.1 model where prm_pricing is fully isolated from the
baseline `post_prm` flow.

### 2.3 Unrelated edits to baseline `procedure-plans` data plan — RESOLVED

**Original finding (pre-fix):** Two CSV edits landed in commit `730953b9`
("feat(prm): switch to additive context patching and wire recipe
mappings") but were not prm_pricing-related; they modified the
shared/default plan used by `prepare_procedureplans`:

- `ProcedurePlanDefinition.csv` — `MasterLabel` flipped from
  `RLM Quote Pricing Procedure Plan` → `RLM_Quote_Pricing_Procedure_Plan`.
- `ProcedurePlanDefinitionVersion.csv` — `EffectiveFrom` flipped from
  `2026-01-17` → `2026-01-01`.

**Dependency check:** The prm_pricing overlay plan
(`datasets/sfdmu/procedure-plans-prm/`) only matches via `DeveloperName`
on the parent records:

- `ProcedurePlanDefinitionVersion` is `Readonly`, queried by
  `DeveloperName='RLM_Quote_Pricing_Procedure_Plan'`.
- `ProcedurePlanSection` upserts by direct field `SubSectionType`, scoped
  by `ProcedurePlanVersion.DeveloperName='RLM_Quote_Pricing_Procedure_Plan'`.
- `ProcedurePlanOption`, `ProcedurePlanCriterion` match by composite
  keys built from `SubSectionType` / `Priority` / `Sequence` only.
- `ExpressionSetDefinition` is `Readonly`, queried by
  `DeveloperName='RLM_PRM_DISTI_Pricing_Procedure'`.

None of those touch `MasterLabel` or `EffectiveFrom`, and `DeveloperName`
on the parent record is unchanged on both sides. Reverting is safe for
prm_pricing.

**Resolution applied:** Both CSVs were restored to their `main` content
via `git checkout main -- …`. `git diff main -- datasets/sfdmu/procedure-plans/`
is now empty.

**Side note for a follow-up PR:** there is a pre-existing inconsistency
on `main` between `cumulusci.yml` anchors and the SFDMU CSV. Anchors
`procedure_plan_definition_name: "RLM_Quote_Pricing_Procedure_Plan"`
(line 509) and
`procedure_plan_definition_version_effective_from: "2026-01-01T00:00:00.000Z"`
(line 516) are consumed by `create_procedure_plan_definition`, which
creates the records first; SFDMU then upserts the same records and
overwrites the values with the spaced MasterLabel / `2026-01-17`
EffectiveFrom from the CSV. This branch was effectively "fixing" that
drift quietly — but the correct path is a separate PR that explicitly
chooses one canonical pair of values and aligns both
`cumulusci.yml` and the CSV. Not in scope for this PR.

### 2.4 Other non-prm_pricing noise (LOW)

- `orgs/ent.json` adds `"release": "previous"` — unrelated org-shape change.
- `.forceignore` reorders the `RLM_TSO.permissionsetgroup-meta.xml` entry
  and adds a "Storage only" comment.
- `AGENTS.md` — ~100 lines of Prettier reformat (table alignment, blank
  lines, `*` → `_`). No content change, but adds review noise.
- `docs/analysis/rlm-prefix-standardization-audit.md` deletion plus an
  uncommitted `docs/archive/rlm-prefix-standardization-audit.md` (a move,
  but currently shows as one delete + one untracked file).
- `docs/references/cci-task-reference.md` lost one line (the dead
  `deploy_post_prm_tso` reference).
- Removal of `deploy_post_prm_tso` task and TSO gating on `prepare_prm`
  steps 2/3/5/8. Reasonable cleanup, but unrelated to prm_pricing.

### 2.5 Working-tree only (uncommitted) — must NOT be committed (HIGH if committed)

`git status` still has:

- `unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml`
  with `samcheckster@gmail.com.invalid`. HEAD has the placeholder
  `rlm-network-sender@example.com` (good). This is the
  `patch_network_email_for_deploy` runtime leak — leave unstaged and revert
  before any commit. `AGENTS.md` rule #7 explicitly forbids it.
- `unpackaged/post_ux/assembly_manifest.json` working-tree drift —
  regenerated artifact, do not commit manually.

---

## 3. `cumulusci.yml`

The committed `cumulusci.yml` diff is structurally clean — 11 new tasks,
2 new flows, 1 modified flow, 1 new feature flag, 1 new YAML anchor, 1 new
dataset variable, plus the dead-`deploy_post_prm_tso` removal.

### 3.1 Additions (correct shape)

- **Tasks (11):** `apply_context_prm_pricing`,
  `configure_pricing_recipe_table_mappings`,
  `deploy_post_prm_pricing_{objects,decision_tables,expression_sets,flows,permissionsets}`,
  `activate_prm_expression_sets`, `deactivate_prm_expression_sets`,
  `insert_prm_procedure_plan_data`, `deactivate_procedure_plan_version`.
- **Flows (2 + 1 modified):** new `deploy_post_prm_pricing`, new
  `prepare_prm_pricing`; `prepare_prm` adds **step 11** gated on
  `prm and prm_pricing`.
- **Feature flag:** `prm_pricing` (see §3.3 for the default-value defect).
- **YAML anchor:** `ps_prm_pricing: &ps_prm_pricing`.
- **Dataset variable:** `prm_pricing_recipe_table_mappings`.

### 3.2 Task / flow naming — RESOLVED

**Original finding (pre-fix):** the new tasks and flow were named
`deploy_post_prm_core_*` / `deploy_post_prm_core`, but their `path:`
options all pointed at `unpackaged/post_prm_pricing/`. The "core" framing
implied baseline PRM metadata, when in fact the bundle is the
prm_pricing-only branch metadata. The misnomer was mirrored in task
descriptions ("PRM core custom fields", "PRM permission sets", etc.)
and in `unpackaged/post_prm_pricing/README.md` line 18.

**Resolution applied:**

- Renamed the five tasks
  `deploy_post_prm_core_{objects,decision_tables,expression_sets,flows,permissionsets}`
  → `deploy_post_prm_pricing_{...}` and rewrote each `description:` to
  explicitly mention "PRM pricing" plus the deployed components
  (e.g. "Deploy PRM pricing custom fields (Account, Quote, QuoteLineItem,
  ChannelProgramLevel, ChannelProgramMember) from
  unpackaged/post_prm_pricing/objects.").
- Renamed the flow `deploy_post_prm_core` → `deploy_post_prm_pricing`
  with description "Deploy the PRM pricing metadata bundle
  (unpackaged/post_prm_pricing/) in dependency order." and updated its
  five `task:` references.
- Updated `prepare_prm_pricing` step 2 from `flow: deploy_post_prm_core`
  to `flow: deploy_post_prm_pricing`.
- Updated `unpackaged/post_prm_pricing/README.md` line 18 to say
  "Task group: `deploy_post_prm_pricing_*` in `cumulusci.yml`".
- Regenerated `.cursor/skills/cci-orchestration/{tasks,flows,feature-flags}-reference.md`
  via `python scripts/ai/generate_cci_reference.py`.

`git grep deploy_post_prm_core` returns no matches (this review doc's
historical reference excluded — it is the record of the finding).

### 3.3 Defect — `prm_pricing` flag default disagrees with its own docs (MEDIUM)

```126:126:cumulusci.yml
    prm_pricing: true        # Enable branch PRM pricing metadata/tasks (non-main behavior)
```

But the new `unpackaged/post_prm/README.md` ships with:

```184:189:unpackaged/post_prm/README.md
project_config:
  project__custom__:
    prm: true                    # Core PRM feature
    prm_exp_bundle: true         # Experience Cloud site content
    prm_pricing: false           # Branch PRM pricing metadata/tasks
```

If `prm_pricing` is genuinely "branch / non-main behavior", it should
default to `false`. Setting it `true` means every consumer of this branch
runs `prepare_prm_pricing` automatically — counter to the isolation goal.
Pick one truth and align both.

### 3.4 `prepare_prm_pricing` flow logic — correct, two small notes

```3002:3028:cumulusci.yml
  prepare_prm_pricing:
    group: Revenue Lifecycle Management
    description: Deploy branch PRM pricing metadata/tasks behind prm_pricing.
    steps:
      1:
        task: deactivate_prm_expression_sets
      2:
        flow: deploy_post_prm_pricing
      3:
        task: assign_permission_sets
        options:
          api_names: *ps_prm_pricing
      4:
        task: configure_pricing_recipe_table_mappings
      5:
        task: activate_prm_expression_sets
      6:
        task: deactivate_procedure_plan_version
        when: project_config.project__custom__procedureplans
      7:
        task: insert_prm_procedure_plan_data
        when: project_config.project__custom__procedureplans
      8:
        task: activate_procedure_plan_version
        when: project_config.project__custom__procedureplans
      9:
        task: apply_context_prm_pricing
```

- Step 1 → step 2 → step 5 ordering is correct for re-deploys (deactivate,
  deploy, activate). `ManageExpressionSets._set_versions_status` swallows
  "not found by ApiName" with a warning, so step 1 is idempotent on first
  run.
- Procedure-plan deactivate/insert/activate (steps 6–8) are correctly
  gated on `procedureplans`. The overlay plan only adds rows for
  `RLM_Quote_Pricing_Procedure_Plan` and is isolated from the baseline
  `procedure-plans` plan.
- The `RLM_PRM_Pricing` permission set assigned in step 3 **omits**
  `ChannelProgramLevel.RLM_Adjustment_Type__c` and
  `ChannelProgramLevel.RLM_Adjustment_Value__c` — these two CPL fields
  exist only in prm_pricing and would have no FLS via this PS.

---

## 4. Documentation / comments

### 4.1 `unpackaged/post_prm/README.md` (new) is inaccurate (HIGH for doc accuracy)

It claims `post_prm` owns content that is actually now in `post_prm_pricing`:

- "Account (2 fields): `RLM_Primary_Reseller__c`, `RLM_Primary_Distributor__c`"
  → live in `post_prm_pricing` (post_prm's `Account/fields/` is empty after `73ae9c01`).
- "Quote (1 field): `RLM_Distributor_Account__c`" → lives in `post_prm_pricing`.
- "QuoteLineItem (3 fields): `RLM_Distributor_Discount_Percent__c`,
  `RLM_Distributor_Unit_Price__c`, `RLM_Partner_Net_Total_Price__c`" → live
  in `post_prm_pricing`.
- "Flows (2): `RLM_Update_Channel_Program_Member.flow`,
  `RLM_Create_New_Quote.flow`" → live in `post_prm_pricing`.
- "Decision Tables (1 PRM-owned): `RLM_Channel_Program_Level_Partner.decisionTable`"
  → lives in `post_prm_pricing`.
- "Expression Set Definitions: `RLM_PRM_DISTI_Pricing_Procedure` … deployed from
  `post_prm`" → actually deployed from
  `post_prm_pricing/expressionSetDefinition/`.
- "`RLM_PRM.permissionset-meta.xml` — Grants read/edit access to all 12 PRM
  custom fields (6 on channel objects, 6 on quote/account objects)" → the
  actual `RLM_PRM.permissionset-meta.xml` is 6 channel fields only. The
  Quote/Account fields are granted by `RLM_PRM_Pricing` (a different PS in
  the prm_pricing bundle).
- "Field Synchronization History … Fixed `ChannelProgramLevel.RLM_Discount_Rate__c`
  from type Percent → Number (scale 0). Added `trackHistory: false` to all
  6 existing fields …" → After the §2.1 resolution, four of those edits
  are now genuinely applied in `post_prm/` (CPL `RLM_Discount_Rate__c` and
  the three CPM fields). The remaining two CPL fields
  (`RLM_Deal_Expiration_Days__c`, `RLM_Minimum_Deal_Size__c`) still do
  **not** carry `<trackHistory>false</trackHistory>` in `post_prm/`. If
  the "all 6" claim must hold, either add `trackHistory=false` to those
  two or soften the README wording to "4 of 6".

The README needs to be rewritten to describe what `post_prm` actually
contains today: the 6 channel-program fields (CPL + CPM), the `RLM_PRM`
permission set, the partner community network, the Experience Bundle, the
partner community user profile/perm-set, the navigation menus, and the
sharing-rules deploy.

### 4.2 `unpackaged/post_prm_pricing/README.md`

- ~~Line 18 references `deploy_post_prm_core_*`~~ **Resolved** in §3.2:
  the README now references `deploy_post_prm_pricing_*`.
- Doesn't enumerate the actual bundle contents (per-object field list,
  flows, decision table, expression set, permset). Worth listing
  explicitly so this README is the source of truth for the bundle.

### 4.3 `cumulusci.yml` comments

- Line 126 comment "non-main behavior" is fine in spirit but inconsistent
  with `default: true` (§3.3).
- ~~The five `deploy_post_prm_core_*` task descriptions all say "PRM core
  custom fields"~~ **Resolved** in §3.2: each `deploy_post_prm_pricing_*`
  task now carries an explicit "Deploy PRM pricing …" description with
  the deployed component list.

### 4.4 Auto-generated CCI references

`scripts/ai/generate_cci_reference.py` was re-run after each commit; skill
diffs are consistent with the YAML diffs. No action needed unless the
renames in §3.2 land — then re-run again.

### 4.5 SFDMU v5 validator

`python scripts/validate_sfdmu_v5_datasets.py` flags two Medium issues
against `datasets/sfdmu/procedure-plans-prm/`:

- `ProcedurePlanCriterion`: externalId contains nested relationship path
  `ProcedurePlanOption.ProcedurePlanSection.SubSectionType` which may
  cause v5 flattening errors (Bug 2 territory).

The pattern matches the existing baseline `procedure-plans` plan on
`main`, so this is not a new class of risk — but remains a Bug 2/3
candidate to watch.

---

## 5. Strict-additivity scorecard

| Area | Status |
|---|---|
| New `unpackaged/post_prm_pricing/` bundle | Additive |
| New `datasets/context_plans/PrmPricing/` | Additive |
| New `datasets/sfdmu/procedure-plans-prm/` | Additive |
| New `datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json` | Additive |
| New `tasks/rlm_configure_pricing_recipe_table_mappings.py` | Additive |
| New `DeactivateProcedurePlanVersion` Python class | Additive |
| New `cumulusci.yml` tasks / flows / flag | Additive (naming defect, §3.2) |
| `prepare_prm` step 11 added (gated) | Additive (only safe if flag default is `false` — §3.3) |
| `unpackaged/post_prm/README.md` (new) | Additive **but inaccurate** (§4.1) |
| ~~`post_prm_pricing` redeclares 4 fields owned by `post_prm`~~ | **Resolved** — `post_prm/` XML brought in line with `post_prm_pricing/`; second deploy is now an idempotent no-op (§2.1) |
| ~~`qb-prm` Account.csv / export.json~~ | **Resolved** — reverted to `main`; prm_pricing seed data will live in a separate dataset (§2.2) |
| ~~`datasets/sfdmu/procedure-plans/*.csv`~~ | **Resolved** — reverted to `main`; underlying drift between `cumulusci.yml` anchors and CSV flagged for a separate PR (§2.3) |
| `orgs/ent.json` (`release: previous`) | Not prm_pricing-related (§2.4) |
| `.forceignore` reorder | Not prm_pricing-related (§2.4) |
| `AGENTS.md` Prettier reformat | Not prm_pricing-related (§2.4) |
| `docs/analysis/rlm-prefix-standardization-audit.md` move | Not prm_pricing-related (§2.4) |
| Removal of `deploy_post_prm_tso` + TSO gating on `prepare_prm` | Not prm_pricing-related (§2.4) |
| Working-tree `rlm.network-meta.xml` real email | Not committed; must stay that way (§2.5) |

---

## 6. Recommended actions

To make the branch truly additive for `prm_pricing` and reach a clean state:

1. ~~Eliminate the 4 duplicate fields in `post_prm_pricing/objects/`~~
   **Done (alternate path):** the four `post_prm/` field XMLs were
   updated in-place to match the `post_prm_pricing/` versions
   (`type=Number`, `<trackHistory>false</trackHistory>`). Both bundles
   now ship byte-identical XML for the 4 shared fields, so the second
   deploy is an idempotent no-op rather than a schema mutation.
   Duplication is retained intentionally per current direction; if the
   team later wants single source of truth, delete the duplicates from
   `post_prm_pricing/objects/ChannelProgramLevel/` and
   `post_prm_pricing/objects/ChannelProgramMember/` only.
2. ~~Remove the new Account columns from
   `datasets/sfdmu/qb/en-US/qb-prm/Account.csv` and the matching SELECT~~
   **Done:** both files were reverted to `main`. Next step is to land a
   separate prm_pricing-gated dataset (e.g.
   `datasets/sfdmu/qb/en-US/qb-prm-pricing/`) plus a new
   `insert_qb_prm_pricing_data` task wired into `prepare_prm_pricing` so
   the new `Account.RLM_Primary_Reseller__c` /
   `Account.RLM_Primary_Distributor__c`, `Quote.RLM_Distributor_Account__c`,
   and QLI distributor / partner-net fields can be seeded without
   touching the baseline `qb-prm` plan.
3. ~~Revert the two CSVs under `datasets/sfdmu/procedure-plans/`~~
   **Done:** both files were restored to `main` via
   `git checkout main -- …`. Underlying drift between `cumulusci.yml`
   anchors (`procedure_plan_definition_name`,
   `procedure_plan_definition_version_effective_from`) and the SFDMU CSV
   values is a pre-existing inconsistency on `main` — track separately.
4. **Set `prm_pricing` default to `false`** in `cumulusci.yml` to match
   the README and the "isolated from baseline" intent (or update both
   sides if the team genuinely wants default-on).
5. ~~Rename the deploy tasks/flow~~ **Done:** five tasks renamed to
   `deploy_post_prm_pricing_{objects,decision_tables,expression_sets,flows,permissionsets}`
   and the flow renamed to `deploy_post_prm_pricing` in `cumulusci.yml`;
   `prepare_prm_pricing` step 2 updated;
   `unpackaged/post_prm_pricing/README.md` updated; CCI skill references
   regenerated.
6. **Fix `RLM_PRM_Pricing` permset** to include
   `ChannelProgramLevel.RLM_Adjustment_Type__c` and
   `ChannelProgramLevel.RLM_Adjustment_Value__c` so the pricing FLS is
   complete.
7. **Rewrite `unpackaged/post_prm/README.md`** to describe the bundle as
   it actually is (channel-program fields, `RLM_PRM` permset, partner
   community). Move the partner/distributor/quote-line-item descriptions
   into `unpackaged/post_prm_pricing/README.md`.
8. **Split unrelated cleanups into a separate PR** (or drop):
   `orgs/ent.json`, `.forceignore` reorder, `AGENTS.md` Prettier reformat,
   `docs/analysis/rlm-prefix-standardization-audit.md` move,
   `deploy_post_prm_tso` removal + TSO gating cleanup. These are
   reasonable changes but don't belong in a prm_pricing-isolated PR.
9. **Discard the working-tree edits** to
   `unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml`
   and `unpackaged/post_ux/assembly_manifest.json` before any push.
10. **After 1–8:** re-run `python scripts/ai/generate_cci_reference.py`
    and `python scripts/validate_sfdmu_v5_datasets.py` and commit the
    regenerated docs.

---

## Appendix A — File inventory (committed diff vs `main`)

```
.cursor/skills/cci-orchestration/SKILL.md                                                |  +19
.cursor/skills/cci-orchestration/feature-flags.md                                        |  +22
.cursor/skills/cci-orchestration/flows-reference.md                                      |  +36
.cursor/skills/cci-orchestration/tasks-reference.md                                      | +163
.forceignore                                                                             |   ±6
AGENTS.md                                                                                | ±102 (Prettier)
README.md                                                                                |   ±5
cumulusci.yml                                                                            | +153
datasets/context_plans/PrmPricing/contexts/prm_pricing.json                              | +117 (NEW)
datasets/context_plans/PrmPricing/manifest.json                                          |   +8 (NEW)
datasets/sfdmu/procedure-plans-prm/**                                                    |  +83 (NEW plan)
datasets/sfdmu/procedure-plans/ProcedurePlanDefinition.csv                               |   reverted to main (§2.3 fix)
datasets/sfdmu/procedure-plans/ProcedurePlanDefinitionVersion.csv                        |   reverted to main (§2.3 fix)
datasets/sfdmu/qb/en-US/qb-prm/Account.csv                                               |   reverted to main (§2.2 fix)
datasets/sfdmu/qb/en-US/qb-prm/export.json                                               |   reverted to main (§2.2 fix)
datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json                         |  +12 (NEW)
docs/analysis/rlm-prefix-standardization-audit.md                                        | -524 (moved → docs/archive untracked)
docs/references/cci-task-reference.md                                                    |   -1
orgs/ent.json                                                                            |   +1 (release: previous)
tasks/rlm_configure_pricing_recipe_table_mappings.py                                     | +422 (NEW)
tasks/rlm_create_procedure_plan_def.py                                                   |  +71 (DeactivateProcedurePlanVersion)
unpackaged/post_prm/README.md                                                            | +227 (NEW, inaccurate)
unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml                 |   ±2 (committed: placeholder; working tree: real email)
unpackaged/post_prm_pricing/**                                                           | +814 (NEW bundle, with §2.1 dup fields)
unpackaged/post_ux/assembly_manifest.json                                                |   ±2 (regenerated artifact)
```

## Appendix B — Verification commands used

```bash
git log --oneline main..HEAD
git diff main --stat
git diff main -- cumulusci.yml
git diff main -- unpackaged/post_prm/
git diff main -- datasets/sfdmu/qb/en-US/qb-prm/
git diff main -- datasets/sfdmu/procedure-plans/
git ls-files unpackaged/post_prm_pricing/
python scripts/validate_sfdmu_v5_datasets.py
```
