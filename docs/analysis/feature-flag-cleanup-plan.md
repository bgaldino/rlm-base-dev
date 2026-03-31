# Cleanup Plan: Dead Code and Orphaned Files

This plan documents dead code and orphaned files identified during the feature flag audit (March 2026). Items are grouped by risk level and priority.

---

## Phase 1: Safe Removals (no runtime impact)

These items are never referenced in any flow or task. Removing them has zero impact on `prepare_rlm_org` or any other flow.

### 1.1 Dead Tasks in `cumulusci.yml`

| Task | Why it's dead | Action |
|------|---------------|--------|
| `insert_clm_data_prod` | Duplicate of `insert_clm_data` — both point to `*quantumbit_clm_dataset`. Never referenced in any flow. | Remove task definition |
| `restore_rc_tso` | Defined but never called in any flow (including `prepare_tso`). Also remove from README task table. | Remove task definition + README reference |
| `deploy_rc_tso` | Defined but never called in any flow. | Remove task definition + README reference |

#### Verification before removal

```bash
# Confirm no flow references exist (should return only the task definition lines)
grep -n 'insert_clm_data_prod\|restore_rc_tso\|deploy_rc_tso' cumulusci.yml
```

#### Post-removal check

```bash
# Confirm restore_rc_tso Python module is also unused
grep -rn 'rlm_restore_rc_tso' cumulusci.yml tasks/
# If only the import in cumulusci.yml was removed, consider deleting tasks/rlm_restore_rc_tso.py
```

---

### 1.2 Orphaned Dataset Directories

These directories exist on disk but are not referenced by any task, flow, or anchor in `cumulusci.yml`.

| Directory | Contents | Why it's orphaned | Action |
|-----------|----------|-------------------|--------|
| `datasets/sfdmu/qb/en-US/qb-accounting/` | 6 files (CSVs + export.json) | No task or anchor references it. Only appears in `.cursor/` plans. | Delete directory |
| `datasets/sfdmu/qb/ja/` | qb-pcm, qb-pricing subdirs | Japanese locale datasets — never wired up. No task references. | Delete directory |
| `datasets/sfdmu/mfg/en-US/` | mfg-configflow, mfg-constraints-p, mfg-constraints-prc, mfg-multicurrency | Manufacturing datasets — no task references. Only in `.cursor/` plans. | Delete directory |
| `datasets/sfdmu/_archived/` | 4 archived constraint subdirs | Explicitly archived. Not referenced anywhere. | Delete directory |
| `datasets/context_plans/archive/` | Legacy context plans | Documented as unused in `docs/context_service_utility.md`. | Delete directory |
| `datasets/context_plans/ProductDiscoverySalesTransactionType/` | Context plan files | Not referenced anywhere in the codebase. | Delete directory |

#### Verification before removal

```bash
# Confirm no references exist (exclude node_modules, .cursor, .claude)
grep -rn 'qb-accounting\|qb/ja\|mfg-configflow\|mfg-constraints\|mfg-multicurrency' \
  --include='*.yml' --include='*.py' --include='*.sh' --include='*.json' \
  --exclude-dir=node_modules --exclude-dir=.cursor --exclude-dir=.claude .

grep -rn 'ProductDiscoverySalesTransactionType\|context_plans/archive' \
  --include='*.yml' --include='*.py' --include='*.md' \
  --exclude-dir=node_modules .
```

---

## Phase 1b: Unused Feature Flags

These flags are defined in `project.custom` (lines 84-117) but never referenced in any `when:` condition. They are marked `[unused]` in their comments.

| Flag | Default | Notes |
|------|---------|-------|
| `qbrix` | `false` | "Use xDO base" — never gated any task or flow. Remove unless xDO integration is planned. |
| `ramps` | `true` | "Insert and configure ramps" — no ramp tasks exist. Remove; re-add if ramp support is built. |
| `product_dataset` | `qb` | String flag, not boolean. Intended to select dataset family (qb, q3, mfg) but never wired into `when:` conditions or Python code. Flows use `qb`/`q3` boolean flags instead. Remove or wire up. |
| `locale` | `en_US` | String flag. Intended for locale selection but never consumed. Japanese datasets (`qb/ja/`) exist but aren't connected. Remove or wire up. |

### Decision criteria

- If any planned feature depends on these flags, keep them and add a `# TODO: wire up in <feature>` comment.
- Otherwise, remove to reduce confusion. They can always be re-added when needed.

---

## Phase 2: Low-Risk Removals (manual-only tasks with overlapping alternatives)

These tasks are never used in flows but could theoretically be run manually. They overlap with tasks that flows actually use. Confirm with the team before removing.

