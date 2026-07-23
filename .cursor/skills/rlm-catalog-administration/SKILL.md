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
2. Any time more than one record will be created or uploaded, only use SFDMU data plans for bulk load; see `.cursor/skills/sfdmu-data-plans/SKILL.md`.
3. For product and catalog loads, construct a temporary directory, imitating `./datasets/sfdmu/qb/en-US/qb-pcm`. Look at the file `./datasets/sfdmu/qb/en-US/qb-pcm/export.json` - base which objects need to have CSV files created and which fields need to be accomodated based on the contents of this export.json file.
4. SFDMU does not use hard-coded ID's - any files created for that purpose need to keep this in mind. 
4. Wire pricing changes through the layering model in `.cursor/skills/pricing-wiring/SKILL.md`. 
5. Validate on a clean org, then re-run for idempotency.
6.

## DO NOT

<!-- TODO(vance): explicit safety constraints. Candidates:
- DO NOT invent SKUs, prices, or attribute values that are not present in the source.
- DO NOT load directly against a shared org before dry-running on a scratch/PDE.
- DO NOT modify shipped procedures/decision tables to accommodate a catalog load.
- DO NOT skip the intermediate CSV/YAML review step, even for "small" catalogs.
- DO NOT hardcode record IDs, org URLs, or user references.
-->

- **DO NOT** _TBD_
- **DO NOT** _TBD_
- **DO NOT** _TBD_

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

Once Products and Price Book Entries are loaded, any change to **pricing
behavior** (recipes, procedures, overlays, decision tables) belongs to the
pricing-wiring workflow. Do not extend this skill with procedure-authoring
detail; instead, link out:

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

Run the applicable checks after every catalog load:

```bash
# TODO(vance): confirm exact commands for this repo.
python scripts/validate_sfdmu_v5_datasets.py
python scripts/ai/skill_manifest.py --check
```

Also review:

- Product count in target org matches the intermediate artifact.
- Price Book Entries exist for every (Product, PriceType, Currency) tuple.
- No duplicate SKUs were introduced.
- Source metadata (path, fetch date, currency) is recorded in the load
  artifact directory.
- Schema drift check: `.cursor/skills/schema-validation/SKILL.md`.
- Doc consistency before PR: `.cursor/skills/doc-consistency/SKILL.md`.
