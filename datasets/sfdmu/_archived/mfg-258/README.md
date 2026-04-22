# Manufacturing (MFG) data shape

This directory holds SFDMU data plans for the Manufacturing data shape, following the same patterns as the QuantumBit (QB) shape under `qb/en-US/`.

## Directory structure

Create plan directories under `mfg/en-US/`, for example:

```
mfg/
└── en-US/
    └── mfg-pcm/          # Manufacturing Product Catalog Management (example)
        ├── export.json
        ├── README.md
        ├── Product2.csv
        └── … (one CSV per object in export.json)
```

## Adding a new MFG plan (e.g. mfg-pcm)

1. **Create the plan directory:** `datasets/sfdmu/mfg/en-US/mfg-pcm/` (or your plan name).
2. **Add export.json and CSVs** using the same format as QB plans (see [qb-pcm README](../qb/en-US/qb-pcm/README.md) or [qb-rating README](../qb/en-US/qb-rating/README.md)). Use single-pass (flat `objects`) or multi-pass (`objectSets`) as needed.
3. **Wire in cumulusci.yml:**
   - Under **DATA PLAN NAMES AND PATHS**: add an anchor, e.g.  
     `mfg_pcm_dataset: &mfg_pcm_dataset "datasets/sfdmu/mfg/en-US/mfg-pcm"`
   - Add a load task (e.g. `insert_mfg_pcm_data`) using `LoadSFDMUData` with `pathtoexportjson: *mfg_pcm_dataset`.
   - Add an extract task (e.g. `extract_mfg_pcm_data`) in group **Data Management - Extract** using `ExtractSFDMUData` with the same anchor. Post-process runs by default; output goes to `datasets/sfdmu/extractions/mfg-pcm/<timestamp>/processed/`.
   - Add an idempotency task (e.g. `test_mfg_pcm_idempotency`) in group **Data Management - Idempotency** using `TestSFDMUIdempotency` with the same anchor.
4. **Add a README** in the plan directory documenting objects, external IDs, and load order.

The extract task and post-process script are plan-agnostic: they work for any path under `datasets/sfdmu/` (qb, mfg, or other shapes). See the main [README](../../../README.md) section **Data plan directory structure** and **Adding a new data shape**.
