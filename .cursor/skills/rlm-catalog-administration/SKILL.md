# RLM Catalog Administration — Load Products and Pricing from Source Materials

Use this skill when a user asks to load, seed, extend, or update **Products
and/or Pricing** in an RLM (Revenue Lifecycle Management) catalog based on an
external source — a PDF price sheet, a public product/pricing web page, a
vendor spec, or a free-form natural-language description. The skill covers
translating the source into catalog-shaped artifacts (product definitions,
attribute values, price book entries, pricing procedures where applicable),
choosing the correct load path, and validating the resulting catalog before
handoff.

This skill is consumable by Cursor, Claude Code, GitHub Copilot, Codex,
Windsurf, Aider, and any other agent that can read repository files. Follow
the DO NOT list before proposing any load command.

## Quick Rules

1. Always confirm source type (PDF / URL / description) and target org before extracting.
2. Any time more than one record will be created or uploaded, only use SFDMU data plans for bulk load; see `.cursor/skills/sfdmu-data-plans/SKILL.md`. Do **not** fall back to `sf data import bulk`, `sf data upsert bulk`, Composite REST, or the SObject MCPs to work around an SFDMU issue — fix the plan instead (see Troubleshooting below).
3. For product/catalog structure loads (Product2, ProductCategory, ProductComponentGroup, ProductRelatedComponent, etc.), imitate `./datasets/sfdmu/qb/en-US/qb-pcm/` — its `export.json` is the reference for which objects need CSVs and which fields to include. For **pricing** loads (PricebookEntry, ProductSellingModelOption, PriceAdjustmentSchedule, AttributeBasedAdjRule, BundleBasedAdjustment, CostBookEntry, PricebookEntryDerivedPrice), imitate `./datasets/sfdmu/qb/en-US/qb-pricing/` instead — the object set and lookup pattern differ from `qb-pcm`.
4. SFDMU plans must not contain hardcoded Salesforce IDs. Lookups reference records via natural keys (`StockKeepingUnit`, `Name`, `Code`, `IsStandard`, etc.). When the target org already contains records that a plan needs to reference (e.g. an existing `Pricebook2`, `ProductSellingModel`, or `Product2`), **ship a companion CSV for that object in the plan directory, populated by querying the target org first** — that is how SFDMU resolves lookups in `csvfile`-source mode. See the `Product2.csv` / `Pricebook2.csv` / `ProductSellingModel.csv` files in `datasets/sfdmu/qb/en-US/qb-pricing/` for the canonical shape.
5. Wire **any PricebookEntry work** — creating, loading, updating, or overlaying — through `.cursor/skills/pricing-wiring/SKILL.md`. This includes the base PBE + `ProductSellingModelOption` load itself, not just procedure/recipe/overlay changes.
6. Present a summarized plan to the user in terms of what will be loaded or updated.
7. No need to make the temporary directory permanent as a plan - ask the user to confirm, then act directly from the temp directory.
8. Unless told to do so explicitly, do not set the IsSoldOnlyWithOtherProds field on Product2.
9. When a load session spans multiple phases (structure → pricing → attributes → images → …), re-read this skill **and** the linked skill for the incoming phase before starting it. Do not treat a new phase as a continuation of the previous one — its rules and reference plans differ.


## DO NOT

