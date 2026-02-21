# Resolving ProcedurePlanOption → ProcedurePlanSection Missing Parent Lookup

SFDMU reports **2 missing parent lookup records** for `ProcedurePlanSectionId` on ProcedurePlanOption. Option rows reference sections by `ProcedurePlanSection.SubSectionType` and `ProcedurePlanSection.Sequence` (e.g. `DefaultPricing;1`, `HeaderDistribution;2`). The target org has 2 Section records with those values, but SFDMU does not resolve the lookup when Section is Readonly in the same object set as Option (Section source is merged to 4 rows and the composite externalId map does not match).

## Options to resolve (without editing source CSVs)

### 1. **Report to SFDMU**
- Open an issue: Readonly parent with composite externalId (`SubSectionType;Sequence`) is not resolving for child Option records when parent Section has 4 source rows (2 real + 2 stubs).
- Run with `--diagnostic --anonymise` and attach the generated log.
- Link to this repo’s `export.json` and `MissingParentRecordsReport.csv` if useful.

### 2. **Use a different tool or script for Option**
- Run SFDMU for Section only (Set 1), then use another method (e.g. `sf data import`, or a small script using Bulk API / REST) to insert ProcedurePlanOption rows with `ProcedurePlanSectionId` set from the target Section Ids (e.g. from `source/ProcedurePlanSection_source.csv` after the run).

---

## Option that requires editing the Option CSV (one-time)

### 3. **Populate ProcedurePlanSectionId in ProcedurePlanOption.csv**
If you allow a one-time CSV change:

1. Run the migration once (Set 1 and Set 2). Set 1 may insert or skip Section; Set 2 will write `source/ProcedurePlanSection_source.csv` with target Section data.
2. Open `source/ProcedurePlanSection_source.csv` and note the two Section **Id**s and their `SubSectionType` and `Sequence` (e.g. `DefaultPricing`/`1` → Id1, `HeaderDistribution`/`2` → Id2).
3. Add a column **ProcedurePlanSectionId** to `ProcedurePlanOption.csv` and set:
   - Row for DefaultPricing / Sequence 1 → first Section Id  
   - Row for HeaderDistribution / Sequence 2 → second Section Id  
4. In `export.json` set `"excludeIdsFromCSVFiles": "false"` so SFDMU uses the Id column (or leave true and confirm whether SFDMU still uses explicit lookup Id when present).
5. Re-run the migration. Option inserts should use the provided Section Ids and succeed.

This replaces reliance on the broken composite lookup with explicit Ids from the target org.
