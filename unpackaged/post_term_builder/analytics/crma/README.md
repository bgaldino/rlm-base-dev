# Delta Term Builder — CRM Analytics dashboards (backup)

Backup copies of the two CRM Analytics (CRMA / Tableau CRM) dashboards built
for the **Delta Term Builder** demo, plus the datasets they read from.

> **These are REST API exports, not deployable source metadata.** They are
> kept here as a copy/backup of live org assets. Do **not** expect
> `cci`/`sf` metadata deploys to pick them up — the `.json` files sit in a
> non-metadata-type folder (`analytics/`) so source deploys ignore them.
> Restore is manual, via the Wave REST API (see **Restore** below).

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

## Restore

The Wave REST API has no single "import dashboard" call; recreate in order —
dataset first (a dashboard's steps reference it by Id), then the dashboard.

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
