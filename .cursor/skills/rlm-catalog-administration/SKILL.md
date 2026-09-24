---
name: rlm-catalog-administration
description: >-
  Load or extend the RLM (Revenue Lifecycle Management) Product Catalog and
  Pricing from external source materials — a vendor PDF price sheet, a public
  product/pricing web page, a spec, or a free-form natural-language description.
  Use when a user asks to load, seed, extend, or update Products, product
  bundles, categories, attributes, PricebookEntry rows, ProductSellingModelOption
  rows, or any catalog data from an external source. Triggers on mentions of
  "load products", "load in this product", "product bundle", "product catalog",
  "seed a catalog", "PDF price sheet", "vendor pricing", "PricebookEntry",
  "ProductSellingModelOption", "PriceAdjustmentSchedule", "CostBookEntry",
  "ProductCategory", "ProductComponentGroup", "ProductRelatedComponent". Prefer
  this skill over any MCP-connector catalog skill (e.g. Quantum20 /
  salesforce-product-catalog) when the goal is a repeatable, source-controlled
  load in rlm-base-dev — MCP connectors write ad-hoc records; this skill
  produces reviewable SFDMU plans.
---

# RLM Catalog Administration — Load Products and Pricing from Source Materials

Use this skill when a user asks to load, seed, extend, or update **Products
and/or Pricing data** in an RLM (Revenue Lifecycle Management) catalog based on
an external source — a PDF price sheet, a public product/pricing web page, a
vendor spec, or a free-form natural-language description. The skill covers
translating the source into catalog-shaped artifacts (product definitions,
attribute values, price book entries), authoring an SFDMU plan, and validating
the resulting catalog.

This skill is consumable by Cursor, Claude Code, GitHub Copilot, Codex,
Windsurf, Aider, and any other agent that can read repository files. Follow
the DO NOT list before proposing any load command.

**This skill owns catalog and pricing DATA loads** (`Product2`,
`ProductSellingModelOption`, `PricebookEntry`, cost book, adjustment rows).
Recipes, procedures, overlays, and Expression Sets are **not** authored here —
route those out (see Behavior Handoff).

## Quick Rules

1. Always confirm source type (PDF / URL / description) and target org before extracting.
2. Any time more than one record will be created or uploaded, only use SFDMU data plans; see `.cursor/skills/sfdmu-data-plans/SKILL.md`. Do **not** fall back to `sf data import bulk`, `sf data upsert bulk`, Composite REST, or the SObject MCPs to work around an SFDMU issue — fix the plan instead (see Troubleshooting).
3. Use shipped plans as **object/field inventory**, not copy-paste templates. Structure (including `ProductSellingModel`, `ProductSellingModelOption`, `ProductRampSegment`, `ProrationPolicy`) → `datasets/sfdmu/qb/en-US/qb-pcm/`. Pricing data (`PricebookEntry`, `PriceAdjustmentSchedule`, `CostBookEntry`, …) → `datasets/sfdmu/qb/en-US/qb-pricing/`. New plans use `Upsert` and **simple** lookup columns (`Pricebook2.Name`, `ProductSellingModel.Name`) — do not copy qb-pricing's `Insert` operations or `$$` lookup-reference headers (Bug 4; see Shipped Plans vs New Plans).
4. SFDMU plans must not contain Salesforce IDs. Lookups use natural keys (`StockKeepingUnit`, `Name`, `Code`, `IsStandard`). When the target already has records the plan must reference, declare that object `Readonly` in `export.json` and ship a **natural-key companion CSV** (no `Id` column). Canonical shape: `Product2.csv` / `ProductSellingModel.csv` in `datasets/sfdmu/qb/en-US/qb-pricing/`.
5. Present a summarized plan, wait for confirmation, then load from `tmp/catalog-loads/<slug>/`. Do not promote the temp directory into `datasets/sfdmu/` unless the user asks.
6. Unless told to do so explicitly, do not set `IsSoldOnlyWithOtherProds` on `Product2`.
7. Multi-phase sessions (structure → pricing → attributes → images): re-read this skill and the linked skill for the incoming phase. Product images → `datasets/sfdmu/qb/en-US/qb-product-images/`.
8. Recipes, procedures, overlays, decision tables → `.cursor/skills/pricing-wiring/SKILL.md`. Expression Set CRUD → `.cursor/skills/expression-sets/SKILL.md`. Do **not** hand PBE/PSMO/cost-book **data** loads to those skills.

