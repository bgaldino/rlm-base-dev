# qb-product-images Data Plan

SFDMU data plan for QuantumBit (QB) product image URLs. Updates the `DisplayUrl` field on existing Product2 records created by qb-pcm, pointing them to static resource image paths for the product catalog UI.

## CCI Integration

### Flow: `prepare_product_data`

This plan is executed as **step 3** of the `prepare_product_data` flow (when `qb=true`), after qb-pcm.

| Step | Task                                | Description                                |
|------|-------------------------------------|--------------------------------------------|
| 1    | `insert_quantumbit_pcm_data`        | Runs qb-pcm plan (creates products)       |
| 3    | `insert_quantumbit_product_image_data` | Runs this SFDMU plan (updates DisplayUrl)|

### Task Definition

```yaml
insert_quantumbit_product_image_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-product-images"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with one Update-only object. No records are created — only existing Product2 records are matched by `StockKeepingUnit` and updated with their `DisplayUrl`.

```
Single Pass (SFDMU)
─────────────────────────────────
Update Product2.DisplayUrl
(match by StockKeepingUnit)
```

### Objects

| # | Object   | Operation | External ID        | Records |
|---|----------|-----------|--------------------|---------|
| 1 | Product2 | Update    | `StockKeepingUnit` | 165     |

**Note:** This is an Update-only operation — it will not create products. Products must already exist from the qb-pcm plan. The `Name` field is included in the SOQL for reference but is not modified.

## Product Image Mapping

The 165 products are mapped to static resource image paths (e.g., `/resource/RLM_quantumBit_logo_sq`, `/resource/database`, `/resource/powerswerve`). Some products have no `DisplayUrl` set (empty value in CSV), meaning they rely on a default or have no image.

Image categories include:
- Generic QB branding (`/resource/RLM_quantumBit_logo_sq`) — most common
- Hardware-specific images (`/resource/powerswerve`, `/resource/hd_8tb_72k`, `/resource/intel_e52609`, etc.)
- Software/service images (`/resource/database`, `/resource/collab_suite`, `/resource/genAI`, etc.)
- Professional services (`/resource/ps_proj_mgr`, `/resource/ps_sol_arch`, etc.)

## Portability

- **External ID**: `StockKeepingUnit` — fully portable across orgs
- **No auto-numbered fields**
- **No composite keys or `$$` columns**
- `excludeIdsFromCSVFiles: "true"` — no Salesforce IDs in CSV

The `DisplayUrl` values reference static resources that must be deployed to the org. If the static resources are not present, the images will not render but the data load will still succeed.

## Dependencies

**Upstream:**
- **qb-pcm** — Product2 records must exist (matched by `StockKeepingUnit`)

**Downstream:**
- None — this is a cosmetic/UI-only update

## File Structure

```
qb-product-images/
├── export.json                          # SFDMU data plan (single pass, 1 object)
├── README.md                            # This file
├── Product2.csv                         # 165 records (Update DisplayUrl)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Idempotency

This plan is inherently idempotent — the Update operation sets `DisplayUrl` to the same value on each run. Re-runs will match existing products by `StockKeepingUnit` and apply the same `DisplayUrl` values, resulting in no effective changes.

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None applicable.** This plan only touches `Product2.DisplayUrl`.

### Self-Referencing Fields

**None applicable.**

### Field Coverage

This plan uses only 3 Product2 fields: `StockKeepingUnit` (externalId), `Name` (reference), and `DisplayUrl` (update target). All are confirmed present in the 260 schema. `DisplayUrl` is a standard updateable URL field on Product2.

**No missing fields, no schema changes, no risks.**

### Cross-Object Dependencies

| Lookup Target | Source  | Status     |
|---------------|---------|------------|
| Product2      | qb-pcm  | Update only|

## Optimization Opportunities

1. **Extraction available**: Use `extract_qb_product_images_data` (Data Management - Extract). Run all extracts: `cci flow run run_qb_extracts --org <org>`. Idempotency: `test_qb_product_images_idempotency` / `cci flow run run_qb_idempotency_tests --org <org>`.
2. **Static resource dependency**: Consider documenting which static resources must be deployed for images to render
3. **Consistency**: Consider switching from `objectSets` to flat `objects` array for consistency with qb-pcm
