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
2. **Always cross-validate against TWO orgs** when classifying orphan fields — a field present in one org but absent in another is likely feature-gated, not removed. Hold the **org shape constant** across the pair (two `ent` orgs, say): a field gated by a shape you didn't build looks identical to a removed one.
3. **Verify against Core source** before bulk-removing fields. The validators surface candidates; codesearch confirms ground truth. For a pre-GA release there may be no Core UDD branch yet (264 had none), in which case a live org is the only ground truth and the previous release's UDD verification carries forward unchanged rather than being re-run.
4. **Use `prepare_rlm_org`-built scratch orgs.** The 264 refresh used two of them — `rlm-base__264merged` and `rlm-base__264fresh` — and diffed against the *committed* `scripts/erd/schema_diff/262-schema.json` rather than a live 262 org, so the baseline is byte-identical to what the previous refresh was built from.
5. **All schema diff scripts default to skipping custom fields**. Pass `--include-custom` only for project-internal tooling that needs to see deployed `RLM_*__c` fields.

## DO NOT

1. **DO NOT** patch `erd-data.json` from a single org without cross-validating against another release/configuration. You'll baseline feature-gated noise as canonical schema.
2. **DO NOT** use `techido-260` or other ad-hoc orgs for baseline — only fresh `prepare_rlm_org` builds.
2a. **DO NOT** trust `validate_erd_against_org.py --patch` to remove anything. It only **adds** — `patch_erd` never increments its `fields_removed` counter, so the `0` that `main` prints for it is unconditional, not a finding. Fields the release retired have to be removed deliberately (see Workflow A step 4b).
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

Worked example: the 262 → 264 refresh. `diff_schemas.py` needs **Python 3.10+**
(it uses `X | None` annotations), so run these with the interpreter CumulusCI is
installed under, not a 3.9 system Python.

```bash
# 1. Build TWO scratch orgs of the SAME shape on the target release
cci flow run prepare_rlm_org --org 264merged
cci flow run prepare_rlm_org --org 264fresh

# 2. Extract from both, then confirm they agree field-for-field before trusting either
python scripts/erd/schema_diff/extract_schema.py --org rlm-base__264merged \
  --output scripts/erd/schema_diff/264-schema.json
python scripts/erd/schema_diff/extract_schema.py --org rlm-base__264fresh \
  --output /tmp/264-crossval.json
# any object/field difference between the two is org noise, not schema — resolve it first

# 3. Diff against the PREVIOUS release's committed snapshot (not a live old org)
python scripts/erd/schema_diff/diff_schemas.py \
  --baseline scripts/erd/schema_diff/262-schema.json \
  --target scripts/erd/schema_diff/264-schema.json \
  --report scripts/erd/schema_diff/262-vs-264-diff.md \
  --json scripts/erd/schema_diff/262-vs-264-diff.json \
  --impact

# 4a. Additions: patch what the org has and the ERD lacks
python scripts/erd/validate_erd_against_org.py --org rlm-base__264merged --patch \
  --report docs/erds/validation-report.md

# 4b. Removals: --patch will NOT do these. Take the diff's `removed` list, delete
#     those fields AND their `relationships` rows, and recompute `stats`.
#     Back up first — `docs/erds/erd-data.json.bak*` is gitignored.

# 5. Orphans across both orgs — expect the previous release's documented
#    feature-gated/cross-cloud set to still be listed. Only entries that appear in
#    the diff's `removed` list are this release's doing.
python scripts/erd/cleanup_orphan_erd_fields.py \
  --orgs rlm-base__264merged,rlm-base__264fresh \
  --dry-run --report docs/erds/orphan-candidates.md

# 6. Rewrite the whole `metadata` block (release, apiVersion, baseline*, source,
#    lastRefreshedOn, note), then regenerate the HTML
python scripts/erd/build_erds.py

# 7. Re-run step 4a WITHOUT --patch. Done means: gaps 0, missing fields 0,
#    missing relationships 0, and orphans reduced by exactly the release's removals.
```