- **DO NOT** use SObject MCPs to load/update records in Salesforce without explicitly asking the user and receiving confirmation.
- **DO NOT** invent SKUs, prices, or attribute values that are not present in the source. If a value is missing, ask the user or mark the row for review — do not synthesize.
- **DO NOT** modify shipped procedures / decision tables / pricing recipes to accommodate a catalog load. If a load appears to require it, stop and route to `.cursor/skills/pricing-wiring/SKILL.md`.
- **DO NOT** skip the intermediate CSV / YAML review step, even for "small" catalogs. Every load produces a reviewable intermediate at `tmp/catalog-loads/<slug>/` first, then loads from that directory after user confirmation.
- **DO NOT** hardcode Salesforce record IDs, org URLs, or user references inside any file that will be reused or committed. Plans must be portable across orgs — reference by natural key (SKU, Name, Code) and let SFDMU resolve at run time.
- **DO NOT** bypass SFDMU with direct `sf data import bulk`, `sf data upsert bulk`, Composite REST, or MCP inserts for business records (Product2, PricebookEntry, ProductSellingModelOption, ProductRelatedComponent, ProductCategoryProduct, etc.), even when SFDMU is misbehaving. Fix the plan (usually a missing reference CSV in the plan directory) — see Troubleshooting. The direct-bulk path produces non-repeatable, ID-baked artifacts that cannot be re-run across orgs.
- **DO NOT** trust an SFDMU "Inserted N" summary line on its own. Always cross-check with a SOQL count on the target and read `<Object>_insert_target.csv` in the plan's `target/` directory — SFDMU reports pass-level counts that do not always match batch-level success.

---

## Entry Conditions

Read this skill before loading or extending catalog Products or Pricing from
any external source.

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Load products from a vendor PDF price sheet | Yes | Extract to intermediate, review, then load. |
| Load products from a public product/pricing web page | Yes | Confirm scraping is permitted; capture source URL and fetch date. |
| Seed a catalog from a free-form natural-language description | Yes | Ask clarifying questions to nail down SKUs, price types, currency, and attributes before generating. |
| Add a handful of new products to an existing catalog | Yes | Reuse existing categories/attributes; do not fork the taxonomy. |
| Change pricing behavior (procedures, recipes, overlays) | Usually no | Route to `.cursor/skills/pricing-wiring/SKILL.md`; return here only for the data side. |
| Author or CRUD pricing procedures / Expression Sets | No | Route to `.cursor/skills/expression-sets/SKILL.md`. |
| Bulk data movement between orgs unrelated to catalog | No | Route to `.cursor/skills/sfdmu-data-plans/SKILL.md`. |
| Validate ERD/schema drift after a load | No, but adjacent | Route to `.cursor/skills/schema-validation/SKILL.md` after load. |

---

## Source Intake

Before extracting, capture and record:

| Field | Example | Why it matters |
|-------|---------|----------------|
| Source type | PDF / URL / description | Determines extraction path. |
| Source location | Path or URL | Traceability; reruns; audit. |
| Fetch date | 2026-07-23 | Prices drift; freshness matters. |
| Currency / price type(s) | USD List, USD MSRP | Drives Price Book / Price Type wiring. |
| Locale / market | US, EMEA | May require multi-currency setup. |
| Confidence | High / Medium / Low | Flags rows needing human review. |

If the source is a **natural-language description**, ask the user to confirm
at minimum: SKU convention, price type(s), currency, whether attributes/options
are in scope, and whether the target catalog already exists.

---

## Extraction and Normalization

1. Convert the source to a normalized intermediate artifact **before** touching
   catalog metadata. Prefer CSV for tabular product/price rows, YAML for
   hierarchical catalogs with categories, attributes, and options.
2. Store the intermediate under a working directory the user can review
   (e.g., `tmp/catalog-loads/<slug>/`), never inline in a skill or committed
   config unless the user asks.
3. Keep one row per **(Product, PriceType, Currency)** tuple; do not collapse
   price variants into a single product row.
4. Preserve the source column/label names alongside normalized names so the
   review is reversible.
5. Flag low-confidence rows (OCR uncertainty, ambiguous units, missing SKUs)
   for human review before load.

---

## Load Path Selection

Pick the load path based on target org, volume, and reversibility needs:

