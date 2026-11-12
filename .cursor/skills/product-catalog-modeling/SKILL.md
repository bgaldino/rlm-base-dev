---
name: product-catalog-modeling
description: >-
  Turn commercial offerings into a Revenue Cloud Product Catalog Management (PCM)
  model: product vs attribute vs component, static vs configurable bundles, component
  groups and cardinality, classifications and attribute overrides, selling models and
  options, IsSoldOnlyWithOtherProds and IsAssetizable, catalogs, categories and Family.
  Use when designing or reviewing a catalog before it is built or loaded, or when a
  modeling choice explains a pricing, configurator or asset-lifecycle symptom. Use
  sfdmu-data-plans to load the model and revenue-cloud-data-model for raw schema.
---

# Product Catalog Modeling — From Offer to PCM Model

Use this skill to decide **how** a set of things a business sells becomes PCM records:
which concepts are products, which are attributes, which are bundle components, how
they are grouped and counted, how they are sold over time, and how they are organized
for browsing. It is plain markdown, usable by any agent. It covers the modeling
decisions; loading the result is `sfdmu-data-plans`, the field-level schema is
`revenue-cloud-data-model`, and configuration rules are `constraint-models`.

Every product claim carries its source: `[Help: <article>]` (the 264 Help snapshot under
`docs/salesforce/264/help/articles/`), `[Dev guide: <article>]` (`docs/salesforce/264/dev-guide/articles/`),
`[Repo: <file>]`, or `[Measured: <date>, 264]` (a live 264 build; `[Measured: <date>, fresh 264 ent-sb0 scratch org]`
names the org: a newly built scratch org of the repo's `ent-sb0` shape). A claim only a live
org could settle is marked **Open — needs live verification**. Help article ids below
drop the `.md` suffix of the snapshot file name.

## Quick Rules

1. **Decide `Product2.Type` first: it cannot be changed after the record is created.**
   A wrong simple/bundle choice means a new product. Static ↔ configurable *can* be
   converted later. [Help: `ind.product_catalog_create_simple_products.htm`; `ind.product_catalog_conversion_of_bundle_products.htm`]
2. **A choice is an attribute unless something downstream needs it as its own record**:
   its own SKU, price book entry, selling model, asset, fulfillment line or category
   placement. Then it is a product (a component, or a variation product). See
   [Product vs attribute vs component](#product-vs-attribute-vs-component).
3. **Configurable bundle components live under groups, never directly under the root**,
   and groups nest at most two levels. Component cardinality counts *quantity*. Group
   cardinality counts *distinct* components in Help, but counted **lines** at run time, so
   keep each component on one line ([`bundles-and-cardinality.md`](bundles-and-cardinality.md#two-kinds-of-cardinality)).
   [Help: `ind.product_catalog_products.htm`; `ind.product_catalog_group_cardinality.htm`; Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]
4. **Attributes reach a product only through a product classification.** Put an attribute
   that drives a price on the classification the adjustment names, not on its parent, and
   never override it in a bundle context. [Help: `ind.product_catalog_product_classifications.htm`; `ind.pricing_attribute_based_pricing_limits.htm`]
5. **Pick the selling model from how the charge recurs** (once, for a fixed term, until
   cancelled), then give the product one `ProductSellingModelOption` per model it can be
   sold on, with at most one `IsDefault`. Price book entries and attribute-based adjustments
   carry a `ProductSellingModelId`. [Help: `ind.product_catalog_product_selling_model.htm`; Dev guide: `sforce_api_objects_productsellingmodeloption.htm`; Repo: `scripts/ai/query_erd.py describe PricebookEntry`, `describe AttributeBasedAdjustment`]
6. **`IsAssetizable` on a bundle root governs every child**; it decides whether the sale
   leaves an asset that amend, renew and cancel can act on. [Help: `ind.product_catalog_create_bundled_products.htm`; `ind.qocal_asset_lifecycle.htm`]
7. **Category codes must be unique across every level and every catalog a plan loads.** A plan keyed on
   `ProductCategory.Code` resolves a parent by code, so a child that reuses its parent's
   code becomes its own parent. [Measured: 2026-11, 264; Repo: `datasets/sfdmu/qb/en-US/qb-pcm/export.json`]
8. **Load a PCM plan twice into a fresh org, and never extract from an org that had only
   one pass**: on the measured plan, the first insert left classification attributes'
   `AttributeNameOverride` and `IsRequired` at platform defaults. [Measured: 2026-11, 264] See [Loading the model](#loading-the-model).

## DO NOT

- **DO NOT** model a simple product you may later need to bundle (or the reverse) on the
  assumption you can flip `Type`. You cannot. [Help: `ind.product_catalog_create_simple_products.htm`]
- **DO NOT** put a configurable product (simple or bundle) under a **static** bundle, or
  leave a static bundle's child without *Include component by default*. [Help: `ind.product_catalog_add_components_to_a_static_product_bundle.htm`]
- **DO NOT** set *Require this component* or *Include component by default* on a
  **product classification** component. [Help: `ind.product_catalog_local_cardinality.htm`]
- **DO NOT** set a component selling model on a configurable bundle's components, or,
  under a new static bundle, a parent selling model other than None or any component selling
  model. [Help: `ind.product_catalog_product_relationships.htm`; `ind.product_catalog_add_components_to_a_static_product_bundle.htm`]
- **DO NOT** override a price-impacting attribute in a bundle context. The attribute-based
  adjustment stops applying. [Help: `ind.pricing_attribute_based_pricing_limits.htm`]
- **DO NOT** rename a `Family` value or a category/classification code that is already in
  use without first searching for consumers that match it as a literal. See
  [Family](catalogs-and-loading.md#product-family-is-a-contract).
- **DO NOT** test a bundle in the configurator, or headlessly, with configuration rules
  off. Place the quote with rules **on**; a result with rules off says nothing about the
  model. [Measured: 2026-11, 264]
- **DO NOT** hardcode the QuantumBit names in this skill as the model to build. They are
  a labelled worked example; discover your own instances first.
- **DO NOT** cite or copy content from the private `.agents/artifacts/` tree, and do not name a real
  customer or brand in a model, example or commit.

## Entry Conditions

| Task | Use this skill? | Notes |
|---|---|---|
| Design a catalog for a new offering, vertical or demo shape | Yes | Start at [Discovery](#discovery), then the decision table. |
| Decide whether an option is an attribute, a component or a separate product | Yes | [Product vs attribute vs component](#product-vs-attribute-vs-component). |
| Set group/component cardinality, defaults, required components | Yes | [`bundles-and-cardinality.md`](bundles-and-cardinality.md). |
| Choose selling models, proration policy, `IsAssetizable`, `IsSoldOnlyWithOtherProds` | Yes | [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md); proration setup itself is `pricing-setup/proration-and-selling-models.md`. |
| Review a PCM plan's CSVs for modeling mistakes before a PR | Yes | Then `sfdmu-data-plans` for plan mechanics. |
| Write or fix `export.json`, externalIds, passes, `$$` columns | No | `sfdmu-data-plans`. This skill only names the PCM-specific load facts. |
| Look up a PCM field, relationship or SOQL shape | No | `revenue-cloud-data-model` (`scripts/ai/query_erd.py`). |
| Write CML rules, ports, `.ffxblob` | No | `constraint-models`. This skill covers what the catalog hands CML. |
| Configure pricing elements, adjustments, recipes | No | `pricing-procedures`, `pricing-setup`. |
| Fulfillment decomposition of a product | No | `dro-plans`. |

## Discovery

Find what exists before you model on top of it. Use `--target-org <sf_alias_or_username>`
(an `sf` alias, not a CCI alias; see `AGENTS.md`).

```bash
# Products by modeling shape: Type x ConfigureDuringSale, with lifecycle flags
sf data query --target-org <sf_alias> -q "SELECT Type, ConfigureDuringSale, IsAssetizable, IsSoldOnlyWithOtherProds, COUNT(Id) n FROM Product2 WHERE IsActive = true GROUP BY Type, ConfigureDuringSale, IsAssetizable, IsSoldOnlyWithOtherProds"
# Classification tree and the attributes each level carries
sf data query --target-org <sf_alias> -q "SELECT Code, Name, Status, ParentProductClassification.Code FROM ProductClassification ORDER BY Code"
sf data query --target-org <sf_alias> -q "SELECT ProductClassification.Code, AttributeDefinition.Code, AttributeNameOverride, IsRequired, IsPriceImpacting, DefaultValue FROM ProductClassificationAttr ORDER BY ProductClassification.Code"
# One bundle's groups and components (replace <SKU>)
sf data query --target-org <sf_alias> -q "SELECT Code, Name, MinBundleComponents, MaxBundleComponents, ParentGroup.Code FROM ProductComponentGroup WHERE ParentProduct.StockKeepingUnit = '<SKU>'"
sf data query --target-org <sf_alias> -q "SELECT ProductComponentGroup.Code, ChildProduct.StockKeepingUnit, ChildProductClassification.Code, IsComponentRequired, IsDefaultComponent, IsQuantityEditable, Quantity, MinQuantity, MaxQuantity, QuantityScaleMethod, DoesBundlePriceIncludeChild FROM ProductRelatedComponent WHERE ParentProduct.StockKeepingUnit = '<SKU>'"
# Selling models, and which ones each product can be sold on
sf data query --target-org <sf_alias> -q "SELECT Name, SellingModelType, PricingTerm, PricingTermUnit, Status FROM ProductSellingModel"
sf data query --target-org <sf_alias> -q "SELECT Product2.StockKeepingUnit, ProductSellingModel.Name, IsDefault, ProrationPolicy.Name FROM ProductSellingModelOption WHERE Product2.StockKeepingUnit = '<SKU>'"
# Catalogs, category tree, Family values in use
sf data query --target-org <sf_alias> -q "SELECT Catalog.Code, Code, Name, ParentCategory.Code FROM ProductCategory ORDER BY Catalog.Code, Code"
sf data query --target-org <sf_alias> -q "SELECT Family, COUNT(Id) n FROM Product2 GROUP BY Family"
```

What the repo ships, offline: the PCM plans `datasets/sfdmu/qb/en-US/qb-pcm/`,
`datasets/sfdmu/q3/en-US/q3-pcm/` and `datasets/sfdmu/mfg/en-US/mfg-pcm/`, each with a
README that lists its objects, keys and counts. `python scripts/ai/query_erd.py describe <Object>`
gives fields offline. `python scripts/sfdmu_product_view.py capture` reads what the
configurator sees for a built org (see `sfdmu-data-plans`); outside the qb and q3 PCM plans,
pass `--sku` for your products.

## The modeling decisions

Each row is a choice, its trade-off, and what it changes downstream. The sub-files carry
the detail and the sources.

| Choice | Pick A when… / B when… | Trade-off | Downstream effect |
|---|---|---|---|
| **Attribute vs product** | Attribute: a characteristic on one SKU, same price book entry. Product: needs its own SKU, price, selling model, asset or fulfillment line. | Attributes keep the catalog small; each product adds price book entries, options and category rows. | Attribute → no PBE of its own; priced through attribute-based adjustments (classification-bound) or a pricing element that reads attributes, such as a price adjustment matrix or a formula. Product → own PBE per selling model, own asset line. [Help: `ind.product_catalog_plan_catalog.htm`; `ind.pricing_attribute_based_pricing_limits.htm`; `ind.pricing_add_the_price_adjustment_matrix_element.htm`; `ind.pricing_formula_based_pricing.htm`] |
| **Simple vs bundle** (`Type`) | Bundle when the thing sold is a set of priced/fulfilled parts. | Irreversible. | Only bundles carry groups, components and bundle-based adjustments. [Help: `ind.product_catalog_create_simple_products.htm`; `ind.product_catalog_products.htm`; `ind.pricing_create_bundle_based_adjustments.htm`] |
| **Static vs configurable** (`ConfigureDuringSale`) | Static: a fixed kit. Configurable: the buyer picks parts, quantities or attributes. | Static needs a default for every attribute and fixes children and quantities; configurable needs groups and cardinality. Convertible both ways, but configurable → static also requires no classification components. | Configurable: buyers add or remove children, change quantities and attributes at run time, and CML bundle rules apply. Static: buyers change none of that at run time. [Help: `ind.product_catalog_create_bundled_products.htm`; `ind.product_catalog_change_a_configurable_bundle_product_to_a_static_bundle_product.htm`; Repo: `constraint-models/SKILL.md`] |
| **Component vs classification component** | One product per row vs "any product based on classification X". | Classification components grow with the catalog but cannot be required or default. | New products of that classification appear in the bundle without a PCM edit; CML sync does not pick up class membership changes. [Help: `ind.product_catalog_creation_of_a_bundled_product_structure.htm`; `ind.product_catalog_local_cardinality.htm`; `ind.product_configurator_sync_cml_and_pcm.htm`] |
| **Cardinality** (group min/max, component min/max/default, required, default) | See [`bundles-and-cardinality.md`](bundles-and-cardinality.md). | Tight cardinality blocks bad quotes but can make a bundle unconfigurable. | CML sync carries component cardinality and *required*; group changes do not sync. [Help: `ind.product_configurator_sync_cml_and_pcm.htm`] |
| **Where an attribute value is set** | Definition → classification attr → product attr → bundle override. | Lower levels are more specific but must be reviewed when a higher level changes. | Bundle overrides break attribute-based pricing. [Help: `ind.product_catalog_attribute_fields.htm`; `ind.pricing_attribute_based_pricing_limits.htm`] |
| **Selling model** | One Time / Term-Defined / Evergreen from the pricing basis. | Each extra model adds a PBE and an option per product. | Proration, renewal and the Subscription price element read it. [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md) |
| **`IsAssetizable`** | True when the sale must leave something to amend, renew or cancel. | False keeps the asset table clean for consumables. | Root value overrides children. [Help: `ind.product_catalog_create_bundled_products.htm`] |
| **`IsSoldOnlyWithOtherProds`** | True for add-ons that must not be sold alone. | The platform refuses to put it in a category, so offer it as a bundle component. | Search did not find it, but a quote placed by API with it alone was accepted, ordered and activated. [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#issoldonlywithotherprods) [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] |
| **Catalog / category placement** | Catalogs by audience or business unit; categories for browsing. | More catalogs means more category rows to keep coded uniquely. | Drives Product Discovery browsing; categories, not catalogs, hold products. [`catalogs-and-loading.md`](catalogs-and-loading.md) |
| **Family** | A coarse product line other systems filter on. | A free picklist value becomes a contract. | Whatever keys on it (search facets, Apex, rules) breaks on a rename. [`catalogs-and-loading.md`](catalogs-and-loading.md#product-family-is-a-contract) |

### Product vs attribute vs component

Ask, in order, and stop at the first yes:

1. **Is it fulfilled, assetized, renewed or invoiced separately?** → its own product. A
   bundle **component** if it is sold inside something; a standalone product if not.
2. **Does it have its own price that is not a function of the parent's attributes, or its
   own selling model?** → its own product (a component if bought inside a bundle). PBEs
   are keyed by product and selling model. [Repo: `pricing-setup/price-books.md`; `scripts/ai/query_erd.py describe PricebookEntry`]
3. **Does every combination need its own SKU for tracking, but buyers should pick from one
   screen?** → **variation products** under a variation parent (up to 5 attributes in a
   variation attribute set; the parent cannot be purchased; turning variants off after use
   can cause errors and data inconsistencies). [Help: `ind.product_catalog_create_product_variants_in_revenue_cloud.htm`; `ind.product_catalog_turn_on_product_variants.htm`]
4. **Otherwise** → an **attribute** on the product's classification. Size, colour,
   capacity, region of a single SKU. Attributes "reduce the number of individual products
   you need to build". [Help: `ind.product_catalog_plan_catalog.htm`]

Downstream checks for an attribute choice: if it changes price, it must
be active with `IsPriceImpacting` selected [Help: `ind.pricing_define_price_impacting_attributes.htm`],
belong directly to the classification the adjustment names, must not be a picklist over a
Boolean data type (use a Checkbox/Boolean attribute), and numeric values match in the `.0`
form. [Help: `ind.pricing_attribute_based_pricing_limits.htm`]
If a configuration rule must reason about it, CML needs it as an attribute variable; a
change to an attribute *under a product class* does not sync to CML. [Help: `ind.product_configurator_sync_cml_and_pcm.htm`]

## Loading the model

Loading is `sfdmu-data-plans`; derive a new plan from the QuantumBit one rather than from
scratch: copy `datasets/sfdmu/qb/en-US/qb-pcm/` (its `export.json` already orders
attributes → classifications → products → selling models → bundles → catalogs, and its
README documents each key), cut it to your objects, and keep its externalIds unless you
have a reason in that skill's terms. Load facts measured on 264 PCM builds (b and c are
general SFDMU behaviour, seen on a PCM plan):

| # | Fact | What to do |
|---|---|---|
| a | On the measured PCM plan (for the QuantumBit plan this is open; see below), after the **first** SFDMU insert on a fresh org, classification attributes' `AttributeNameOverride` and `IsRequired` held platform defaults; a second, update pass applied the plan's values. [Measured: 2026-11, 264] | Run the whole plan twice on a fresh org. Never re-extract an org that had one pass; the extract would bake the defaults into the CSVs. |
| b | A `Readonly` anchor object that children reach through a `$$` composite lookup column needs a CSV with that `$$` column, or those lookups silently fail to resolve. [Measured: 2026-11, 264] This conflicts with `sfdmu-data-plans` → *Where a plan's CSVs live*, which says a `Readonly` object never reads a source file and its CSV is optional; that skill's live-verified case is a single-field traversal. Not reconciled: see Open questions. | Keep a CSV with the same `$$` column the children's lookup columns name; shipped plans already do. |
| c | In a plan without `useSeparatedCSVFiles: true`, repeating an object across object sets does not give pass 2 its own data: pass 2 re-reads the plan-root CSV of the same name. [Measured: 2026-11, 264] Per-pass files need that flag and `objectset_source/object-set-N/` (`sfdmu-data-plans` → *Where a plan's CSVs live*). | For fact (a)'s second pass, run the plan again: that is the measured fix. |
| d | A generated category code that collided across levels made a category its own parent. [Measured: 2026-11, 264] | Generate codes from the full path, and check uniqueness across every level and catalog the plan loads. |
| e | A configurator test of a bundle must place the quote with configuration rules on. [Measured: 2026-11, 264] | See `constraint-models`. |

In this repo, `prepare_product_data` runs `insert_quantumbit_pcm_data` once. The
`test_qb_pcm_idempotency` task loads the plan once, extracts the org, and reloads the
extraction, so its second load replays the one-pass org state, not the CSVs: it is not
fact (a)'s second pass. [Repo: `cumulusci.yml`; `tasks/rlm_sfdmu.py` `TestSFDMUIdempotency`] Whether a
one-pass QuantumBit build leaves any classification attribute at a default that differs
from its CSV is **Open — needs live verification**: every `IsRequired` in the QB CSV is
`false`, the documented default, but all 36 rows set `AttributeNameOverride`, whose
first-insert value was not recorded. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProductClassificationAttr.csv`; Dev guide: `sforce_api_objects_productclassificationattr.htm`]

After a load of new products, run the `refresh_all_decision_tables` flow and the
`rebuild_search_index` task before placing a quote. That and two more load facts (a `Family`
value missing from the picklist, component fields an insert can't set or values it rejects) are facts (f)–(h) in
[`catalogs-and-loading.md`](catalogs-and-loading.md#pcm-load-facts-264).

Two more load constraints that shape the model, from the QB plan: bundle depth is capped by
the org value `MaxBundleDepth` (default 3, ceiling 5; the repo's scratch shapes set 5), and
several PCM lookups are create-only, so a partial failure needs a delete before a reload.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/README.md`; `orgs/README.md`; `sfdmu-data-plans/SKILL.md`]

## Sub-files

Read the one your decision needs:

- [`bundles-and-cardinality.md`](bundles-and-cardinality.md) — read when designing a
  bundle: static vs configurable rules (and a locked configurable bundle when a fixed kit's
  children recur), group nesting, group vs local cardinality,
  defaults and required components, quantity scaling, price-includes-child, validation.
- [`attributes-and-classifications.md`](attributes-and-classifications.md) — read when
  placing attributes: picklists, classifications and subclassifications, the four levels
  where a value can be set, and what pricing and CML need from them.
- [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md) — read when choosing
  selling models and options, component selling models, `IsAssetizable`,
  `IsSoldOnlyWithOtherProds`, ramps and their lifecycle effects.
- [`catalogs-and-loading.md`](catalogs-and-loading.md) — read when organizing catalogs and
  categories, coding them, using `Family`, or turning the model into a plan.

## Examples

### Worked example — QuantumBit Starter (illustration only; substitute your own)

The repo's fictional QuantumBit catalog models an entry offer as a **configurable bundle**
`QB-BDL-STND` (`Type=Bundle`, `ConfigureDuringSale=Allowed`, `Family=Bundle`,
`IsAssetizable=true`, One-Time default option) with two root groups, each **pick exactly
one** (`MinBundleComponents=1`, `MaxBundleComponents=1`) and each with one default child:

| Group | Children (default first) | Child selling model |
|---|---|---|
| Training | Essentials Training (default), Fundamentals Training | One-Time |
| Maintenance | Silver Hardware Maintenance (default), a second maintenance tier | Silver: Term Annual with the Default Proration Policy |

[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`, `ProductComponentGroup.csv`, `ProductRelatedComponent.csv`, `ProductSellingModelOption.csv`]

Why this shape: the training choice is a **component**, not an attribute, because each
course is priced and fulfilled on its own. "Exactly one" is a group rule, so it lives in
group cardinality; the pre-selected choice is `IsDefaultComponent` on one child, not
`IsComponentRequired` (which would forbid the alternative). The bundle root is
assetizable, so every child is assetizable whatever its own flag says. [Help: `ind.product_catalog_create_bundled_products.htm`]

### Routing examples

- "Should storage size be a product or an attribute?" → if each size has its own price
  book entry or SKU, a product or variation product; if price varies by size on one SKU,
  a price-impacting attribute on the classification. This skill.
- "My attribute-based discount stopped applying inside a bundle." → a bundle-context
  override on that attribute. This skill, then `pricing-procedures`.
- "Child lookups load blank in my new PCM plan." → facts (b)–(d) above, then
  `sfdmu-data-plans`.
- "Place says *Could not find product with ID* for a product I just loaded." → the decision-table
  refresh and search index rebuild after the load (fact f in [`catalogs-and-loading.md`](catalogs-and-loading.md#pcm-load-facts-264)).
- "A group I set to pick one says its number of child products is out of range, but I
  picked one product." → check whether the product is on two lines (a CML-sized default
  component splits); see
  [`bundles-and-cardinality.md`](bundles-and-cardinality.md#cml-sized-default-components).
- "The configurator lets me pick two from a pick-one group." → check the group holds
  products, not child groups: only the lowest-level group's cardinality is enforced at run
  time ([`bundles-and-cardinality.md`](bundles-and-cardinality.md#two-kinds-of-cardinality)).
  Then check rules were on (fact e) and that the cardinality reached CML: group changes do
  not sync. `constraint-models`.

## Validation Checks

Before committing a model (CSV changes) or a review of one:

```bash
python scripts/validate_sfdmu_v5_datasets.py               # expected result: AGENTS.md pre-merge checklist
python scripts/ai/check_sfdmu_layering.py                  # Bug 4 shapes in $$ lookups
python scripts/ai/check_plan_readme_consistency.py --strict <plan_dir>
```

Review the CSVs for these, each a rule above:

- Every `Type=Bundle` + `ConfigureDuringSale=Allowed` product has all components under a
  group, and no group mixes products with a classification.
- No static bundle has a configurable child, a child without *Include component by default*,
  or an editable quantity.
- No classification component is required or default.
- Every group's `MinBundleComponents` ≤ distinct children, and required children ≤ `MaxBundleComponents`.
- Every `Family` value is a value of the org's `Family` picklist, or the same change adds it
  to the `Product2Family` standard value set.
- No `ProductCategoryProduct` row names a product with `IsSoldOnlyWithOtherProds` true; the
  platform refuses that assignment.
- No `QuantityScaleMethod` is the literal `None`; the 264 picklist rejects it
  ([`bundles-and-cardinality.md`](bundles-and-cardinality.md#quantity-scaling-and-lifecycle)).
- Every product has at most one `IsDefault` selling model option; term-defined and
  evergreen options carry a proration policy where proration is wanted.
- Category codes are unique across all levels and catalogs; no row's `ParentCategory.Code` equals its own `Code`.
- Price-impacting attributes sit on the classification the adjustment names and are not overridden in a bundle.

After a load into an org: run the plan's second pass (fact a), then the `refresh_all_decision_tables` flow and
the `rebuild_search_index` task, run **Validate Product
Definition** on each changed bundle in PCM [Help: `ind.product_catalog_bundled_product_validations.htm`], and
configure one bundle in the configurator with rules on.

## Open questions

Every item marked **Open — needs live verification** in this skill and its sub-files:

- **`IsSoldOnlyWithOtherProds`.** Whether search hides it for the flag or for the missing
  category, and what amend, renew or cancel do when its companion is removed. See
  [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#issoldonlywithotherprods).
- **Is `ProductCategory.Code` unique per org or per catalog?** The snapshot does not say.
  Fact (d) only proves that a plan keyed on `Code` alone conflates levels. **Open — needs live verification.**
- **A non-assetizable child under an assetizable root.** Help says the root wins; whether
  a child flagged false then appears as an asset with lifecycle actions is **Open — needs live verification.**
- **Which end date stops a sale.** Help contradicts itself on `DiscontinuedDate` vs
  `EndOfLifeDate`. See [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#other-lifecycle-fields-on-product2).
- **How a mixed-model bundle co-terminates and renews.** Co-termination for any shape;
  renewal beyond the one-time rule and the one measured shape (a locked configurable bundle
  with a Term Defined root). See [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-model-of-the-bundle-root).
- **Which mixed root/child shapes ramp deals support.** Help's ramp-deal considerations
  list them, but the snapshot drops the supported marks. See
  [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-model-of-the-bundle-root).
- **Recurring children in a fixed kit.** Which selling model a static kit's Term Defined
  or Evergreen child is quoted, renewed and billed on; how a locked configurable bundle's
  children amend, and whether the lock holds on its renewal quote. See [`bundles-and-cardinality.md`](bundles-and-cardinality.md#static-kit-or-locked-configurable-bundle-when-children-recur).
- **Which `bundlevalidation` messages block an order.** A locked child's hand-edited
  quantity does; a CML-set locked quantity and a group out of range are not measured. See
  [`bundles-and-cardinality.md`](bundles-and-cardinality.md#static-kit-or-locked-configurable-bundle-when-children-recur).
- **Bundle-based adjustments under a new static bundle**, whose component rows carry
  parent selling model None. See
  [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-model-of-the-bundle-root).
- **One-pass QuantumBit build.** Whether any classification attribute is left at a default
  that differs from its CSV. See [Loading the model](#loading-the-model).
- **Selling models on an existing static bundle's components.** The q3 plan's `CERT007`
  sets them; Help forbids them under a *new* static bundle. See
  [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-models-inside-bundles).
- **A `Readonly` anchor behind a `$$` lookup.** Fact (b) says it needs a CSV;
  `sfdmu-data-plans` says a `Readonly` object is source-free and its CSV optional (its own
  optional-CSV example, `inapp/RecordType.csv`, is reached through a `$$` lookup). Settling it
  needs a load of a `$$` lookup against a CSV-less `Readonly` parent; until then, keep the CSV.
- **Other classification-attribute fields after one pass.** Whether fields beyond
  `AttributeNameOverride` and `IsRequired` behave like fact (a). See
  [`attributes-and-classifications.md`](attributes-and-classifications.md#loading-attributes).