Then sweep the figures out of the **four** docs that restate them —
`docs/erds/README.md`, `.cursor/skills/revenue-cloud-data-model/SKILL.md`,
`scripts/ai/README.md`, and this file. All four carry object and field counts with no
generator behind them, so they go stale silently. The 262→264 refresh swept the first
two and this one and **missed `scripts/ai/README.md`**, leaving `query_erd.py stats`
printing 264 figures while its own README described 262 — so sweep by grepping the
outgoing numbers, not by walking a list from memory.

Two other things the same refresh had to fix by hand, worth checking rather than
assuming:

- **`validate_erd_against_org.py --patch` corrects `refersTo` but not
  `relationshipName` or `description`.** Those three name the same target, so a
  repaired field can end up asserting a correct `refersTo` beside a
  `relationshipName` and a description belonging to the *old, wrong* target. That is
  worse than a uniformly wrong field, because two of the three still read as
  authoritative — and `relationshipName` is the SOQL parent-traversal token, so a
  stale one is a hard `INVALID_FIELD`. Sweep all three against the org describe
  together.
- **`refersTo` must match an ERD node key exactly.** `query_erd.build_relationship_index`
  tests `ref in erd["objects"]`, which is case-sensitive, so a target that is right in
  API terms but spelled differently from the node key (`PricebookEntry` vs the node
  `PriceBookEntry`) makes traversal stop silently rather than error. The same applies to
  a target carrying a parenthetical like `Invoice (the master object)`.

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

# Dispatch researcher with the input JSON, merge findings into
# .agents/artifacts/orphan-fields/orphan-field-ownership.json, then:
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

**264 (2026-08-15).** `erd-data.json` is a 264 capture: 263 objects, 4,252 fields,
674 relationships. Cross-validated across `rlm-base__264merged` and
`rlm-base__264fresh` (both `ent`), which agreed field-for-field — 254 describable
objects, 3,913 platform fields each. 264 has no Core UDD branch or Metadata Coverage
Report yet, so the Core verification below carries forward from 262 rather than being
re-run, and a live org is ground truth for this release. The refresh added 70 fields
and 12 relationships, removed the 8 fields 264 retired, and left the previous
release's documented orphan set untouched. Delta:
`scripts/erd/schema_diff/262-vs-264-diff.md`.

Three data-quality classes were also repaired against the org, all pre-existing:
8 relationship rows whose target contradicted the org (including
`ProductUsageResourcePolicy.UsageAggregationPolicyId`, which 264 makes the *only*
binding site for the accumulation policy and which pointed at `UsageResource`
instead of `UsageResourceBillingPolicy`); 94 reference fields with a null `refersTo`;
and 10 `refersTo` values whose casing matched no ERD node, which silently broke
traversal (`PricebookEntry` vs the ERD's `PriceBookEntry`).

**262 (2026-05-27).** 127 entities individually verified against canonical Core UDD
source at `gitcore.soma.salesforce.com/core-2206/core-262-public@p4/262-patch`.
Outcome: 498 PDF artifacts removed, 38 orphans remain (all explicitly-documented
feature-gated or cross-cloud fields). Findings persisted at:

- `.agents/artifacts/orphan-fields/orphan-field-ownership.json` — structured per-entity classification database
- `.agents/artifacts/orphan-fields/orphan-field-ownership.md` — narrative research findings
- `.agents/artifacts/audit-262/262-vs-260-core-schema-research.md` — the 262 release schema research from Core source
- `.agents/artifacts/audit-262/262-org-vs-core-cross-validation.md` — cross-validation between Core source and org introspection

## Related

- `revenue-cloud-data-model` skill — the data model itself
- `sfdmu-data-plans` skill — uses ERD to validate plan CSVs against schema
- `scripts/erd/schema_diff/` — schema diff tooling
