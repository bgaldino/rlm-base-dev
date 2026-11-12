# Catalogs, Categories, Family and Loading

> Sub-file of [`SKILL.md`](SKILL.md). Release 264. Read when organizing a model for
> browsing, coding it, choosing `Family` values, or turning it into an SFDMU plan. Plan
> mechanics are in [`../sfdmu-data-plans/SKILL.md`](../sfdmu-data-plans/SKILL.md). Source
> tags follow the parent skill's convention.

## Catalogs

A catalog is the top container; you need at least one. It can stand for a kind of product,
a service line, a sales territory or a business unit. [Help: `ind.product_catalog_plan_catalog.htm`; `ind.product_catalog_catalogs.htm`]
Products are placed in a catalog's **categories**, not in the catalog itself
(`ProductCategoryProduct` carries the category and catalog). [Help: `ind.product_catalog_assign_products_to_catalog_cat_and_subcategories.htm`; Repo: `scripts/ai/query_erd.py describe ProductCategoryProduct`]

| Choice | Trade-off | Downstream |
|---|---|---|
| One catalog | Simplest; one category tree | Every user browses the same tree |
| Catalogs by line or audience | Focused browsing | Each needs its own category tree; a product in two catalogs needs a row per category. Users switch catalogs, or you set a default. [Help: `ind.product_catalog_set_default_catalog.htm`] |
| Commercial vs technical catalog | Separates what buyers see from what fulfillment needs | Distinguished with product types and record types; the technical side is order orchestration (`dro-plans`). [Help: `ind.product_catalog_plan_catalog.htm`] |

## Categories

Categories nest (`ParentCategoryId`); a product can sit in several. Each category has a
name, a code, a sort order and *Show In Menu* (`IsNavigational`), which the Product
Discovery UI ignores but its APIs return. [Help: `ind.product_catalog_create_catalog_categories_and_subcategories.htm`]
Sort order at design time is the order Product Discovery shows. [Help: `ind.product_catalog_catalogs.htm`]

Categories organize browsing; **classifications** organize attributes. They are separate
trees and need not match. A category tree follows how buyers look for things; a
classification tree follows which products share attributes.
[Help: `ind.product_catalog_plan_catalog.htm`; `ind.product_catalog_product_classifications.htm`]

### Coding categories

Codes are what plans match on. The QuantumBit plan keys `ProductCategory` on `Code` alone
and resolves the parent through `ParentCategory.Code`. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/export.json`, `ProductCategory.csv`]

Measured on a 264 build: **a generated category code that collided across levels made a
category its own parent.** [Measured: 2026-11, 264] With `Code` as the key, a subcategory
that reuses its parent's code matches the parent's row, and `ParentCategory.Code` then
points at itself.

Rules:

- Make every category code unique across **all levels and all catalogs** the plan loads.
  Whether the platform enforces uniqueness per org or per catalog is **Open — needs live verification**;
  do not rely on either.
- Derive generated codes from the full path (`<catalog>-<parent>-<name>`), not the name.
  Name-as-code (`GPU`, `PCIe`) reads well but collides as soon as a subcategory shares a
  name with an ancestor.
- Keep code prefixes distinct between objects. QuantumBit uses `PC-` for both category and
  classification codes (`PC-QB-HW-CPU` is a category, `PC-QB-DB` a classification), which
  is legal (they are different objects) but easy to misread in a review. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProductCategory.csv`, `README.md`]
- Before a load: no row's `ParentCategory.Code` equals its own `Code`, and no code repeats.

## Product family is a contract

`Product2.Family` is a standard picklist. The 264 Help snapshot documents no pricing or
approval behaviour driven by it; it matters because **your own** automation filters on it.
[Repo: a search of `docs/salesforce/264/help/articles/` for `Family` finds no match; `scripts/ai/query_erd.py describe Product2`]
In this repo:

| Consumer | How it uses `Family` |
|---|---|
| Billing schedule UI | Lists active products with `Family = 'Software'` (`unpackaged/post_billing_ui/classes/RLM_BillingScheduleGroupService.cls`) |

Decision tables, approval conditions, flows, Apex and reports in an org can key on it the
same way, by literal value.

