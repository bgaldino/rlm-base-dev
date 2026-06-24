# In-App Learning Framework — Maintain the `inapp` Integration

Use this skill when working on the **In-App Learning** navigation framework — the
data-driven "Learning Home" layered onto a Foundations build (a **temporary**
integration of the Industries In-App Framework, pending a from-scratch redesign).
It covers the SFDMU data plan, the one-shot converter, per-release content updates,
the `RLM_Learning_*` naming convention, and deploy/reload/verify. Readable by any agent.

Feature surface: `inapp` flag (default **false**) → `prepare_inapp` flow (`prepare_rlm_org`
step 30) → `deploy_post_inapp` (metadata `unpackaged/post_inapp`) + `load_inapp_dataset`
(data `datasets/sfdmu/inapp`). Access via the `RLM_Learning` permission set.

## Quick Rules

1. **The converter is the source of truth for the data.** Edit
   `datasets/sfdmu/inapp/convert_from_legacy.py`, then **re-run it** to regenerate the
   CSVs — never hand-edit `RLM_Learning_*.csv`. It reads the legacy SQL dump and emits
   SFDMU v5 CSVs. Re-running is idempotent.
2. **Converter SOURCE side stays legacy-named; OUTPUT side is `RLM_Learning_*`.**
   `parse_table(sql, "Block__c")` and the `*-NN` row-id constants read the original dump;
   only `write_csv` object names, column headers, and `__r` traversals carry the prefix.
3. **Everything the integration adds to rlm-base is `RLM_Learning_*`** (objects, fields,
   tabs, flexipages, app, permset, Apex) or **`rlmLearning*`** (LWC — camelCase can't take
   the underscore prefix). The CCI token stays `inapp` (`post_<feature>` convention — a
   different axis from the metadata API prefix). Static images: `<block-name-slug>.png`.
