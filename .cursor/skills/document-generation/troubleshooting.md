# Troubleshooting Document Generation

Read when output is blank, wrong, or generation errors. Run the Before generation checks in SKILL.md first. Parent: [document-generation](SKILL.md).

### Common Extract Architecture Pitfalls

| Pitfall | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Cartesian product | N×M rows instead of N+M | Two multi-record sequences at the same nesting level | Nest child under parent via hierarchical OutputFieldName |
| FilterGroup cartesian | Records × groups explosion | Multiple FilterGroups on a nested child sequence | Use separate independent hierarchy instead of OR filters |
| Missing children | Only top-level records' children appear | Parent sequence has restrictive filter (e.g., ParentId = null) | Create separate root query without the restriction |
| Singleton instead of array | One object instead of array | Root-level OutputFieldName or all records collapse to same context | Nest under a parent (e.g., `Quote:MyArray` not just `MyArray`) |
| Null field values | Field silently blank | Relationship traversal without explicit join sequence | Use direct field or add join sequence for intermediate object |
| Output path confusion | Data in wrong JSON location | Using internal hierarchy paths for output field mappings | Use separate top-level output path (e.g., `Line:*` not `Quote:QuoteLineItem:*`) |
| Mixed-depth leakage | Parent + child count entries (e.g., 7+5=10 instead of 5) | Field mappings for same output array read from different hierarchy depths | All mappings must read from same depth — use redundant join for parent fields |
| Grantless parents in array | Empty rows for records without children | No subquery filtering; parent-level mapping includes all parents | Use child-first hierarchy with redundant parent join at child level |

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| All tokens blank | Extract failing (duplicates, NPE) | Check for duplicate object queries, null OutputObjectName |
| `getOutputObjectName() is null` | Item missing OutputObjectName | Set `OutputObjectName: "json"` on all items |
| "mandatory details missing" in UI | Same as above, or missing InputFieldName on object queries | Add required fields |
| `[object Object]` for images | Org below Release 256 (DocGen 1.0) `[inferred: threshold not in the 264 snapshot]` | Upgrade org; or use RTB_ with HTML `<img>` as fallback |
| IMG_ token consumed, no image | Missing `width`/`height`, or Integration User can't access file | Add both dimensions + add Integration User to Content Library |
| Engine crash: `Cannot read properties of undefined (reading '0')` | `src` has ContentVersion ID (`068`) or file Title | Use ContentDocument ID (`069`) only |
| HYP_ shows red "URL is invalid" error | Wrong field name (`src` instead of `url`) or token formatted as Word hyperlink | Use `"url"` field (not `"src"`); ensure token is plain text in template |
| Template locked for edits | Active status | Deactivate (`IsActive: false, Status: Draft`) first |
| Specific token blank | Field not in Extract or Transform | Trace: is field queried? Is it mapped through both ODTs? |
| Repeating section empty | Formula item missing or wrong ResultPath | Check formula at `OutputCreationSequence: 0` |
| Formula produces no output | Unsupported function (FormulaConverted is null) | Check `FormulaConverted` field — if null, the function isn't supported. See "Formula Function Catalog" in `extract-engine-reference.md` |
| ODT Name rejected on create | Contains underscores or spaces | Use camelCase only — alphanumeric, no special chars |
| More array entries than expected | Field mappings at mixed hierarchy depths | Run `docgen_odt_inspect_hierarchy.py` — all mappings for same output array must be at uniform depth |
| Array is singleton (object, not list) | OutputFieldName at root level | Nest under parent: use `Root:ArrayName` not just `ArrayName` |
| Missing child records in output | Parent sequence has restrictive filter | Child sequences inherit parent scope — create independent hierarchy with broader filter |
| N×M×G explosion in child results | Multiple FilterGroups on nested sequence | Each parent × each FilterGroup evaluated independently — use single FilterGroup or separate hierarchy |