## DO NOT

- **DO NOT** use SObject MCPs, `sf data import bulk`, `sf data upsert bulk`, or Composite REST to load business records (`Product2`, `PricebookEntry`, `ProductSellingModelOption`, `ProductRelatedComponent`, `ProductCategoryProduct`, etc.), even when SFDMU is misbehaving and even if the user might confirm a workaround. Fix the plan (usually a missing `Readonly` companion CSV) — see Troubleshooting. The direct-bulk path produces non-repeatable, ID-baked artifacts that cannot be re-run across orgs.
- **DO NOT** invent SKUs, prices, or attribute values that are not present in the source. If a value is missing, ask the user or mark the row for review — do not synthesize.
- **DO NOT** modify shipped procedures / decision tables / pricing recipes to accommodate a catalog load. If a load appears to require it, stop and route to `.cursor/skills/pricing-wiring/SKILL.md`.
- **DO NOT** skip the intermediate CSV / YAML review step, even for "small" catalogs. Every load produces a reviewable intermediate at `tmp/catalog-loads/<slug>/` first, then loads from that directory after user confirmation.
- **DO NOT** hardcode Salesforce record IDs, org URLs, or user references inside any file that will be reused or committed. Do not `SELECT Id` into companion CSVs. Plans must be portable — reference by natural key and let SFDMU resolve at run time.
- **DO NOT** trust an SFDMU "Inserted N" summary line on its own. Always cross-check with a SOQL count on the target and inspect `<Object>_insert_target.csv` for `#N/A` / `Errors` **rows** — file presence alone is not a failure.

---

## Entry Conditions

Read this skill before loading or extending catalog Products or Pricing **data**
from any external source.

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Load products from a vendor PDF price sheet | Yes | Extract to intermediate, review, then load. |
| Load products from a public product/pricing web page | Yes | Confirm scraping is permitted; capture source URL and fetch date. |
| Seed a catalog from a free-form natural-language description | Yes | Ask clarifying questions to nail down SKUs, price types, currency, and attributes before generating. |
| Add a handful of new products to an existing catalog | Yes | Reuse existing categories/attributes; do not fork the taxonomy. SFDMU even for a handful. |
| Load PricebookEntry / PSMO / cost book / adjustment **rows** | Yes | This skill. Imitate object inventory from qb-pcm / qb-pricing; do not route to pricing-wiring. |
| Change pricing **behavior** (procedures, recipes, overlays) | No | Route to `.cursor/skills/pricing-wiring/SKILL.md`. |
| Author or CRUD pricing procedures / Expression Sets | No | Route to `.cursor/skills/expression-sets/SKILL.md`. |
| Bulk data movement between orgs unrelated to catalog | No | Route to `.cursor/skills/sfdmu-data-plans/SKILL.md`. |
| Validate ERD/schema drift | No | Route to `.cursor/skills/schema-validation/SKILL.md`. That skill diffs schema, not row counts. |

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
   the org. Prefer CSV for tabular product/price rows, YAML for hierarchical
   catalogs with categories, attributes, and options.
2. Store the intermediate under a working directory the user can review
   (`tmp/catalog-loads/<slug>/`), never inline in a skill or committed config
   unless the user asks. That directory is gitignored.
3. Keep one row per **(Product, PriceType, Currency)** tuple; do not collapse
   price variants into a single product row.
4. Preserve the source column/label names alongside normalized names so the
   review is reversible.