4. **Per-release content updates go through the converter's remap dicts** (see
   [§ Per-release content](#per-release-content-update)) and must be **grounded** against
   `docs/salesforce/{release}/feature-index.md` + the Help snapshot.
5. **Validate before every commit:** `python scripts/validate_sfdmu_v5_datasets.py
   --dataset datasets/sfdmu/inapp` and `python scripts/ai/check_plan_readme_consistency.py
   datasets/sfdmu/inapp` — both must pass.
6. **Verify behavioral changes on a live scratch org** (CLAUDE.md DO NOT #9): deploy +
   `load_inapp_dataset`, confirm `RLM_Learning_SectionBlockController.getSectionsWithBlocksByType`
   returns resolved data, and render-check the Learning Home in a browser.
7. **Read the data-plan README** (`datasets/sfdmu/inapp/README.md`) for the externalId
   scheme, the 4 live-load fixes, and image re-host details — it is the committed companion
   to this skill. The maintainer report at `.agents/artifacts/in-app-framework-262-integration-report.md`
   (gitignored) holds the full redesign POV.

## DO NOT

- **DO NOT** hand-edit the generated `datasets/sfdmu/inapp/RLM_Learning_*.csv` — change the
  converter and regenerate.
- **DO NOT** prefix the converter's source-reading calls (`parse_table`, `DEAD_BLOCK_IDS`,
  `*_rt_mapping`) — they must match the original legacy table/row-id names.
- **DO NOT** change the junction (`RLM_Learning_SectionBlock__c`) from `Insert` +
  `deleteOldData: true` back to Upsert — its composite-traversal externalId never matches on
  re-Upsert (SFDMU Bug 5), so Upsert silently doubles the junction.
- **DO NOT** judge an LWC "unused" from flexipage→template/import reachability alone —
  **quickActions reference LWCs** via `<lightningWebComponent>` (this removed `reorderableList`
  by mistake). Grep quickActions before deleting any LWC.
- **DO NOT** trust `curl` HTTP status to validate `help.salesforce.com` /
  `developer.salesforce.com` / Trailhead / YouTube links — they are SPAs that return 200 for
  dead pages. Cross-check `ind.*` IDs against the local snapshot, render the page and read its
  title, or use YouTube oembed (see § Per-release content).
- **DO NOT** keep the demo-account ref generic — the framework hardcodes the demo Account
  (`Infinitech`) in a DynamicLink `Where_Condition__c`; preserve the `Mahesh→Infinitech` remap.

## Entry Conditions

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Update the learning content for a new release | Yes | Converter remap dicts + feature-index grounding; regenerate + reload. |
| Add/replace a learning image | Yes | Drop into the static resource; `rewrite_block_images` handles src + alt. |
| Rename framework metadata / extend the convention | Yes | `RLM_Learning_*` / `rlmLearning*`; watch keyed-Name renames + orphan cleanup. |
| Deploy/verify the framework on a scratch org | Yes | `prepare_inapp` or deploy+`load_inapp_dataset`; verify the controller + render. |
| General SFDMU v5 plan authoring | Use `sfdmu-data-plans/SKILL.md` | This skill is the inapp-specific overlay. |
| Place inapp code/metadata correctly | Also see `repo-integration/SKILL.md` | `templates/` vs `unpackaged/post_ux` rules etc. |
| Harden the inapp Apex | Also see `apex-security-hardening/SKILL.md` | The 4 classes are USER_MODE-hardened. |

## Data model & SFDMU scheme

Pages → Sections → Blocks build the home + per-capability detail pages; `RLM_Learning_DynamicLink__c`
resolves in-app popups, detail links, and external resources; `RLM_Learning_Icon__c` supplies icons;
`RLM_Learning_SectionBlock__c` is the Section↔Block junction. **Composite natural keys, not synthetic
`External_Id__c`:** 5 objects key on `Name` (Upsert, idempotent); the junction uses
`operation: Insert` + `deleteOldData: true` with externalId
`RLM_Learning_Section__r.Name;RLM_Learning_Block__r.Name;RLM_Learning_Order_Sequence__c`.

**The 4 live-load fixes** (all surfaced only on a real load — see README for detail):
1. Lookup queries need **both** the `__c` field **and** the `__r.Name` traversal, or the FK lands null.
2. RecordType matched via a `Readonly` RecordType object + `RecordType.csv` + a **2-part**
   `DeveloperName;SobjectType` externalId (3-part fails on null NamespacePrefix).
3. The permset needs `recordTypeVisibilities` or insert fails "Record Type ID isn't valid for the user."
4. Required fields excluded from FLS, and Section layouts' `<platformActionList>` stripped.

## Per-release content update

All content transforms live in `convert_from_legacy.py`'s `scrub_text()` + remap dicts. **Ground every
target** against `docs/salesforce/{release}/feature-index.md` and the Help snapshot
(`docs/salesforce/{release}/help/articles/`) — and verify links with a **reliable** signal:

| Concern | Mechanism | Verify by |
|---|---|---|
| Renamed Help articles | `HELP_ID_REMAP` (`ind.*` → 262 ID) | file exists in `docs/salesforce/262/help/articles/<id>.md` |
| Dead release-notes pages | `RN_ID_REMAP` (`rn_*`) | render page, read `<title>` (not "couldn't find that page") |
| Renamed dev-guide pages | `DEVGUIDE_ID_REMAP` | file exists in `docs/salesforce/262/dev-guide/articles/` |
| Release label bump | `VERSION_TEXT_REMAPS` + `release=258→262` | — |
| Product rebrand | `_ARM_RE` (guarded "Revenue Cloud"→"Agentforce Revenue Management") | keeps editions/cert/Trailhead titles via lookahead guards |
| Rebranded Trailhead titles | `TRAILHEAD_RELABEL` (exact live title) | fetch the trail/module og:title live |
| Stale `DynamicLink` Names | `DL_NAME_REMAP` | keyed-Name rename → clean orphans on re-loaded orgs |
| Image `<img>` (src + alt) | `rewrite_block_images` + `_img_alt` | `/resource/InAppLearningImages/<slug>.png`, alt = topic |

SPAs (Help, dev-guide, Trailhead, YouTube) return HTTP 200 for dead pages — **snapshot cross-check or
rendered-title is authoritative**, `curl` status is not. YouTube: `/oembed?url=…` 404 = dead. Trailhead
DOES return a real 404 (curl OK there only).

## Naming convention

| Surface | Convention | Example |
|---|---|---|
| CCI flag / task / flow / bundle dir | `inapp` (`post_<feature>`) | `prepare_inapp`, `post_inapp` |
| Custom objects + fields (+ `__r`) | `RLM_Learning_*` | `RLM_Learning_Block__c.RLM_Learning_Header__c` |
| App / flexipages / tabs / permset / Apex | `RLM_Learning_*` | app `RLM_Learning_Home`, `RLM_Learning_SectionBlockController` |
| LWC components | `rlmLearning*` (camelCase) | `rlmLearningAppContainer` |
| Static-resource images | `<block-name-slug>.png` | `revenue-cloud-fundamentals.png` |

**Keyed-rename caveat:** Block/Section/Page/DynamicLink **Names are the SFDMU composite keys**.
Renaming a Name → Upsert inserts a new record and orphans the old one on a re-loaded org; a fresh
build is clean, but ent-r1-style orgs need the old records deleted. App `MasterLabel` ≤ **40 chars**.

## Deploy, reload, verify

```bash
# Fresh build (assigns RLM_Learning, deploys, loads): flip the flag, then
cci flow run prepare_inapp --org <alias>
# Iterative on an existing org:
sf project deploy start --source-dir unpackaged/post_inapp --target-org <user> --ignore-conflicts
cci task run load_inapp_dataset --org <alias>          # Insert+deleteOldData junction = idempotent
```
Then verify (CLAUDE.md DO NOT #9 — no dryrun-only claims): the controller returns resolved data, and
the Learning Home renders in a browser. The `RLM_Learning` permset grants the objects/fields/classes/
tabs/recordtypes **and** the `RLM_Learning_Home` app (`applicationVisibilities`); after assigning it,
Lightning caches tab/app visibility per session — a hard refresh (or Chrome restart) clears it.

## Examples

**Bump content to release N:** add the renamed Help/dev-guide/`rn_*` IDs to `HELP_ID_REMAP` /
`DEVGUIDE_ID_REMAP` / `RN_ID_REMAP` (each verified present in `docs/salesforce/N/`), refresh the area
"what's new" bullets from `feature-index.md`, then regenerate + validate + reload + render-check.

**Swap a learning image:** replace `unpackaged/post_inapp/staticresources/InAppLearningImages/<slug>.png`,
re-run the converter (it re-points `src` + sets `alt` from the block topic), redeploy the static
resource, reload, confirm it serves 200 with matching content-type.

**Delete an LWC:** first `grep -rl '<lightningWebComponent>' unpackaged/post_inapp/quickActions` and the
flexipage/template/import graph — only remove if nothing references it (the quickAction lesson).

## Validation Checks

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/inapp   # PASS
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/inapp        # 0 errors
python datasets/sfdmu/inapp/convert_from_legacy.py                             # regenerate after edits
```
Also: `git diff --stat` for unintended churn; confirm `datasets/sfdmu/inapp/README.md` reflects any
object/count change; deploy 0-failure + controller-returns-data on a live org before PR.
