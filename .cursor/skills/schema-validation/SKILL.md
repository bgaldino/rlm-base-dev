---
name: schema-validation
description: >-
  Validate, refresh, and certify the Revenue Cloud ERD against live Salesforce orgs
  and the Core UDD source. Use when refreshing erd-data.json after a release,
  certifying a new release upgrade (e.g. 260 → 262), diffing schemas across releases,
  removing orphan/artifact fields, or investigating whether a field is a real RC
  platform field vs a custom or other-cloud field.
---

# Schema Validation & ERD Refresh

End-to-end workflow for keeping `docs/erds/erd-data.json` aligned to canonical Revenue Cloud platform schema. The ERD is the grounding source for every AI agent working in this repo — its quality directly determines AI accuracy.

## Quick Rules

1. **The ERD reflects PLATFORM schema only.** Custom fields (any `__c` suffix, including project `RLM_*__c` and managed-package fields) are excluded by every validator and extraction script. Don't override this.
2. **Always cross-validate against TWO orgs** when classifying orphan fields — a field present in one org but absent in another is likely feature-gated, not removed.
3. **Verify against Core source** before bulk-removing fields. The validators surface candidates; codesearch confirms ground truth.
4. **Use `prepare_rlm_org`-built scratch orgs** for both 260 baseline and 262 target — `ent-r1` (260) and `rlm-base__ent-sb0` (262) are the canonical references.
5. **All schema diff scripts default to skipping custom fields**. Pass `--include-custom` only for project-internal tooling that needs to see deployed `RLM_*__c` fields.

## DO NOT

1. **DO NOT** patch `erd-data.json` from a single org without cross-validating against another release/configuration. You'll baseline feature-gated noise as canonical schema.
2. **DO NOT** use `techido-260` or other ad-hoc orgs for baseline — only fresh `prepare_rlm_org` builds.
3. **DO NOT** assume a field is a PDF artifact just because it's missing from one org. Verify against Core UDD source.
4. **DO NOT** remove orphan fields without producing a backup (`erd-data.json.bak.*`) and a removal report.
5. **DO NOT** run `--patch` followed immediately by `--apply --safe-only` without inspecting candidates — review the orphan-candidates report first.

## Tooling Map

| Script | Purpose | Output |
|---|---|---|
| `scripts/erd/validate_erd_against_org.py` | Diff ERD against a single org (find missing fields/relationships, find orphans) | `docs/erds/validation-report.md` |
| `scripts/erd/schema_diff/extract_schema.py` | Extract full schema from one org as JSON | `scripts/erd/schema_diff/<release>-schema.json` |
| `scripts/erd/schema_diff/diff_schemas.py` | Diff two schema JSONs (260 vs 262) with optional SFDMU plan impact analysis | `scripts/erd/schema_diff/260-vs-262-diff.md` |
| `scripts/erd/cleanup_orphan_erd_fields.py` | Classify orphans (pdf_artifact / documented / documented_rel) and optionally remove | `docs/erds/orphan-candidates*.md` |
| `scripts/erd/cleanup_erd_data.py` | Fix data-quality issues in ERD (typos, wrong types, missing domainShort) | In-place patch |
| `scripts/erd/build_erds.py` | Regenerate interactive HTML from `erd-data.json` | `docs/erds/revenue-cloud-erd.html` |
| `scripts/erd/orphan_batch_helper.py` | Batch workflow helper (prepare/apply/validate cycles) | Multiple |
| `scripts/ai/query_erd.py` | Query ERD content (describe/relationships/domain/path/search) | Stdout |

## Common Workflows

### A. Refresh ERD after a release upgrade

```bash
# 1. Provision fresh scratch orgs from the release/260 (260) and main (262) branches
cci flow run prepare_rlm_org --org ent-r1
cci flow run prepare_rlm_org --org ent-sb0

# 2. Extract schemas from both
python scripts/erd/schema_diff/extract_schema.py --org ent-r1 --output scripts/erd/schema_diff/260-schema.json
python scripts/erd/schema_diff/extract_schema.py --org rlm-base__ent-sb0 --output scripts/erd/schema_diff/262-schema.json

# 3. Diff the releases
python scripts/erd/schema_diff/diff_schemas.py \
  --baseline scripts/erd/schema_diff/260-schema.json \
  --target scripts/erd/schema_diff/262-schema.json \
  --report scripts/erd/schema_diff/260-vs-262-diff.md \
  --json scripts/erd/schema_diff/260-vs-262-diff.json \
  --impact

# 4. Refresh ERD against the target release
python scripts/erd/validate_erd_against_org.py --org rlm-base__ent-sb0 --patch \
  --report docs/erds/validation-report.md

# 5. Identify orphans across both orgs
python scripts/erd/cleanup_orphan_erd_fields.py \
  --orgs ent-r1,rlm-base__ent-sb0 \
  --dry-run --report docs/erds/orphan-candidates.md

# 6. Manually review orphan-candidates.md, then apply safe-only removals
python scripts/erd/cleanup_orphan_erd_fields.py \
  --orgs ent-r1,rlm-base__ent-sb0 \
  --safe-only --apply

# 7. Regenerate HTML
python scripts/erd/build_erds.py
```

### B. Verify a single field's ownership against Core source

When you need to know whether a field is real RC, real other-cloud, or a PDF artifact:

