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
- **Bundle-based adjustments** need a selling model on the parent product and on the root
  bundle, and every product in a price book. [Help: `ind.pricing_create_bundle_based_adjustments.htm`]

Children keep their **own** options, which may differ from the root's. In the QuantumBit
Starter bundle the root is One-Time while a maintenance child is Term Annual.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProductSellingModelOption.csv`] How a mixed-model bundle
co-terminates and renews is **Open — needs live verification** beyond the one-time rule above.

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

Amend, renew and cancel act on assets. [Help: `ind.qocal_asset_lifecycle.htm`] So a product
that never becomes an asset has no asset to amend or renew (inferred). Usage buckets are
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

What enforces it is not documented: whether Product Discovery hides the product, whether a
cart holding it alone is rejected, and what amend, renew or cancel do when its companion is
removed are all **Open — needs live verification**. The QuantumBit plan sets it on no product.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`]

**Modeling advice until verified:** if an add-on must never be sold alone, make it a bundle
component (optionally a required one) rather than relying on this flag alone. Cardinality is
enforced by the configurator and checked by Validate Product Definition. [Help: `ind.product_catalog_bundled_product_validations.htm`]

## Other lifecycle fields on `Product2`

| Field | Decision | Owner skill |
|---|---|---|
| `UsageModelType` | Anchor (main subscription), Pack (add-on that grants usage), Commit (minimum committed use). [Help: `ind.product_catalog_create_simple_products.htm`] | `usage-consumption` |
| `DecompositionScope`, `FulfillmentQtyCalcMethod` | How many fulfillment lines; Always One vs Aggregate. [Help: `ind.product_catalog_create_simple_products.htm`] | `dro-plans` |
| `AvailabilityDate`, `DiscontinuedDate`, `EndOfLifeDate` | Sale window and support window | see note below |

**Help disagrees with itself on the end dates.** The simple-product article says a product
cannot be sold after `DiscontinuedDate` and is unsupported after `EndOfLifeDate`; the
bundled-product article says the reverse. [Help: `ind.product_catalog_create_simple_products.htm`; `ind.product_catalog_create_bundled_products.htm`]
Which field the platform enforces for sale is **Open — needs live verification**.