| Path | When to use | Notes |
|------|-------------|-------|
| SFDMU data plan | Bulk load (dozens+ of products) or repeatable seeding across orgs | See `.cursor/skills/sfdmu-data-plans/SKILL.md`. |
| Metadata API (source-controlled) | Catalog structure, categories, attributes, procedures | Org-agnostic; use placeholders. |
| Manual UI entry | One-off small changes, or when the user explicitly requests it | Document what was done for reproducibility. |
| Connect API (runtime CRUD) | Pricing procedure / Expression Set adjustments | Route to `.cursor/skills/expression-sets/SKILL.md`. |

---

## Pricing Wiring Handoff

**Pricing object loading is not covered here.** This skill covers catalog
structure only (Product2, ProductCategory, ProductClassification,
ProductComponentGroup, ProductRelatedComponent, ProductCategoryProduct,
ProductRelationshipType). The moment the load involves any of the objects
below, hand off to `.cursor/skills/pricing-wiring/SKILL.md` for the plan
authoring, then return here only if you also need to add structure records:

- `PricebookEntry`, `Pricebook2`
- `ProductSellingModelOption`, `ProductSellingModel`, `ProductRampSegment`,
  `ProrationPolicy`
- `PriceAdjustmentSchedule`, `PriceAdjustmentTier`, `AttributeBasedAdjRule`,
  `AttributeBasedAdjustment`, `AttributeAdjustmentCondition`,
  `BundleBasedAdjustment`
- `CostBook`, `CostBookEntry`
- `PricebookEntryDerivedPrice`

Also route out for related lifecycle work:

- Recipes, procedures, overlays, decision tables →
  `.cursor/skills/pricing-wiring/SKILL.md`
- Layering model, prerequisites, and overlays →
  `.cursor/skills/pricing-wiring/SKILL.md`
- Expression Set authoring, CRUD, activation lifecycle →
  `.cursor/skills/expression-sets/SKILL.md`

---

## Examples

<!-- TODO(vance): replace / extend with real user flows. -->

### Example 1 — Load products from a vendor PDF

User request: "Here's the ACME 2026 price sheet PDF — load the products and
USD list pricing into the RLM catalog."

Do:

1. Capture source metadata (path, fetch date, currency = USD List).
2. Extract tabular rows to `tmp/catalog-loads/acme-2026/products.csv` with
   source-preserving columns.
3. Flag low-confidence OCR rows for user review.
4. Generate an SFDMU plan referencing the normalized CSV (see
   `.cursor/skills/sfdmu-data-plans/SKILL.md`).
5. Dry-run against a scratch org; validate; then load target.
6. Hand off to `pricing-wiring` if procedure or recipe changes are needed.

### Example 2 — Seed a catalog from a description

User request: "Create a small catalog for a 3-tier SaaS product — Starter,
Pro, Enterprise — with monthly and annual pricing in USD."

Do:

1. Confirm SKU convention, price type(s), and whether options/attributes are in
   scope.
2. Generate `tmp/catalog-loads/saas-demo/catalog.yml` with categories,
   products, price types, and per-tier price entries.
3. Review the YAML with the user before generating metadata or SFDMU plans.
4. Load, then validate.

### Example 3 — Extend an existing catalog from a web page

User request: "Add these three new products from the vendor's public product
page to our existing RLM catalog."

Do:

1. Fetch the URL; record fetch date and confirm scraping is permitted.
2. Reuse existing Category and Attribute records — do not fork the taxonomy.
3. Match against existing SKUs first; only create new Products for genuinely
   new SKUs.
4. Load via SFDMU or Metadata API depending on scope; validate.

---

## Validation Checks

Run the applicable checks after every catalog load. Every load ends with an
**org-side** verification, not just the SFDMU / import summary log.

```bash
# Local plan validation (runs before load)
python scripts/validate_sfdmu_v5_datasets.py

# Org-side verification (runs after load, for every object the plan touched)
sf data query -q "SELECT COUNT() FROM <Object> WHERE <load-filter>" --target-org <alias>
```

Also review:

