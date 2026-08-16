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
2. **Always cross-validate against TWO orgs** when classifying orphan fields — a field present in one org but absent in another is feature-gated, not removed. Hold the **release** constant and let the **shapes differ**: `find_orphans` keeps a field present in *any* queried org, so a second org can only rescue fields from deletion, never accuse one. That makes complementary shapes (`ent` + `pde`, feature on + off) the only pairing that can actually disprove an orphan, and a same-shape pair worthless — it cannot disagree, so "two orgs agreed" is not corroboration. Absence is never positive evidence of removal either way; see DO NOT #1.
3. **Verify against Core source** before bulk-removing fields. The validators surface candidates; codesearch confirms ground truth. For a pre-GA release there may be no Core UDD branch yet (264 had none), in which case a live org is the only ground truth and the previous release's UDD verification carries forward unchanged rather than being re-run.
4. **Use `prepare_rlm_org`-built scratch orgs.** The 264 refresh used two of them — `rlm-base__264merged` and `rlm-base__264fresh` — and diffed against the *committed* `scripts/erd/schema_diff/262-schema.json` rather than a live 262 org, so the baseline is byte-identical to what the previous refresh was built from.
5. **All schema diff scripts default to skipping custom fields**. Pass `--include-custom` only for project-internal tooling that needs to see deployed `RLM_*__c` fields.

## DO NOT

1. **DO NOT** treat org absence as proof of removal, and **DO NOT** classify orphans from a single org. Two rules that pull in opposite directions, because `find_orphans` unions fields across orgs (`present_in_any`) so adding an org can only ever *shrink* the orphan set:
   - **Release: hold it constant.** A field added in 264 is absent from a 262 org for reasons unrelated to removal, and 262's extra fields aren't the ERD's subject. A cross-release second org is worse than one org.
   - **Shape: do NOT hold it constant.** Two `ent` orgs cannot disagree about a field gated out of `ent`, so the pair corroborates nothing while reading as if it did. Prefer complementary shapes.
   - **Ceiling on the whole method:** a feature that *neither* org enables looks removed in both, however many orgs you add. Positive evidence of removal is the release diff (present in the N−1 snapshot, absent in N) or canonical Core UDD source. Require one of those before `--aggressive --apply`; org absence is a candidate filter, not a verdict.

   The 264 refresh used `264merged` + `264fresh`, both **Enterprise** — a same-shape pair, so its orphan verdicts rest on orgs that could not disagree. Nothing was deleted on that basis (the 8 retirements came from the release diff; the remaining 58 were kept and classified), but don't cite that pass as the model for aggressive removal.
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
# 1. Build TWO scratch orgs of the SAME shape on the target release.
#    Same shape is what step 2 needs: it is an equality check on the extraction, and
#    it is only meaningful if both orgs expose the same feature set.
#    Step 5 (orphan classification) wants the opposite — see the note there. The two
#    checks have genuinely different requirements; a same-shape pair satisfies one.
cci flow run prepare_rlm_org --org 264merged
cci flow run prepare_rlm_org --org 264fresh

# 2. Extract from both, then confirm they agree field-for-field before trusting either.
#    Pass no object flag: the default reads the list from erd-data.json. Do NOT pass
#    --all-objects — it fails with EXCEEDED_ID_LIMIT (EntityDefinition has no queryMore).
#    Only ONE snapshot is committed per release; the second stays in /tmp by design.
python scripts/erd/schema_diff/extract_schema.py --org rlm-base__264merged \
  --output scripts/erd/schema_diff/264-schema.json
python scripts/erd/schema_diff/extract_schema.py --org rlm-base__264fresh \
  --output /tmp/264-crossval.json
# any object/field difference between the two is org noise, not schema — resolve it first
# 264 result (2026-08-15, re-confirmed): 254 objects / 3,913 fields each, 0 differences

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
#
#    Unlike step 2, this wants COMPLEMENTARY shapes. Orphans are unioned across orgs
#    (`present_in_any`), so the step-1 same-shape pair cannot disagree about a field
#    gated out of that shape — it produces a list, not a corroborated one. Either add
#    a differently shaped org of the same release, or treat the output strictly as
#    candidates and confirm each against the release diff / Core source. The 264 pass
#    did the latter: both orgs were Enterprise, so it removed only the 8 fields the
#    release diff independently showed gone and kept all 58 remaining candidates.
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

**Then run `python tests/test_erd_doc_counts.py`, which now gates part of that sweep.**
It pins the headline triple *and* the per-domain counts — the Domain Overview table in
`revenue-cloud-data-model/SKILL.md` and every `domains/*.md` headline — to
`erd-data.json`, plus `erd-data.json` against its own `stats` block so a stale
generator cannot certify the docs. The per-domain layer is what the manual sweep never
reached: at 264 the headline triple was correct in all five places while **7 of the
table's 9 rows** were wrong, summing to 185 against an actual 263. It was not simple
staleness either — `rates.md` over-claimed 15 against 11 — so grepping the outgoing
numbers would not have caught it. All four docs above are covered, `scripts/ai/README.md`
included — its citation wraps mid-phrase (`263` / `objects, 4,252 platform fields, 674
verified relationship edges`), so the check matches over a sliding window rather than
per line. What it does **not** cover is the other figures those files carry: the
org-describe pair (254 objects / 3,913 fields), the 1,148 reference-field total, and
the orphan and gap baselines. Those still need the grep.

The count definition it enforces: a domain's objects are all objects carrying that
domain **including** the `(Core Object)` variants (the only reading that sums to the
headline), with `Advanced Approvals` folded into `Approvals` as `DOMAIN_MAP` does.

Two other things the same refresh had to fix by hand, worth checking rather than
assuming:

- **`validate_erd_against_org.py --patch` fixes nothing on a field the ERD already
  has.** Both patch branches are guarded by `if f.name not in obj_fields`
  (`validate_erd_against_org.py:226-260`), so patching is *add-only at field
  granularity*: it writes `refersTo`, `relationshipName`, `description`, and `type`
  only for fields it is adding. For a field already present, a wrong or null value in
  any of those survives every patch run, indefinitely — which is why the 264 refresh
  had to repair 94 null `refersTo`, 6 `relationshipName`, and 44 `type` values by
  hand, and why ~1,100 more `type` contradictions are still outstanding (pack 144).
  Do not read a clean `--patch` run as evidence that existing fields agree with the
  org. Those four attributes all name the same target, so a half-repaired field is
  worse than a uniformly wrong one: the untouched ones still read as authoritative,
  and `relationshipName` is the SOQL parent-traversal token, so a stale one is a hard
  `INVALID_FIELD`. Sweep all four against the org describe together.
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

# Re-validate and produce the next orphan report. --orgs is REQUIRED, has no default,
# and rejects a repeated alias: pass two distinct orgs on the target release with
# complementary shapes. It used to default to a 260/262 pair, so this command silently
# classified orphans against the wrong release.
python scripts/erd/orphan_batch_helper.py validate --batch 4 \
  --orgs rlm-base__264ent,rlm-base__264pde
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
`ProductUsageResourcePolicy.UsageAggregationPolicyId`, which pointed at
`UsageResource` instead of `UsageResourceBillingPolicy` — the same accumulation
policy that `UsageResourcePolicy.UsageAggregationPolicyId` also binds, at resource
rather than product-and-resource level, so neither is the sole binding site);
94 reference fields with a null `refersTo`;
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