| Choice | Trade-off | Downstream |
|---|---|---|
| Family = a coarse product line (Hardware, Software, Services) | Few stable values | Safe to filter on; facets stay short |
| Family mirrors the category tree | Duplicates categories | Every category change becomes a Family change and breaks literal filters |
| Family left blank | No maintenance | Invisible to any family-based facet or rule |

Before renaming or retiring a value, find its consumers: `git grep -nw Family -- force-app unpackaged tasks datasets ':!*.csv' ':!**/staticresources/**'`
in the repo, and the org's decision table sources, approval criteria and flows. The
QuantumBit plan uses Hardware, Software, Services, Bundle, 3rd Party Software, a literal
`None` on five products, and blank on 166 of 314. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`]
A literal `None` is a value, not an absence: a filter for blank does not match it.

**Add new Family and unit values to their picklists as part of the load, or map the
source's values onto existing ones.** The `Family` picklist is unrestricted, so a load stores any value
through the API, but a value that is not one of the org's picklist values is not offered in
the UI's Family picklist. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]
`QuantityUnitOfMeasure` likewise stored units that are not among its picklist values (the UI
wasn't checked). [Measured: same org] A clean load is therefore no check on these values;
compare the plan's distinct `Family` and `QuantityUnitOfMeasure` values with the org's
picklist values before loading. Add a new Family value to the `Product2Family`
standard value set (a metadata deploy) in the same change as the plan that uses it. In this
repo that file is `force-app/main/default/standardValueSets/Product2Family.standardValueSet-meta.xml`;
it lists the values the QuantumBit plan uses; the q3 and mfg PCM plans load values it does
not list. [Repo: that file; `datasets/sfdmu/q3/en-US/q3-pcm/Product2.csv`; `datasets/sfdmu/mfg/en-US/mfg-pcm/Product2.csv`]

## From model to plan

1. **Copy the QuantumBit plan, then cut.** `datasets/sfdmu/qb/en-US/qb-pcm/` already has
   the dependency order: picklists → picklist values → unit of measure → attribute
   definitions → attribute categories → classifications → classification attributes →
   products → product attributes → selling models → proration policy → selling model
   options → ramp segments → relationship types → component groups → related components →
   overrides → catalogs → categories → category products → qualifications → attribute scope.
   Its README states each object's key. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/export.json`, `README.md`]