- **SOQL count on the target matches the CSV row count for every loaded
  object.** If any count is off, treat the load as failed regardless of what
  the SFDMU summary said.
- **`<Object>_insert_target.csv` in the plan's `target/` directory must
  either be absent or empty of `#N/A` / `Errors` rows.** Its existence with
  content means SFDMU silently dropped records even if the summary shows
  "Inserted N".
- Product count in target org matches the intermediate artifact.
- Price Book Entries exist for every (Product, PriceType, Currency) tuple.
- No duplicate SKUs were introduced.
- Source metadata (path, fetch date, currency) is recorded in the load
  artifact directory.
- Schema drift check: `.cursor/skills/schema-validation/SKILL.md`.
- Doc consistency before PR: `.cursor/skills/doc-consistency/SKILL.md`.

---

## Troubleshooting

**Symptom: SFDMU reports "Inserted N" but the target has 0 records.**
Open the plan's `target/<Object>_insert_target.csv`. If every row shows `#N/A`
in lookup FK columns (`Product2Id`, `Pricebook2Id`, `ProductSellingModelId`,
etc.) with errors like `Required fields are missing: [Product2Id, ...]` or
`To save this price book entry, first specify a product.`, SFDMU could not
resolve the natural-key lookup.

**Root cause: missing companion CSVs.** In `csvfile`-source mode, SFDMU
resolves lookup references from *other CSVs shipped in the plan directory*,
not from the target org. If your plan references `Product2` (via
`Product2.StockKeepingUnit`) but the plan directory has no `Product2.csv`,
every lookup returns `#N/A`.

**Fix (canonical):** query the target for the referenced records and drop
them into the plan directory as companion CSVs. This preserves
zero-hardcoded-IDs and keeps the plan portable.

```bash
# Example — for a PricebookEntry load that references existing Product2,
# Pricebook2, and ProductSellingModel records already in the target org:
sf data query --result-format csv \
  -q "SELECT Id, StockKeepingUnit, Name FROM Product2 WHERE StockKeepingUnit IN (...)" \
  --target-org <alias> > <plan-dir>/Product2.csv

sf data query --result-format csv \
  -q "SELECT Id, Name, IsStandard FROM Pricebook2 WHERE IsStandard = true" \
  --target-org <alias> > <plan-dir>/Pricebook2.csv

sf data query --result-format csv \
  -q "SELECT Id, Name, SellingModelType FROM ProductSellingModel WHERE Status = 'Active'" \
  --target-org <alias> > <plan-dir>/ProductSellingModel.csv
```

Then reference each companion object in `export.json` (see `qb-pricing/export.json`
for the exact objects-array shape) and re-run SFDMU. The `qb-pcm` and
`qb-pricing` reference plans ship the full set of companion CSVs — study those
before authoring a new plan.

**Anti-pattern (do not do this):** falling back to `sf data import bulk` /
`sf data upsert bulk` / Composite REST with pre-resolved IDs. That path
produces an ID-baked artifact that cannot be re-run on another org, breaks
the "no hardcoded IDs" rule (Quick Rule 4), and violates the DO NOT list.

**Symptom: `LineEnding is invalid on user data. Current LineEnding setting
is LF`.** You almost never hit this via SFDMU, but if you fall through to
`sf data import bulk` (which you should not — see above), note that Bulk API
2.0 defaults to `LineEnding=LF` while Python's `csv.writer` emits CRLF by
default. Set `lineterminator="\n"` when writing.

**Symptom: SFDMU "Insert" of a record whose object has a system-enforced
unique key (`PricebookEntry` on `(Pricebook2Id, Product2Id,
ProductSellingModelId, CurrencyIsoCode)`, `ProductSellingModelOption` on
`(Product2Id, ProductSellingModelId)`) fails on rerun with `DUPLICATE_VALUE`.**
Use `Upsert` with a composite `externalId` covering the unique key, not
`Insert`. `qb-pricing/export.json` demonstrates the shape.
