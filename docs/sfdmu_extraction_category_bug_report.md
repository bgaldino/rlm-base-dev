# SFDMU Bug Report: Custom Relationship Field Returns #N/A During Extraction

**Repository:** https://github.com/forcedotcom/SFDX-Data-Move-Utility  
**Submit at:** https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/new

---

## Title

[BUG] Extraction returns #N/A for custom relationship traversal fields (e.g. `Category__r.Code`) even when org has data

---

## Description

### Summary

During **extraction** (org → CSV), SFDMU v5 returns `#N/A` for custom relationship traversal fields like `Category__r.Code` in the exported CSV, even when the source org records have the lookup populated and the related object's field contains valid data.

Direct SOQL against the org returns the correct values; SFDMU extraction does not.

### Environment

- **SFDMU version:** v5.x (tested with 5.0.0+)
- **Salesforce API:** v66.0
- **Object:** `AdvAccountForecastFact` (custom object)
- **Field:** `Category__c` (lookup to ProductCategory)
- **Relationship traversal:** `Category__r.Code` (ProductCategory.Code)

### Steps to Reproduce

1. Create an org with:
   - `ProductCategory` records (with `Code` populated, e.g. "Base Chemicals", "Industrial Solvents")
   - `AdvAccountForecastFact` records with `Category__c` populated (pointing to ProductCategory)

2. Configure export.json with a query that includes the relationship field:
   ```json
   {
     "query": "SELECT Id, Name, Category__r.Code, ... FROM AdvAccountForecastFact ...",
     "operation": "Insert"
   }
   ```

3. Run SFDMU extraction: `sf sfdmu run --sourceusername <org> --targetusername CSVFILE -p <plan_dir>`

4. Inspect the extracted `AdvAccountForecastFact.csv`

### Expected Behavior

The `Category__r.Code` column should contain the ProductCategory Code values (e.g. "Base Chemicals", "Industrial Solvents") for each row, matching what a direct SOQL query returns.

### Actual Behavior

The `Category__r.Code` column contains `#N/A` for all rows in the extracted CSV.

### Verification

Direct SOQL against the same org returns correct data:

```bash
sf data query -q "SELECT Id, Name, Category__c, Category__r.Code FROM AdvAccountForecastFact LIMIT 5" -o <org>
```

Example result:
```json
{
  "Name": "Sulfuric Acid (H2SO4) - 200L Drum FQ1 FY 2025",
  "Category__c": "0ZGWs000000qc6DOAQ",
  "Category__r": { "Code": "Base Chemicals" }
}
```

The Salesforce API returns the correct `Category__r.Code` value. SFDMU extraction does not propagate it to the CSV.

### Workaround

Query the org separately for the affected records and merge the relationship field values into the extracted CSV post-extraction. We implemented this as a post-processing task that:
1. Queries `SELECT Name, Category__r.Code FROM AdvAccountForecastFact WHERE Category__c != null`
2. Matches by `Name` and replaces `#N/A` in the extracted CSV with the org values

### Related

- Similar to the documented 2-hop traversal bug (returns #N/A) — this affects **1-hop** custom relationship fields (`CustomLookup__r.Field`)
- Standard relationship fields (e.g. `Account.Name`) may work; the bug appears specific to **custom** relationship traversals (`__r`)

### Additional Context

- `ProductCategory` is a Readonly object in the plan; ProductCategory extraction works correctly (Code column populated)
- The bug occurs during extraction only; load/insert with the same relationship field works when Ids are pre-injected