5. Flag low-confidence rows (OCR uncertainty, ambiguous units, missing SKUs)
   for human review before load.

---

## Load Path Selection

| Path | When to use | Notes |
|------|-------------|-------|
| SFDMU data plan | Default for any multi-record catalog or pricing **data** load (including a handful of products) | See `.cursor/skills/sfdmu-data-plans/SKILL.md`. `Product2`, `ProductCategory`, `AttributeDefinition`, `PricebookEntry`, and related objects are SObjects, not Metadata API types. |
| Manual UI entry | Only when the user explicitly requests a one-off UI change | Document what was done for reproducibility. |
| Metadata API / Connect API | Pricing **procedures** and Expression Sets only | Route to `.cursor/skills/pricing-wiring/SKILL.md` and `.cursor/skills/expression-sets/SKILL.md`. |

---

## What This Skill Loads vs What to Hand Off

### Catalog and pricing DATA (stay here)

Author SFDMU plans for these objects. Use the named shipped plan as **inventory**
(which objects, which fields, which natural keys) — then apply the new-plan
rules in Shipped Plans vs New Plans.

**Structure — imitate `qb-pcm`:**

- `Product2`, `ProductCatalog`, `ProductCategory`, `ProductCategoryProduct`
- `ProductClassification`, `ProductClassificationAttr`
- `AttributeDefinition`, `AttributeCategory`, `AttributePicklist` / `AttributePicklistValue`, `ProductAttributeDefinition`
- `ProductSellingModel`, **`ProductSellingModelOption`**, `ProductRampSegment`, `ProrationPolicy`
- `ProductComponentGroup`, `ProductRelatedComponent`, `ProductRelationshipType`

A `Product2` row without a matching `ProductSellingModelOption` is not sellable.
PSMO lives in **qb-pcm**, not qb-pricing.

**Pricing data — imitate `qb-pricing` object set:**

- `Pricebook2`, `PricebookEntry`, `PricebookEntryDerivedPrice`
- `PriceAdjustmentSchedule`, `PriceAdjustmentTier`
- `AttributeBasedAdjRule`, `AttributeBasedAdjustment`, `AttributeAdjustmentCondition`
- `BundleBasedAdjustment`
- `CostBook`, `CostBookEntry`
- `CurrencyType`

`Product2` / `ProductSellingModel` / `AttributeDefinition` appear in qb-pricing
only as **`Readonly`** lookup parents (loaded earlier by qb-pcm). When a new
pricing plan targets products that already exist in the org, do the same:
`Readonly` + natural-key companion CSV.

### Behavior / metadata (hand off)

- Recipes, procedures, overlays, decision tables, recipe table mappings →
  `.cursor/skills/pricing-wiring/SKILL.md`
- Expression Set authoring, CRUD, activation lifecycle →
  `.cursor/skills/expression-sets/SKILL.md`

---

## Shipped Plans vs New Plans

`qb-pcm` and `qb-pricing` are the object/field reference. They are **not**
templates to clone operation-for-operation into a vendor load.

| Shipped shape (do not copy) | New plan (5.6.4+ floor) |
|-----------------------------|-------------------------|
| qb-pricing `PricebookEntry` (and several adjustment objects) use `Insert`; idempotency is a separate `delete_quantumbit_pricing_data` wipe | `Upsert` with a composite `externalId` covering the unique key. `Insert` reruns `DUPLICATE_VALUE`. Do not add `deleteOldData: true` without explicit user approval. |
| qb-pricing `PricebookEntry.csv` lookup columns `Pricebook2.$$Name$IsStandard` and `ProductSellingModel.$$Name$SellingModelType` | Simple lookup columns only (Bug 4): `Pricebook2.Name`, `ProductSellingModel.Name`. `$$` is valid on the **primary** matching column, not on lookup-reference columns. |
| qb-pricing `Product2.csv` is `Readonly` with a `StockKeepingUnit` column and **no `Id`** | Same pattern for companion CSVs. Never `SELECT Id` into the file. |