| Task | What it does | Why it's likely dead | Overlaps with |
|------|-------------|---------------------|---------------|
| `deploy_context_definitions` | Deploys entire context defs directory | Flows use individual `extend_context_*` tasks | `extend_context_billing`, `extend_context_cart`, etc. |
| `deploy_decision_tables` | Deploys entire DT directory | Flows use `refresh_dt_*` tasks | `refresh_dt_asset`, `refresh_dt_rating`, etc. |
| `deploy_org_settings` | Deploys org settings directory | Never referenced anywhere | Org settings deployed via `unpackaged/pre` |
| `deploy_permissions` | Deploys PSG directory | Flows use `assign_permission_set_groups` | `assign_permission_set_groups` |
| `deploy_post_commerce` | Deploys commerce metadata | No group assigned. `commerce` flag uses other tasks. | `extend_context_cart`, `refresh_dt_commerce` |
| `deploy_post_payments` | Deploys payments metadata | No group assigned. Flows use `deploy_post_payments_site` + `deploy_post_payments_settings`. | `deploy_post_payments_site`, `deploy_post_payments_settings` |

### Decision criteria

- If any team member uses these via `cci task run <name>` directly, keep them.
- If nobody recognizes them, remove and note in the PR description.

---

## Phase 2b: Rename `qb` and `quantumbit` Flags for Clarity

Both flags exist and are actively used, but their names don't convey what they actually control:

| Current name | Default | What it actually gates |
|-------------|---------|----------------------|
| `qb` | `true` | **Data loading** — which SFDMU data plans to insert (PCM, pricing, billing, tax, rating, rates, DRO, constraints, PRM, guided selling) |
| `quantumbit` | `true` | **Metadata deployment** — deploy_post_utils, deploy_post_billing, deploy_post_approvals, deploy_quantumbit, assign QB/CALM permission sets |

### Proposed rename

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `qb` | `qb_data` | Clearly indicates this flag gates data plan loading |
| `quantumbit` | `qb_metadata` | Clearly indicates this flag gates metadata deployment and permission sets |

### Changes required

1. **Flag definitions** (lines 86, 106): rename the keys
2. **All `when:` references to `project__custom__qb`** (~16 occurrences): replace with `project__custom__qb_data`
3. **All `when:` references to `project__custom__quantumbit`** (~6 occurrences): replace with `project__custom__qb_metadata`
4. **YAML anchors** using `quantumbit_*` prefix: keep as-is (internal, not user-facing)
5. **README and docs**: update flag tables and any prose references

### Risk

- Any org-level `cumulusci.yml` overrides (e.g. in `~/.cumulusci/`) that set `qb: false` or `quantumbit: false` will silently stop working after the rename. Announce in release notes.
- Search for `project__custom__qb[^_]` (note: must exclude `qb_` prefixed flags like `qb_data` itself) to find all references.

---

## Phase 3: Granular Deploy Sub-Tasks (keep or consolidate)

These are granular alternatives to composite deploy tasks. They deploy individual subdirectories rather than the whole `unpackaged/post_*` tree. They're useful for debugging partial deploys.

| Group | Composite task (used in flows) | Granular sub-tasks (unreferenced) |
|-------|-------------------------------|----------------------------------|
| Agents | `deploy_agents` | `deploy_agents_bots`, `deploy_agents_flows`, `deploy_agents_genAiFunctions`, `deploy_agents_genAiPlanners`, `deploy_agents_genAiPlugins`, `deploy_agents_permissionsets` |
| Procedure Plans | `deploy_post_procedureplans` | `deploy_post_procedureplans_classes`, `deploy_post_procedureplans_objects`, `deploy_post_procedureplans_permissionsets` |

### Recommendation

**Keep these.** They serve as documented entry points for deploying specific agent/procedure plan components during development and debugging. They have clear naming and group membership. If the team wants to reduce clutter, they can be moved to a separate `debug_tasks.yml` or similar.

---

## Phase 3b: Document Org Definitions

The project defines 15 scratch org configurations (lines 12-63) with no documentation on what each one is for or when to use it. Add a comment block or README section explaining each org.

| Org alias | Config file | Purpose (needs documentation) |
|-----------|-------------|-------------------------------|
| `beta` | `orgs/beta.json` | ? |
| `dev` | `orgs/dev.json` | ? |
| `dev-sb0` | `orgs/dev-sb0.json` | ? (SB0 = Sandbox Edition?) |
| `dev_datacloud` | `orgs/dev_datacloud.json` | ? (Data Cloud features?) |
| `dev_enhanced` | `orgs/dev-enhanced.json` | ? |
| `dev_preview` | `orgs/dev_preview.json` | ? (pre-release API version?) |
| `dev_previous` | `orgs/dev_previous.json` | ? (previous API version?) |
| `test-sb0` | `orgs/test-sb0.json` | ? |
| `tfid` | `orgs/tfid.json` | ? (Trialforce ID base?) |
| `tfid-cdo` | `orgs/tfid-cdo.json` | ? (CDO = Customer Data Object?) |
| `tfid-cdo-rlm` | `orgs/tfid-cdo-rlm.json` | ? (CDO + RLM?) |
| `tfid-dev` | `orgs/tfid-dev.json` | ? |
| `tfid-enable` | `orgs/tfid-enable.json` | ? |
| `tfid-ido-tech` | `orgs/tfid-ido-tech-SB0.json` | ? (IDO = Industries Demo Org?) |
| `tfid-ido-tech-R2` | `orgs/tfid-ido-tech-R2.json` | ? (IDO R2 revision?) |
| `tfid-qb-tso` | `orgs/tfid-qb-tso.json` | ? (QuantumBit Trialforce Source Org?) |
| `tfid-sdo` | `orgs/tfid-sdo.json` | ? (SDO = Sales Demo Org?) |

