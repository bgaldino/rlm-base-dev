# Selling Models and Lifecycle Flags

> Sub-file of [`SKILL.md`](SKILL.md). Release 264. Read when choosing how a product is
> sold over time and which lifecycle flags it carries. Proration *setup* is in
> [`../pricing-setup/proration-and-selling-models.md`](../pricing-setup/proration-and-selling-models.md);
> this file covers the modeling choice. Source tags follow the parent skill's convention.

## Choose the selling model from the pricing basis

Selling models are optional in PCM; a product can have several. [Help: `ind.product_catalog_product_selling_model.htm`; Dev guide: `sforce_api_objects_productsellingmodel.htm`]

| The charge… | `SellingModelType` | `PricingTerm` / `PricingTermUnit` | Lifecycle consequence |
|---|---|---|---|
| happens once (hardware, a setup fee, a course) | `OneTime` | must be null | **Cannot be renewed**: renewing a bundle with one-time children sets them to No Change, quantity 0. [Help: `ind.qocal_asset_lifecycle_considerations.htm`] |
| recurs for a contracted term with an end date | `TermDefined` | required, e.g. 1 Annual | Has an end date to renew against; `DoesAutoRenewAssetByDefault` copies to quote/order lines and then to assets. [Help: `ind.product_catalog_create_a_product_selling_model.htm`; `ind.qocal_view_and_edit_orders.htm`] |
| recurs until cancelled | `Evergreen` | required, e.g. 1 Months | No end date; cancel ends it. [Help: `ind.product_catalog_product_selling_model.htm`] |

`SellingModelType` defaults to `OneTime` and `Status` to `Draft`; a model cannot return to
Draft once Active or Inactive. [Dev guide: `sforce_api_objects_productsellingmodel.htm`; Repo: `pricing-setup/proration-and-selling-models.md`]

**Pricing basis.** The Subscription price element multiplies unit price × quantity ×
pricing term count; the Proration element supplies the count. So a list price is *per
pricing term unit*: a Term Annual model with 1 Annual prices per year. [Repo: `pricing-setup/proration-and-selling-models.md`]
Pick the term unit you want to quote in, not the billing frequency.

**Trade-off of offering several models on one product:** each model needs its own price
book entry per price book and currency, and a PBE's selling model cannot be changed once
set. More models, more PBEs, and more rows to keep in step. [Repo: `pricing-setup/price-books.md`]

## Product selling model options

`ProductSellingModelOption` is the junction that says "this product can be sold on this
model". [Dev guide: `sforce_api_objects_productsellingmodeloption.htm`]

| Field | Use |
|---|---|
| `IsDefault` | At most one per product; optional |
| `ProrationPolicyId` | Term-defined and evergreen options only; with no policy a partial period is charged in full [Repo: `pricing-setup/proration-and-selling-models.md` → Troubleshooting] |
| `Minimum`, `Maximum`, `Increment` | Bounds and step for the subscription term, in pricing term units |

[Dev guide: `sforce_api_objects_productsellingmodeloption.htm`; Help: `ind.product_catalog_assign_a_product_selling_model_to_a_product.htm`]

`ProrationPolicyId` is create-only: an option first inserted without its policy keeps it
blank on reload. [Repo: `sfdmu-data-plans/SKILL.md` → *Reloading a Plan Into a Live Org*]

## Selling models inside bundles

`ProductRelatedComponent` carries `ParentSellingModelId` and `ChildSellingModelId`.
[Repo: `scripts/ai/query_erd.py describe ProductRelatedComponent`]

- **Configurable bundle:** do not set a component selling model. [Help: `ind.product_catalog_product_relationships.htm`]
- **New static bundle:** parent selling model None, and no component selling model. [Help: `ind.product_catalog_add_components_to_a_static_product_bundle.htm`]
  The shipped q3 plan's static bundle `CERT007` sets Term Annual as both parent and component
  selling model on its two children. [Repo: `datasets/sfdmu/q3/en-US/q3-pcm/ProductRelatedComponent.csv`]
  Whether Help's rule, written for a *new* static bundle, makes such rows invalid is **Open —
  needs live verification**; do not copy the pattern into a new model.
