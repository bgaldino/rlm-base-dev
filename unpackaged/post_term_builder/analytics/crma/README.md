# Delta Term Builder — CRM Analytics dashboards (backup)

Backup copies of the two CRM Analytics (CRMA / Tableau CRM) dashboards built
for the **Delta Term Builder** demo, plus the datasets they read from.

This folder holds the backup in **two formats**:

1. **`deployable-metadata/`** — source-format Wave metadata (`.wdash`,
   `.wapp-meta.xml`, `.wds-meta.xml`) + a `package.xml`. Redeployable in one
   `sf project deploy` command (see **Deploy** below). This is the fastest way
   to restore the apps + dashboards into a target org.
2. **REST JSON exports** at this folder's root and under `datasets/`
   (`*.dashboard.json`, `*.dataset.json`, `*.xmd.json`, `*.rows.json`) — full
   Wave REST GET payloads. Not deployable metadata; these are the authoritative
   record of dashboard `state` and the static dataset **rows** (which the
   Metadata API does not capture), and support the manual REST restore.

> **Nothing here is deployed to fresh orgs by `prepare_rlm_org`.** Both the
> source-format files and the `.json` exports reference hardcoded dataset/app
> IDs from the Delta demo org, so the whole `analytics/` subtree is excluded
> from the term builder deploy via a `.forceignore` rule
> (`unpackaged/post_term_builder/analytics/**`). Restore is a deliberate,
> manual step against the Delta org — never part of an org build.

## Source org

Captured 2026-07-22 from the **Delta** connected org
(`scheck@deltarevcloud.demo`, `trailsignup-c79803691fdea3.my.salesforce.com`).

| Dashboard | Id | App / folder | Dataset |
|-----------|----|--------------|---------|
| Delta UC1 — Contract Term Analysis | `0FKaj000001dWvVGAU` | Delta Contract Building Analytics | `Flown_Fact` (`0Fbaj000002UGqzCAG`) |
| Delta UC2 — Contract Adherence | `0FKaj000001dWyjGAE` | Delta Contract Adherence Analytics | `Contract_Fact` (`0Fbaj000002UGz3CAG`) |

## Contents

```
uc1-contract-term-analysis.dashboard.json   full GET payload (label, folder, state)
uc2-contract-adherence.dashboard.json        full GET payload (label, folder, state)
datasets/
  contract_fact.dataset.json  flown_fact.dataset.json   dataset metadata
  contract_fact.xmd.json       flown_fact.xmd.json        main XMD (dimensions/measures)
  contract_fact.rows.json      flown_fact.rows.json       all rows (static demo data)
```

The `.dashboard.json` `state` object is the authoritative definition: `widgets`,
`steps` (with their `aggregateflex`/SAQL queries), and `gridLayouts` (pages +
placements). Dataset rows are the static demo data — the datasets are not fed by
a live data flow, so these rows fully reproduce what the dashboards render.

## Changes baked into these copies

These backups reflect the demo-hardening edits applied on 2026-07-22:

1. **Fixed** the `Invalid group expression: sort_order` error — removed the
   `sort_order` **measure** from the `group by` of the affected steps (UC1
   `tbl_terms`; UC2 `bar_comm_term`, `bar_act_comm_term`, `bar_progress`). A
   measure can't be a grouping dimension in a compact `aggregateflex` query.
2. **Rebranded** the title tiles to be account-agnostic — stripped the
   `Infinitech — ` prefix (now "Contract Term Analysis", "Contract Commitment",
   "Performance vs Commitment").
3. **Added page navigation** to UC2 — `link` widgets (`nav_to_v2`, `nav_to_v1`)
   in the top-right of each page's title band, navigating between the two pages
   (`destinationType: page`). CRMA pages are authoring tabs only and don't render
   as runtime tabs, so these buttons are how a viewer moves between them.

## Deploy (source-format restore)

`deployable-metadata/` is a normal source-format bundle. To push it to a target
org (the Delta demo org, or a clone) in one command — from the repo root:

```bash
sf project deploy start \
  -x unpackaged/post_term_builder/analytics/crma/deployable-metadata/package.xml \
  --target-org Delta
```

`package.xml` deploys the 2 `WaveApplication`s, 7 `WaveDashboard`s, and 2
`WaveDataset` **definitions**. Notes:

- **Datasets deploy as definitions only — no rows.** The Metadata API never
  carries dataset rows. If the datasets are empty/missing on the target, load
  the static demo rows from `datasets/*.rows.json` (Wave external-data upload
  API) so the dashboards render.
- The `.forceignore` rule keeps these files out of the normal term builder
  deploy, so deploying them is always an explicit, manifest-scoped action like
  the one above — it will not happen during `prepare_rlm_org`.
- If a dashboard's steps point at a dataset Id/version that differs on the
  target org, fix the refs per the **Restore** steps below before/after deploy.

## Restore (manual, via Wave REST)

Use this path when you need the full `state` payload (e.g. to re-point step
dataset refs) rather than a straight metadata redeploy. The Wave REST API has no
single "import dashboard" call; recreate in order — dataset first (a dashboard's
steps reference it by Id), then the dashboard.

1. **Dataset** — if `Contract_Fact` / `Flown_Fact` no longer exist, recreate the
   dataset and load `*.rows.json` (external-data upload API, or rebuild from the
   demo source). Note the new dataset Id + current version Id.
2. **Fix step dataset refs** — in the `.dashboard.json` `state`, every
   `steps[].datasets[]` entry and each step `query.query`'s `load "<id>/<ver>"`
   must point at the restored dataset Id/version.
3. **Create the dashboard**:
   ```bash
   sf api request rest "/services/data/v67.0/wave/dashboards" \
     --method POST \
     --body "$(jq '{label, description, folder, state}' uc2-contract-adherence.dashboard.json)" \
     --target-org <alias>
   ```
   (`folder` must reference an existing Wave app; adjust `folder.id` to the target
   org's app.) To update an existing dashboard in place instead, `PATCH
   /wave/dashboards/<id>` with `{ "state": <state> }`.

### PATCH gotchas (learned the hard way)

- The GET serializer **HTML-escapes** each step's embedded query string
  (`&quot;`). Before writing, `html.unescape()` **every** step query and
  re-serialize as plain JSON — the write API rejects escaped queries.
- GET adds read-only fields to `steps[].datasets[]` (`label`, `url`). Strip them
  before PATCH; keep `id` + `name` (write rejects `Unrecognized field 'label'`).
- `group by` accepts a **dimension** or a date function — never a measure.