Full operation rules: `.cursor/skills/sfdmu-data-plans/SKILL.md`. Object-to-plan
map: `.cursor/skills/sfdmu-data-plans/object-plan-mapping.md`.

---

## Examples

### Example 1 — Load products from a vendor PDF

User request: "Here's the ACME 2026 price sheet PDF — load the products and
USD list pricing into the RLM catalog."

Do:

1. Capture source metadata (path, fetch date, currency = USD List).
2. Extract tabular rows to `tmp/catalog-loads/acme-2026/products.csv` with
   source-preserving columns. Flag low-confidence OCR rows for user review.
3. After confirmation, author **two** SFDMU plans under that directory (or two
   object sets): structure from qb-pcm inventory (`Product2` **and**
   `ProductSellingModelOption`), then pricing data from qb-pricing inventory
   (`PricebookEntry`). Existing org products/models/price books → `Readonly`
   companion CSVs (natural keys only).
4. Validate the temp plan: `python scripts/validate_sfdmu_v5_datasets.py --dataset tmp/catalog-loads/acme-2026`.
5. Load with `sf sfdmu run` (see Validation Checks). Confirm SOQL counts.
6. Hand off to `pricing-wiring` **only** if a procedure, recipe, or overlay
   must change — not for the PBE load itself.

### Example 2 — Seed a catalog from a description

User request: "Create a small catalog for a 3-tier SaaS product — Starter,
Pro, Enterprise — with monthly and annual pricing in USD."

Do:

1. Confirm SKU convention, price type(s), and whether options/attributes are in
   scope.
2. Generate `tmp/catalog-loads/saas-demo/catalog.yml` with categories,
   products, selling models, and per-tier price entries.
3. Review the YAML with the user, then generate SFDMU plans (structure +
   pricing data) from it. Include PSMO rows so each tier is sellable.
4. Validate with `--dataset`, load, then SOQL-count.

### Example 3 — Extend an existing catalog from a web page

User request: "Add these three new products from the vendor's public product
page to our existing RLM catalog."

Do:

1. Fetch the URL; record fetch date and confirm scraping is permitted.
2. Reuse existing Category and Attribute records — do not fork the taxonomy.
3. Match against existing SKUs first; only create new Products for genuinely
   new SKUs.
4. Load via SFDMU (even for three products). Companion `Readonly` CSVs for
   categories, selling models, and the standard price book already in the org.

---

## Validation Checks

Run these against **the temp plan you just wrote**, not the shipped datasets.
Every load ends with an **org-side** verification, not just the SFDMU summary.

```bash
# Local plan validation (before load) — pass the temp directory or the check
# walks datasets/sfdmu/ and never sees this plan.
python scripts/validate_sfdmu_v5_datasets.py --dataset tmp/catalog-loads/<slug>

# Load (SF CLI username or alias, not the CCI alias). --canmodify is the
# instance host (no https://), required for non-scratch orgs.
sf sfdmu run --sourceusername CSVFILE \
  --targetusername <sf-username-or-alias> \
  -p tmp/catalog-loads/<slug> \
  --canmodify <instance-host> \
  --noprompt --verbose

# Org-side verification (after load, for every object the plan touched)
sf data query -q "SELECT COUNT() FROM <Object> WHERE <load-filter>" --target-org <sf-alias>
```

Also review:

- **SOQL count on the target matches the CSV row count for every loaded
  object.** If any count is off, treat the load as failed regardless of what
  the SFDMU summary said.
- **`target/<Object>_insert_target.csv` is written on successful runs too.**
  Inspect it for `#N/A` or `Errors` **rows**. File presence or non-empty
  content is not a failure.
- Product count in target org matches the intermediate artifact.
- `ProductSellingModelOption` rows exist for every sellable product.
- Price Book Entries exist for every (Product, PriceType, Currency) tuple.
- No duplicate SKUs were introduced.
- Source metadata (path, fetch date, currency) is recorded in the load
  artifact directory.