- **Bundle-based adjustments** need three selling models: the product's, its parent
  product's and its root bundle's. Help lists all three as prerequisites, and all three
  products must be in a price book. [Help: `ind.pricing_create_bundle_based_adjustments.htm`]
  See [Selling model of the bundle root](#selling-model-of-the-bundle-root).

Configurator validation of component selling models [Platform behaviour, traced in part]: for a Term Defined or Evergreen parent, each child must carry the **same** selling model and subscription term; a blank or different model, or a different term, draws a message. A parent model of None is treated as One Time: its children must then have no model or a One Time model, and term is not compared. In this step, a model on a line that is not one of that product's own options draws a message (a Term Defined line is also checked against the option's Minimum, Maximum and Increment). These are non-blocking messages on the configurator response. So a One Time (or no-model) root expects One Time (or no-model) children, and a term-based child under it draws a child selling-model mismatch message. [Platform behaviour, traced in part] The QuantumBit Starter bundle (One Time root, Term Annual child) would draw it if the step runs on its path; `CERT007` (Term Annual on both parent and children) matches the parent's model, so only a term difference could flag it. Neither the Starter bundle nor `CERT007` has been checked live (Starter message: live check pending). One measurement does not fit the rule: a Term Defined root with Term Defined, Evergreen and One Time children, placed with rules on and then configured, drew no message and no error-log row [Measured: 2026-11-12, 264, scratch]. Either the step does not run on the Place or configure path, or the Term Defined/Evergreen half of the rule does not fire as read; which one is not settled [inferred]. Whether the step runs on the Place path was not traced. Whether the message blocks save or Place is **Open — needs live verification** (the locked bundle measured in `bundles-and-cardinality.md` quoted a Term Defined root with One Time and Evergreen children).

Children keep their **own** options, which may differ from the root's. In the QuantumBit
Starter bundle the root is One-Time while a maintenance child is Term Annual.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProductSellingModelOption.csv`] How a mixed-model bundle
renews is **Open — needs live verification** beyond the one-time rule above and the one
measured shape ([below](#selling-model-of-the-bundle-root)); how it co-terminates is open for
every shape.

### Selling model of the bundle root

Before choosing the root's model, list each child the source names with how its charge
recurs (One Time, Term Defined or Evergreen), then check the source for these:

| If the source… | Then for the root |
|---|---|
| prices a child differently because it is sold inside this bundle | The root needs a selling model. Each Bundle Based Adjustment row carries `RootProductSellingModelId`, `ParentProductSellingModelId` and `ProductSellingModelId`, and the Bundle-Based Price element matches rows on the line's root and parent selling models. Help's worked example uses One Time for all three. [Help: `ind.pricing_create_bundle_based_adjustments.htm`; `ind.pricing_calculate_bundle_based_discounts.htm`; Repo: `scripts/ai/query_erd.py describe BundleBasedAdjustment`] |
| renews the bundle as a unit | A One Time root does not renew: renewing a bundle sets its one-time products to No Change, quantity 0. [Help: `ind.qocal_asset_lifecycle_considerations.htm`] A one-time root with an evergreen component renewed as a $0 quote with quantity 0 on every line ([`asset-lifecycle-changes` Quick Rule 5](../asset-lifecycle-changes/SKILL.md#quick-rules)); that skill models a renewable commitment as Term Defined. |
| ramps the bundle, or renews it early | Early renewal of ramped assets takes a term-defined bundle whose children are all term-defined: a ramped bundle renewed early cannot contain one-time or evergreen child assets. [Help: `ind.qocal_early_renewal_of_ramped_assets.htm`] Measured amend limits for mixed children are in [`../ramped-quotes/bundle-children-lifecycle.md`](../ramped-quotes/bundle-children-lifecycle.md#amend-and-cancel-limitation). |

One Time children renew as No Change, quantity 0, whatever the root's model. [Help: `ind.qocal_asset_lifecycle_considerations.htm`]
No snapshot article says how a Term Defined or Evergreen root renews its Evergreen
children. One shape is measured, a locked configurable bundle with a Term Defined root: its
Evergreen child came through at quantity 0 ([`bundles-and-cardinality.md`](bundles-and-cardinality.md#static-kit-or-locked-configurable-bundle-when-children-recur)).
An Evergreen root, and other bundle shapes: **Open — needs live verification**. Help's ramp-deal considerations list mixed root/child shapes
(a term-defined parent with one-time or evergreen children; "a one-time evergreen parent,
and a term-defined child"), but the snapshot drops the column that marks which are supported:
**Open — needs live verification.** [Help: `ind.qocal_considerations_ramp_deals.htm`] Whether
a bundle-based adjustment applies under a new static bundle, whose component rows Help
requires to carry parent selling model None, is **Open — needs live verification**.

## Ramps

`Product2.CanRamp` and `ProductRampSegment` model per-period price and volume. Only static or
configurable **simple** products can have ramp segments; the segment needs a term-defined
selling model on the product; one segment per segment type per product; Ramp Deals for
Lines must be on. [Help: `ind.product_catalog_product_ramp_segments.htm`] Ramped products
cannot be added to a quote or order on a contract flagged for cotermination. [Help: `ind.qocal_coterminate_contract_important_considerations.htm`]
Group ramps on quotes are the `ramped-quotes` skill.

## `IsAssetizable`

"Select Is Assetizable if the product instance must persist and become a customer asset
after the customer purchases it." Default `true`. **On a bundle root, the root's value
applies to every child**, whatever the child's own flag. [Help: `ind.product_catalog_create_bundled_products.htm`; `ind.product_catalog_create_simple_products.htm`]

| Set true when… | Set false when… |
|---|---|
| The customer will amend, renew, cancel, transfer or swap it later | It is consumed once and has no ongoing state (a one-off fee) |
| Usage grants hang off it (anchor and pack products create entitlement buckets after assetization) | Nothing downstream reads its asset |

On order activation the root's flag decides: a non-assetizable component under an assetizable root still becomes an asset and gets lifecycle actions like its siblings (bundle assembly not traced), and amend, renew and cancel set the flag true on the items they touch. [Platform behaviour, traced in part] The consequence for children that stay non-tracked is traced no further than this: to keep a component out of the asset base, make it a separate line, not a bundle child. A standalone non-assetizable product creates no asset.

Amend, renew and cancel act on assets. [Help: `ind.qocal_asset_lifecycle.htm`] So a product
that never becomes an asset has no asset to amend or renew (inferred; true of a standalone product, not of a child of an assetizable root). Usage buckets are
created after the pack is bought and assetized. [Help: `ind.qocal_understanding_rate_on_packs.htm`]
A technical (fulfillment) product marked assetizable, with a Custom decomposition scope, needs
an assetizable custom fulfillment scope configuration. [Help: `ind.dro_creating_a_technical_product.htm`]

**Trade-off:** `true` everywhere is the safe default for lifecycle, at the cost of asset
rows for things nobody amends. Because the root wins, a bundle that mixes one-off and
ongoing children cannot make only some children assetizable; split the one-off part out, or
accept assets for it. (The QuantumBit plan has 161 assetizable and 153 non-assetizable
products. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`])