```python
# 1. Find the entity's canonical XML in codesearch:
mcp__plugin_codesearch_codesearch__search(
    query='file:"<EntityName>.entity.xml" repo:"core-262-public" branch:"262-patch"'
)

# 2. Read the entity XML:
mcp__plugin_codesearch_codesearch__blob(
    code_host="gitcore.soma.salesforce.com",
    org="core-2206",
    repo="core-262-public",
    ref="p4/262-patch",
    file_path="core/<module>-udd/java/resources/udd/<EntityName>.entity.xml"
)

# 3. Look for <flexField name="..."> elements with apiAccess/orgAccess gates
```

The 262-patch source is the canonical truth for what fields exist on a Revenue Cloud entity.

### C. Batch-process a long orphan list

Use `scripts/erd/orphan_batch_helper.py` to iterate through orphan classification:

```bash
# Prepare next batch input (top 20 by orphan count)
python scripts/erd/orphan_batch_helper.py prepare --batch 4 --size 20

# Dispatch researcher with the input JSON, merge findings into orphan-field-ownership.json, then:
python scripts/erd/orphan_batch_helper.py apply --batch 4

# Re-validate and produce the next orphan report
python scripts/erd/orphan_batch_helper.py validate --batch 4
```

## The Three Orphan Classifications

When the validator finds a field in `erd-data.json` that isn't in the org, classify it:

| Class | Meaning | Action |
|---|---|---|
| **A — RC feature-gated** | Field IS declared in RC-related UDD module (e.g. `core/billing-udd/`, `core/revenue-usage-udd/`) with an `apiAccess`/`orgAccess` gate that's not enabled in this org | **KEEP** — document as feature-gated. Field is canonical RC schema. |
| **B — Other-cloud** | Field IS declared but in a non-RC UDD module (e.g. `core/fieldservice-udd/` for FSL fields like `Asset.Availability`) | Decide: keep as cross-cloud documentation, OR remove if ERD is RC-only. |
| **C — PDF artifact** | Field is NOT declared in ANY UDD entity XML (PDF chapter sweep, `*Id` self-reference, related-list column, enum value, typo) | **REMOVE** — pollutes ERD without being real schema |

The standard `safe_only` mode of `cleanup_orphan_erd_fields.py` only removes class C (and only if `description` is empty AND `refersTo` is null). For class A/B and class C with descriptions, manual review against Core source is required.

## Common Pitfalls (verified from prior cleanup work)

### Pitfall 1: Ignoring the chapter-sweep signature
The v260 PDF extraction conflated fields from multiple objects in the same chapter into individual object field lists. Watch for:
- An entity with 20+ orphans where the canonical entity has only 4-10 flexFields → 100% PDF artifacts
- Top offenders historically: `AttrPicklistExcludedValue` (68 orphans, 4 real fields), `TaxPolicy` (61 vs 4), `QuoteLineRateCardEntry` (56 vs 7)

### Pitfall 2: Self-`Id` suffix orphans
A field like `EntityNameId` on `EntityName` is almost always a PDF artifact (related-list column harvested as a field). The actual field uses just the relationship name.

### Pitfall 3: Sibling-entity name pollution
PDF extraction sometimes attaches a sibling entity's fields to the wrong object. Example: `SeqPolicySelectionCondition` field-listed on `SequenceGapReconciliation`.

### Pitfall 4: Definition-vs-runtime split
DRO has paired entities — `FulfillmentStepDependencyDef` (design-time, references `DependsOnStepDefinition`) vs `FulfillmentStepDependency` (runtime, references `DependsOnStep`). Don't conflate.

### Pitfall 5: Polymorphic lookup confusion
Fields like `UsageEntitlementBucket.ProductId` don't exist as direct FKs — products reach those entities only through polymorphic `Parent`/`GrantBindingTarget` lookups.

### Pitfall 6: Casing matters
`Asset.RolledbackAssetAction` (lowercase 'b') is a PDF artifact — canonical is `RolledBackAssetAction` (capital 'B'). Same for `PricingAPIExecution` → canonical `PricingApiExecution`.

### Pitfall 7: Currency-conversion fields are real
The pattern `*CnvAmount` / `*CnvRate` / `*CnvDate` / `*IsoCode` IS canonical RC schema, gated by `Billing.orgHasInvoicingEnabled` or `orgHasMultiCurrency`. Always keep these — they appear identically across CreditMemoLineTax and InvoiceLineTax.

## What Was Verified

As of 2026-05-27, 127 entities have been individually verified against canonical Core UDD source at `gitcore.soma.salesforce.com/core-2206/core-262-public@p4/262-patch`. Findings persisted at:

- `.agents/artifacts/orphan-field-ownership.json` — structured per-entity classification database
- `.agents/artifacts/orphan-field-ownership.md` — narrative research findings
- `.agents/artifacts/262-vs-260-core-schema-research.md` — the 262 release schema research from Core source
- `.agents/artifacts/262-org-vs-core-cross-validation.md` — cross-validation between Core source and org introspection

Outcome: 498 PDF artifacts removed, 38 orphans remain (all explicitly-documented feature-gated or cross-cloud fields).

## Related

- `revenue-cloud-data-model` skill — the data model itself
- `sfdmu-data-plans` skill — uses ERD to validate plan CSVs against schema
- `docs/upgrades/262-upgrade-plan.md` — release certification log
- `scripts/erd/schema_diff/` — schema diff tooling