- If the plan is promoted into `datasets/sfdmu/` for a PR: plan README +
  `python scripts/ai/check_plan_readme_consistency.py <plan_dir>` and
  `.cursor/skills/doc-consistency/SKILL.md`.

---

## Troubleshooting

**Symptom: SFDMU reports "Inserted N" but the target has 0 records.**
Open `target/<Object>_insert_target.csv`. If rows show `#N/A` in lookup FK
columns (`Product2Id`, `Pricebook2Id`, `ProductSellingModelId`, …) with errors
like `Required fields are missing: [Product2Id, ...]` or `To save this price
book entry, first specify a product.`, SFDMU could not bind the natural-key
lookup.

**Root cause: missing `Readonly` parent in the plan.** In `csvfile`-source
mode, child CSVs resolve lookups through **other objects declared in the same
`export.json`**. Those parent objects need a companion CSV of natural keys.
SFDMU then **queries the target org** (the `Readonly` operation) to bind Ids.
If `PricebookEntry.csv` references `Product2.StockKeepingUnit` but the plan
has no `Product2` object / `Product2.csv`, every lookup is `#N/A`. Dumping
`Id` values into the CSV is not the fix — that bakes the org into the plan.

**Fix (canonical):** add the parent as `Readonly` with the same `externalId`
the child lookup uses, and ship a natural-key CSV (no `Id` column). Match the
qb-pricing companion shape: `Product2.csv` is a `StockKeepingUnit` column
only.

```bash
# Keys only — never SELECT Id. Strip the CLI "Total number of records" footer
# before saving; headers must match export.json / the shipped companion CSV.
sf data query --result-format csv \
  -q "SELECT StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN ('SKU-1','SKU-2')" \
  --target-org <sf-alias>

sf data query --result-format csv \
  -q "SELECT Name, IsStandard FROM Pricebook2 WHERE IsStandard = true" \
  --target-org <sf-alias>

sf data query --result-format csv \
  -q "SELECT Name, PricingTerm, PricingTermUnit, SellingModelType, Status FROM ProductSellingModel WHERE Status = 'Active'" \
  --target-org <sf-alias>
```

Reshape each result to the companion CSV headers (add a `$$` **primary**
matching column when `externalId` is composite; do **not** add `$$` on lookup
reference columns). Declare each object in `export.json` as `Readonly` with
that `externalId` (`StockKeepingUnit`, `Name;IsStandard`,
`Name;SellingModelType`). Study `qb-pcm` / `qb-pricing` companion CSVs before
authoring a new plan.

**Anti-pattern (do not do this):** `sf data import bulk` / `sf data upsert bulk`
/ Composite REST with pre-resolved Ids, **or** `SELECT Id, ...` into the
companion CSV. Both produce an ID-baked artifact that cannot be re-run on
another org and violate Quick Rule 4.

**Symptom: `LineEnding is invalid on user data. Current LineEnding setting
is LF`.** That error comes from Bulk API 2.0, which means the load left SFDMU.
Go back to the SFDMU plan; do not set `lineterminator` as a workaround.

**Symptom: SFDMU `Insert` of a record whose object has a system-enforced
unique key (`PricebookEntry` on `(Pricebook2Id, Product2Id,
ProductSellingModelId, CurrencyIsoCode)`, `ProductSellingModelOption` on
`(Product2Id, ProductSellingModelId)`) fails on rerun with `DUPLICATE_VALUE`.**
Use `Upsert` with a composite `externalId` covering the unique key, not
`Insert`. qb-pricing's `Insert` on those objects is a pre-5.6.4 shipped
workaround (idempotency via `delete_quantumbit_pricing_data`); it does **not**
demonstrate the new-plan shape. See `.cursor/skills/sfdmu-data-plans/SKILL.md`.