## `IsSoldOnlyWithOtherProds`

Help: select *Sell only with other products* "if you can only sell this product when it's
combined with other products". [Help: `ind.product_catalog_create_simple_products.htm`] The
flag is exposed on product representations returned by the catalog APIs.
[Dev guide: `apex_class_runtime_industries_cpq_ProductDetailsRepresentation.htm`]

Help does not say what enforces it. Three write paths refuse, each on its own object: (1) assigning a category to a product whose flag is true (insert or update of the product-category link; a link with no category is not refused); (2) setting the flag from false to true on a product that already has a category assignment (a non-specific input error; true to false is never checked); (3) a Product Set with the flag true. [Platform behaviour, traced] No refusal was found when the flagged product is added as a bundle component, or in Place, quote-to-order or activation, where the flag is only read into product details (absence of hits in the modules searched; live check pending) [Platform behaviour, traced in part]. The flag is also returned to catalog API clients, which may filter on it. Treat it as a catalog-hygiene flag, not a reliable sales rule. Measured [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]:

| Step | Result |
|---|---|
| Assign it to a catalog category | **Refused**: `INVALID_OPERATION`, "This product can't be assigned to the category because the Sell only with other products checkbox is selected on the product." |
| Product Discovery search; the line editor's Quick Add search | Not found |
| Make it a bundle component | Accepted |
| Place it alone on a quote (rules on, `validateProductCatalog: true`), then order and activate | All accepted |

**Modeling advice:** set the flag, make the add-on a bundle component, and keep it out of
categories (the platform requires that). To make "only with X" real, require it through a bundle
component or add your own check (a configuration rule or a quote validation): the
refusals found are all on catalog writes (category assignment, switching the flag on for a product that already has a category, a Product Set); none was found at sale time.
Whether search hides it because of the flag or because it has no category (the flag is in the search index documents, so a filter is plausible; its logic is not traced), and what amend,
renew or cancel do when its companion is removed: **Open — needs live verification.** The
QuantumBit plan sets the flag on no product. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`]

## Other lifecycle fields on `Product2`

| Field | Decision | Owner skill |
|---|---|---|
| `UsageModelType` | Anchor (main subscription), Pack (add-on that grants usage), or a commitment type. Help lists one Commit value; the dev guide lists Monetary, Quantity and Token commitments, and `usage-consumption` names the API values. [Help: `ind.product_catalog_create_simple_products.htm`; Dev guide: `usage_management_fields_on_product2.htm`] | `usage-consumption` |
| `DecompositionScope`, `FulfillmentQtyCalcMethod` | How many fulfillment lines; Always One vs Aggregate. [Help: `ind.product_catalog_create_simple_products.htm`] | `dro-plans` |
| `AvailabilityDate`, `DiscontinuedDate`, `EndOfLifeDate` | Sale window and support window | see note below |

**Help disagrees with itself on the end dates.** The simple-product article says a product
cannot be sold after `DiscontinuedDate` and is unsupported after `EndOfLifeDate`; the
bundled-product article says the reverse. [Help: `ind.product_catalog_create_simple_products.htm`; `ind.product_catalog_create_bundled_products.htm`]
Which field the platform enforces for sale is **Open — needs live verification**.
