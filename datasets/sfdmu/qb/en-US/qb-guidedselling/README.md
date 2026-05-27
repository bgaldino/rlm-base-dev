# qb-guidedselling Data Plan

SFDMU data plan for QuantumBit guided-selling OmniStudio data (AssessmentQuestions, OmniProcesses, OmniProcessElements).

## Status: Extraction/Preservation Only

**The source of truth for guided selling setup is the metadata in `unpackaged/post_guidedselling/`, not these CSVs.** The `prepare_guidedselling` flow deploys metadata directly and does not consume this SFDMU plan.

These CSVs are retained for extraction roundtrip preservation and historical reference. They should be regenerated from a freshly-built org via:

```bash
cci task run extract_qb_guidedselling_data --org <org>
```

The CSVs in this directory may be stale relative to the current metadata. A future cleanup should either:
- Regenerate them from a canonical org after the metadata deploys cleanly, or
- Remove this plan entirely if extraction preservation is no longer needed.

## Objects

| # | Object | Operation | externalId | Notes |
|---|--------|-----------|------------|-------|
| 1 | AssessmentQuestionConfig | Upsert | `DeveloperName` | |
| 2 | AssessmentQuestionSetConfig | Upsert | `DeveloperName` | |
| 3 | AssessmentQuestion | Upsert | `UniqueIndex` | |
| 4 | AssessmentQuestionSet | Upsert | `UniqueIndex` | |
| 5 | AssessmentQuestionAssignment | **Insert** + deleteOldData | `AssessmentQuestion.UniqueIndex;AssessmentQuestionSet.UniqueIndex` | Traversal composite |
| 6 | AssessmentQuestionVersion | **Insert** + deleteOldData | `Name` | |
| 7 | OmniProcess | Upsert | `UniqueName` | |
| 8 | OmniScriptConfig | Upsert | `DeveloperName` | |
| 9 | OmniProcessElement | **Insert** + deleteOldData | `OmniProcess.UniqueName;Name` | Traversal composite |
| 10 | OmniProcessAsmtQuestionVer | **Insert** + deleteOldData | `AssessmentQuestionVersion.Name;OmniProcessElement.Name` | Traversal composite |

## Dependencies

**Upstream:**
- `qb-pcm` — Products must exist for guided selling product qualification.
- `deploy_post_guidedselling` — OmniScript and AssessmentQuestion metadata must be deployed first.

**Downstream:**
- None for org setup (metadata path handles this).
- Product2 guided-selling field values are loaded by `qb-guidedselling-products` (separate plan).