### Hardcoded instance targets

Some org configs pin to a specific Salesforce instance (e.g. `"instance": "USA794"` in `dev-sb0.json`). These orgs **require a DevHub that has been specifically enabled to create scratch orgs on that instance**. A standard DevHub will fail with an error when attempting to create them. This makes them unusable for most team members.

Audit all `orgs/*.json` files for `"instance"` keys:

```bash
# Find all orgs with hardcoded instance targets
grep -l '"instance"' orgs/*.json
```

For each instance-pinned org, document:
1. Why it targets that specific instance
2. Which DevHub is required to create it
3. The closest alternative org type that does **not** require instance pinning (e.g., `dev-sb0` → `dev` or `beta`), so team members without the special DevHub can use a comparable config

### Duplicate org configs

Several org configs are identical or near-identical:

**Exact duplicates (byte-for-byte):**

| Group | Files | Recommendation |
|-------|-------|----------------|
| Enhanced + USA794 | `beta.json` = `dev-sb0.json` = `test-sb0.json` | Consolidate to one file. If instance pinning isn't needed, use `dev-enhanced.json` (same config, no instance). |
| Base RLM | `feature.json` = `release.json` | Consolidate. Neither is referenced in `cumulusci.yml` — may be safe to delete. |

**Identical except for instance pin:**

| Files | Difference |
|-------|-----------|
| `beta.json`, `dev-sb0.json`, `test-sb0.json` (instance: USA794) vs `dev-enhanced.json` (no instance) | Only the `"instance": "USA794"` key. All features and settings are identical. |

**Identical except for orgName:**

| Files | Difference |
|-------|-----------|
| `dev.json` ("Agentforce Revenue Management") vs `dev-enhanced.json` ("Agentforce Revenue Management (Enhanced)") | Same features and settings. Only the `orgName` string differs. These are effectively the same org. |

This means `dev`, `dev-enhanced`, `beta`, `dev-sb0`, and `test-sb0` all produce the same org (modulo orgName and instance pin) — 5 configs for 1 shape.

### Org config files not registered in `cumulusci.yml`

These JSON files exist in `orgs/` but have no corresponding scratch org definition:

| File | Notes |
|------|-------|
| `feature.json` | Identical to `release.json`. Not registered. Possibly a CCI convention default? |
| `release.json` | Identical to `feature.json`. Not registered. Possibly a CCI convention default? |
| `tfid-sdo-lite.json` | Template-based (TFID `0TTKX000001ASkL`). Not registered. |

### Filename mismatch bug

`cumulusci.yml` line 56 references `config_file: orgs/dev_datacloud.json` (underscore), but the actual file on disk is `orgs/dev-datacloud.json` (hyphen). Creating a `dev_datacloud` scratch org will fail. Fix by renaming the file or updating the reference.

### Action items

1. Review each `orgs/*.json` config file to understand the feature/edition differences
2. Audit for hardcoded `"instance"` values — document the reason or remove if no longer needed
3. Fix the `dev_datacloud` filename mismatch (line 56 vs actual file)
4. Consolidate duplicate configs — decide which orgs need distinct definitions vs which can share a config file
5. Decide whether `feature.json`, `release.json`, and `tfid-sdo-lite.json` should be registered or deleted
6. Add inline comments in `cumulusci.yml` above each org definition explaining its purpose and when to use it
7. Document in the README which org to use for common workflows (e.g., "for local dev use `dev`, for TSO testing use `tfid-qb-tso`")
8. Identify any orgs that are no longer used and can be removed

---

## Phase 4: Verify After Cleanup

After removing items from Phases 1-2:

```bash
# 1. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('cumulusci.yml'))"

# 2. Verify flow parsing
cci flow info prepare_rlm_org --org dev

# 3. Verify task list is clean
cci task list | grep -i 'clm_data_prod\|restore_rc_tso\|deploy_rc_tso'

# 4. Run SFDMU dataset validation
python scripts/validate_sfdmu_v5_datasets.py
```

---

## Already Completed (this session)

- Removed deprecated anchors `quantumbit_constraints_product_dataset` and `quantumbit_constraints_component_dataset`
- Removed dead tasks `insert_qb_constraints_product_data` and `insert_qb_constraints_component_data`
- Added `psg_debug: false` flag definition (was referenced but never defined)
- Added `constraints` guard to `constraints_data`-only steps
- Updated all flag comments with `[metadata]`/`[data]`/`[both]`/`[unused]`/`[modifier]` categories
- Clarified `qb` vs `quantumbit` comments (data vs metadata)
- Expanded all TSO references to "Trialforce Source Org (TSO)"