2. **Keep the keys.** Products on `StockKeepingUnit`; definitions, classifications, groups,
   categories and catalogs on `Code`. Use `;` composite keys and matching `$$` columns as
   `sfdmu-data-plans` describes; avoid Bug 4 shapes (a `$$` lookup whose parts are not
   exactly the parent's `externalId`, including a self-reference).
   [Repo: `sfdmu-data-plans/SKILL.md`]
3. **Mark empty objects `excluded: true`.** [Repo: `sfdmu-data-plans/SKILL.md`]
4. **Write a README** and run the plan checks (below).
5. **Load twice into a fresh org.** [Measured: 2026-11, 264]
6. **Run the `refresh_all_decision_tables` flow and the `rebuild_search_index` task** before
   placing a quote (fact f; the refresh is `decision-tables` Quick Rule 1).

```bash
# A new plan, through the generic loader (CCI alias, not sf alias). If the plan keeps
# ProrationPolicy, tolerate the platform-seeded duplicate as insert_quantumbit_pcm_data does;
# otherwise drop the ignore_row_errors_for option.
cci task run load_sfdmu_data -o pathtoexportjson datasets/sfdmu/<shape>/<locale>/<plan> -o ignore_row_errors_for "{ProrationPolicy: duplicate value found}" --org <cci_alias>
cci task run load_sfdmu_data -o pathtoexportjson datasets/sfdmu/<shape>/<locale>/<plan> -o ignore_row_errors_for "{ProrationPolicy: duplicate value found}" --org <cci_alias>   # second pass
cci flow run refresh_all_decision_tables --org <cci_alias>
cci task run rebuild_search_index --org <cci_alias>   # async: wait minutes, then retry Place until "Could not find product" stops
```

### PCM load facts (264)

| Fact | Consequence |
|---|---|
| **(a)** On the measured PCM plan (for the QuantumBit plan this is open; see [`SKILL.md`](SKILL.md#loading-the-model)), after the first SFDMU insert on a fresh org, classification attributes' `AttributeNameOverride` and `IsRequired` held the attribute definition's values rather than the plan's; a second, update pass applied the plan's values. [Measured: 2026-11, 264] Traced: an insert copies these from the attribute definition, an update does not. [Platform behaviour, traced] | Load twice. Never extract from an org that had one pass, or the definition's values become the plan. |
| **(b)** A `Readonly` anchor object that children reach through a `$$` composite lookup column needs a CSV with that `$$` column, or those lookups silently fail to resolve. [Measured: 2026-11, 264] This conflicts with `sfdmu-data-plans` → *Where a plan's CSVs live* (a `Readonly` object is source-free, its CSV optional); not reconciled, see [`SKILL.md`](SKILL.md#open-questions). | When a plan anchors on objects another plan loaded through `$$` lookups, keep the anchor's CSV with the `$$` columns its children reference. |
| **(c)** In a plan without `useSeparatedCSVFiles: true`, repeating an object across object sets: pass 2 re-reads the plan-root CSV of the same name. [Measured: 2026-11, 264] | For fact (a)'s second pass, run the plan again: that is the measured fix. |
| **(d)** A generated category code that collided across levels made a category its own parent. [Measured: 2026-11, 264] | See *Coding categories*. |
| **(e)** A configurator test of a bundle must place the quote with configuration rules on. [Measured: 2026-11, 264] | See `constraint-models`. |
| **(f)** Place Sales Transaction answered "Could not find product with ID …" for newly loaded products until `refresh_all_decision_tables` and `rebuild_search_index` had run and the index build had finished, minutes later. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] | After a load that adds products, run both, then retry Place until the error stops. The message is raised when the product lookup in the configurator step does not return the product; qualification procedures that read decision tables run there unless the recipe is the transaction recipe, so a stale table is plausible, not shown. No search-index dependence was found. [Platform behaviour, traced in part] The measured wait for both stays. `check_search_index_readiness` can't confirm this rebuild on an org that already had one: it reads Ready once any build has completed since the org was created (`tasks/rlm_rebuild_search_index.py`). |
| **(g)** A `Family` value outside the org's picklist is stored through the API but not offered in the UI. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] | Deploy the picklist value with the plan; see [Family](#product-family-is-a-contract). |
| **(h)** On `ProductRelatedComponent`, `ParentProductRole` and `ChildProductRole` are not writable, `MinQuantity` must be at least 1 when given, and `QuantityScaleMethod` rejects `None`. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] | See [`bundles-and-cardinality.md`](bundles-and-cardinality.md#two-kinds-of-cardinality) and [quantity scaling](bundles-and-cardinality.md#quantity-scaling-and-lifecycle). |

In this repo `prepare_product_data` runs `insert_quantumbit_pcm_data` once.
`test_qb_pcm_idempotency` loads the plan once, extracts the org, reloads the extraction and
fails if counts rise; its second load replays the one-pass org state, not the CSVs, so it is
not fact (a)'s second pass. [Repo: `cumulusci.yml`; `tasks/rlm_sfdmu.py` `TestSFDMUIdempotency`]

Other load constraints: `ProrationPolicy` is create-only and platform-seeded, so its insert
is rejected as a duplicate and tolerated (`ignore_row_errors_for`); several PCM lookups are
create-only, so a partial failure needs a delete before a reload; bundle depth beyond 3 needs
`MaxBundleDepth`. [Repo: `cumulusci.yml`; `sfdmu-data-plans/SKILL.md`; `datasets/sfdmu/qb/en-US/qb-pcm/README.md`]

### Check before and after

```bash
python scripts/validate_sfdmu_v5_datasets.py                             # expected result: AGENTS.md pre-merge checklist
python scripts/ai/check_sfdmu_layering.py                                # $$ lookup shapes (Bug 4)
python scripts/ai/check_plan_readme_consistency.py --strict <plan_dir>   # 0 errors, 0 warnings
python scripts/sfdmu_product_view.py capture --target-org <sf_alias> --shape <qb|q3> --sku <SKU> --out <file>   # what the configurator sees; --sku (repeatable) is required for a plan outside qb/q3-pcm, else it reads that shape's Product2.csv
```

After the load, re-run the Discovery queries in [`SKILL.md`](SKILL.md#discovery) and
compare against the CSVs, especially `ProductClassificationAttr.AttributeNameOverride` and
`IsRequired` (fact a) and `ProductCategory.ParentCategory.Code` (fact d).
