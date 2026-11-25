# Selling Models and Lifecycle Flags

> Sub-file of [`SKILL.md`](SKILL.md). Release 264. Read when choosing how a product is
> sold over time and which lifecycle flags it carries, and for product images (`DisplayUrl`). Proration *setup* is in
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
  An insert of rows of that shape (static parent, both selling models set) was accepted when
  both products had their selling model options (inactive test bundle on an existing org;
  inactive and active test bundles on a fresh build), so Help's rule, written for a *new* static bundle, looks
  like guidance (see [Measured component rules](#measured-component-selling-model-rules));
  `CERT007`'s own rows were not the ones inserted. A test bundle with mismatched pairs priced
  and configured with no message (same section); whether `CERT007`'s matched Term Annual pairs
  price, order and renew correctly is **Open — needs live verification**; do not copy the
  pattern into a new model.
- **Bundle-based adjustments** need three selling models: the product's, its parent
  product's and its root bundle's. Help lists all three as prerequisites, and all three
  products must be in a price book. [Help: `ind.pricing_create_bundle_based_adjustments.htm`]
  See [Selling model of the bundle root](#selling-model-of-the-bundle-root).

Configurator validation of component selling models [Platform behaviour, traced in part]: for a Term Defined or Evergreen parent, each child must carry the **same** selling model and subscription term; a blank or different model, or a different term, draws a message. A parent model of None is treated as One Time: its children must then have no model or a One Time model, and term is not compared. In this step, a model on a line that is not one of that product's own options draws a message (a Term Defined line is also checked against the option's Minimum, Maximum and Increment). These are non-blocking messages on the configurator response. So a One Time (or no-model) root expects One Time (or no-model) children, and a term-based child under it draws a child selling-model mismatch message. [Platform behaviour, traced in part] The QuantumBit Starter bundle (One Time root, Term Annual child) would draw it if the step runs on its path; `CERT007` (Term Annual on both parent and children) matches the parent's model, so only a term difference could flag it. Neither the Starter bundle nor `CERT007` has been checked live (Starter message: live check pending). One measurement does not fit the rule: a Term Defined root with Term Defined, Evergreen and One Time children, placed with rules on and then configured, drew no message and no error-log row [Measured: 2026-11-12, 264, scratch]. Either the step does not run on the Place or configure path, or the Term Defined/Evergreen half of the rule does not fire as read; which one is not settled [inferred]. An Evergreen static bundle with One Time and Term Annual children drew no message either ([below](#measured-component-selling-model-rules)) [Measured: 2026-11-24, fresh 264 ent-sb0 scratch org], but a static bundle cannot be configured at run time, so the step may skip static bundles, a third explanation [Help: `ind.product_catalog_create_bundled_products.htm`] [inferred]. Whether the step runs on the Place path was not traced. Whether the message blocks save or Place is **Open — needs live verification** (the locked bundle measured in `bundles-and-cardinality.md` quoted a Term Defined root with One Time and Evergreen children).

Children keep their **own** options, which may differ from the root's. In the QuantumBit
Starter bundle the root is One-Time while a maintenance child is Term Annual.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProductSellingModelOption.csv`] How a mixed-model bundle
renews is **Open — needs live verification** beyond the one-time rule above and the one
measured shape ([below](#selling-model-of-the-bundle-root)); how it co-terminates is open for
every shape.

### Measured component selling-model rules

What an insert of a `ProductRelatedComponent` row did with `ParentSellingModelId` and
`ChildSellingModelId`, through the standard record API. Help only says not to select them
(above); this is what the platform enforced through API 68.0, with the Bundle to Bundle
Component Relationship type. First measured on an existing org (configurable parent a shipped
QuantumBit bundle; static parent a new, inactive test bundle)
[Measured: 2026-11-10, 264, existing org]. Repeated on a fresh build with new test products:
an inactive configurable bundle with one component group, an inactive static bundle and an
**active** static bundle (each child active when its parent was). Each row gave the same result
as on the existing org, on each parent of its type; the messages below are quoted from the
fresh build, every refusal with error `INVALID_INPUT`.
[Measured: 2026-11-24, fresh 264 ent-sb0 scratch org] The configurable-bundle refusal was also
seen on a scratch load ([`bundles-and-cardinality.md`](bundles-and-cardinality.md#quantity-scaling-and-lifecycle)).

| Parent product | Insert | Result |
|---|---|---|
| Configurable bundle (`ConfigureDuringSale` Allowed) | A parent selling model | Rejected: "The parent selling model is unsupported for configurable product bundles. Delete the parent selling model and try again." |
| Configurable bundle | A component selling model | Rejected: "The component selling model is unsupported for configurable product bundles. Delete the component selling model and try again." |
| Configurable bundle | Any row without a component group | Rejected: "Group is mandatory for configurable parent product." |
| Static bundle (`ConfigureDuringSale` Not Allowed) | `IsDefaultComponent` false (or omitted, fresh build) | Rejected: "Child component must be added by default for a Static Parent Product." |
| Static bundle | One selling model set, the other blank | Rejected: "The parent and child product selling models must both have values or both be empty." |
| Static bundle | Both set, a selling model option missing on either product | Rejected: "To create a Product Related Component, first add a product selling model option to the related product and product selling model." |
| Static bundle | Both set, each product has the option | Accepted. |
| Static bundle | Both blank | Accepted. |

- **No type-compatibility check on insert.** An Evergreen parent with a One Time, a Term
  Defined or an Evergreen child was accepted once each product had the selling model option. A
  row with both models blank was also accepted. Being accepted on insert does not show that a
  mismatched pair is valid.
- **A mismatched pair priced and configured with no reaction.** A separate active static
  bundle (Evergreen Monthly), built for this check rather than reused from the insert tests,
  with two rows, Evergreen parent with a One Time child and Evergreen parent
  with a Term Annual child (each child's only option), was placed on a test quote with only the
  bundle line (Place Sales Transaction, `configurationMethod: Force`, configuration rules on,
  `pricingPref: System`; the Evergreen root line needed a `BillingFrequency`). Place succeeded
  and added both children, each on the child selling model of its row (the Term Annual line got
  a one-year term and billing frequency Annual), each linked to the root by a
  `QuoteLineRelationship` with pricing `IncludedInBundlePrice`. The quote priced
  (`CompletedWithPricing`) with the root at its price book entry and each child at 0; both
  component rows, inserted without `DoesBundlePriceIncludeChild`, stored it as true (and
  `IsQuantityEditable` as false). A configurator `configure` call on the root line, rules and
  pricing on, returned `success: true`, `solverStatus: "success"`, no messages
  and a null `ValidationResult` on every line; no `RevenueTransactionErrorLog` row was written.
  Not compared against a matched-model bundle; ordering, billing and renewal of such a bundle
  were not tried. [Measured: 2026-11-24, fresh 264 ent-sb0 scratch org] This does not test the
  traced configurator rule [above](#selling-models-inside-bundles): a static bundle cannot be
  configured at run time [Help: `ind.product_catalog_create_bundled_products.htm`], so the step
  may skip static bundles [inferred].
- **Duplicates are allowed.** Several rows for one parent and child pair coexisted (four per
  static parent on the fresh build, each with a different model pair).
- **The bulk product view repeats a child once per row.** `/connect/pcm/products/bulk` for the
  parent listed the child once for each row, and each entry's `productRelatedComponent` carried
  `parentSellingModelId` and `childSellingModelId` (omitted when blank). Its
  `productSellingModelOptions` lists the product's own options, not the component's model. So a
  duplicate row shows up as a duplicate child in the view. Same on the fresh build (the
  inactive static parent's four rows gave four entries).

Do not add component selling models to a new model (see the DO NOT in SKILL.md). If an
existing plan already carries them, as `CERT007` does, load both selling model options before
the component row, and set both models or neither. Under a configurable
bundle, leave both blank and put the choice on the child's own options.

### Selling model of the bundle root

Before choosing the root's model, list each child the source names with how its charge
recurs (One Time, Term Defined or Evergreen), then check the source for these:

| If the source… | Then for the root |
|---|---|
| prices a child differently because it is sold inside this bundle | The root needs a selling model. Each Bundle Based Adjustment row carries `RootProductSellingModelId`, `ParentProductSellingModelId` and `ProductSellingModelId`, and the Bundle-Based Price element matches rows on the line's root and parent selling models. Help's worked example uses One Time for all three; a Term Defined Annual root, parent and child also priced the child [Measured: 2026-11-11, 264, scratch, one org]. [Help: `ind.pricing_create_bundle_based_adjustments.htm`; `ind.pricing_calculate_bundle_based_discounts.htm`; Repo: `scripts/ai/query_erd.py describe BundleBasedAdjustment`] |
| renews the bundle as a unit | A One Time root does not renew: renewing a bundle sets its one-time products to No Change, quantity 0. [Help: `ind.qocal_asset_lifecycle_considerations.htm`] A one-time root with an evergreen component renewed as a $0 quote with quantity 0 on every line ([`asset-lifecycle-changes` Quick Rule 5](../asset-lifecycle-changes/SKILL.md#quick-rules)); that skill models a renewable commitment as Term Defined. |
| ramps the bundle, or renews it early | Early renewal of ramped assets takes a term-defined bundle whose children are all term-defined: a ramped bundle renewed early cannot contain one-time or evergreen child assets. [Help: `ind.qocal_early_renewal_of_ramped_assets.htm`] Measured amend limits for mixed children are in [`../ramped-quotes/bundle-children-lifecycle.md`](../ramped-quotes/bundle-children-lifecycle.md#amend-and-cancel-limitation). |

One Time children renew as No Change, quantity 0, whatever the root's model. [Help: `ind.qocal_asset_lifecycle_considerations.htm`]
Early renewal of a usage-based asset needs a Term Defined selling model; it is not available for One Time or Evergreen. [Help: `ind.qocal_renew_usage_based_assets_early.htm`]
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
component or add your own check: a configuration rule, or a trigger (a validation rule can't; see below): the
refusals found are all on catalog writes (category assignment, switching the flag on for a product that already has a category, a Product Set); none was found at sale time.
A quote line validation rule can't tell a bundle child from a standalone line: `ParentQuoteLineItemId` can't be read in a formula, and a rule on insert saw the engine's own children without
it. The rule refused those children; limiting it to update let a standalone line through. An after-insert trigger on `QuoteLineItem` that looks
for the bundle's root line on the same quote refused a standalone line while Place still placed bundles; Place
returned `FIELD_CUSTOM_VALIDATION_EXCEPTION` with its message [Measured: 2026-11-16, 264, scratch]. The trigger checks the
quote, not the line, so a quote that already holds the root passes a standalone line, and removing the root afterward leaves the line standalone, since the trigger runs only when the line is inserted. [inferred]

Whether search hides the flagged product because of the flag or because it has no category (the flag is in the search index documents, so a filter is plausible; its logic is not traced), and what amend,
renew or cancel do when its companion is removed: **Open — needs live verification.** The
QuantumBit plan sets the flag on no product. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`]

## Other lifecycle fields on `Product2`

| Field | Decision | Owner skill |
|---|---|---|
| `UsageModelType` | Anchor (main subscription), Pack (add-on that grants usage), or a commitment type. Help lists one Commit value; the dev guide lists Monetary, Quantity and Token commitments, and `usage-consumption` names the API values. [Help: `ind.product_catalog_create_simple_products.htm`; Dev guide: `usage_management_fields_on_product2.htm`] | `usage-consumption` |
| `DecompositionScope`, `FulfillmentQtyCalcMethod` | How many fulfillment lines; Always One vs Aggregate. [Help: `ind.product_catalog_create_simple_products.htm`] | `dro-plans` |
| `AvailabilityDate`, `DiscontinuedDate`, `EndOfLifeDate` | No enforcement found (see note below) | see note below |

**Help describes the end dates in opposite ways.** The simple-product article ties
`DiscontinuedDate` to sale and `EndOfLifeDate` to support; the bundled-product article says
the reverse.
[Help: `ind.product_catalog_create_simple_products.htm`;
`ind.product_catalog_create_bundled_products.htm`]
Availability, discontinued and end-of-life dates are returned with product data and must be in
the order availability <= discontinued <= end of life, but no date was found that stops
browsing, adding to a quote, ordering, amending or renewing. Treat them as informational and
use `IsActive` or a rule if a product must be blocked [Platform behaviour, traced in part].
Not run live.

### Product images

`Product2.DisplayUrl` holds the image shown for a product, and Connect product responses return it
as `displayUrl`. [Dev guide: `connect_responses_recommended_products_output.htm`,
`connect_responses_guided_selection_output.htm`, `connect_responses_configurator_product_catalog_output.htm`]
In this repo:

- **QuantumBit uses static-resource paths.** The qb plan stores `/resource/<name>`,
  with the files shipped as static resources in two places: most in
  `unpackaged/post_quantumbit/staticresources/`, and six (`powersupply`, `liquidcooler`,
  `nvexpand`, `RAIDController`, `cacheboost`, `cpuheatsink`) in
  `force-app/main/default/staticresources/`. A product with no art of its own points at one
  shared logo, and most do. Every path names a resource that ships in one of the two places;
  point a product at an existing image rather than at a name that does not ship
  (`PROD-455868158` reuses `powerswerve`). [Repo:
  `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`; `unpackaged/post_quantumbit/staticresources/`;
  `force-app/main/default/staticresources/`] An org built with `qb` on before that fix
  keeps `/resource/omniserver`, which does not resolve, on `PROD-455868158`. Fix that one record:
  `sf data update record --sobject Product2 --where "StockKeepingUnit='PROD-455868158'" --values "DisplayUrl=/resource/powerswerve" --target-org <sf_alias>`
  [Measured: 2026-11-25, 264, existing org]. No follow-up step is needed: a `DisplayUrl` change
  made this way, with no search-index rebuild, showed at once on Browse Catalogs cards and in the
  configurator header (`PROD-455868158` on a qb org; `LLMCERT001` and `CERT007` on a q3 org)
  [Measured: 2026-11-24, fresh 264 ent-sb0 scratch org]. Reloading qb-pcm also works, but its Upsert resets
  every qb-pcm record to the plan's values, overwriting edits made on the org; after a reload, run
  [`catalogs-and-loading.md`](catalogs-and-loading.md) step 6 (the `refresh_all_decision_tables`
  flow, then `rebuild_search_index`).
- **Keep `DisplayUrl` in the product plan's own `Product2.csv`.** An image-only plan that ran
  after the product plan blanked the images whenever the product plan was reloaded alone; the
  URLs now live in the product CSV. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/README.md`]
- **Deploy the resource before the plan that points at it.** `prepare_rlm_org` deploys
  `force-app` (`deploy_full`, step 5) and the QuantumBit metadata (`prepare_quantumbit`, step 7)
  before the product plan (`prepare_product_data`, step 8), so the paths resolve when the first
  quote opens. Both flags default on, but the `post_quantumbit` resources (all but the six in
  `force-app`) deploy only when `quantumbit` is on, while the qb product plan loads when `qb` is on;
  a build with `qb` on and `quantumbit` off loads paths whose resources were never deployed. A new image is two changes in one PR: the resource,
  and the CSV row. [Repo: `cumulusci.yml`, `prepare_rlm_org` steps 5, 7 and 8]
- **Decide the fallback on purpose.** Choose a shared placeholder for products without art,
  or accept a blank; do not leave the choice to whichever rows were filled in.
- **The q3 plan uses one shipped placeholder for every product.** All 78 rows of
  `datasets/sfdmu/q3/en-US/q3-pcm/Product2.csv` point at `/resource/RLM_product_placeholder`, a
  neutral image in `force-app/main/default/staticresources/`, so q3 follows the rule above: one
  deliberate fallback, not a split by whichever rows happened to have an address. Half of them
  used to hotlink third-party hosts, which break without notice and which the repo has no license
  to use; do not reintroduce such addresses. The dev guide's example responses still show
  external `https` addresses. An org built with `quantumbit` on before that change (most qb
  builds too) keeps the 16 `img-src` trusted sites added for those hosts until they are removed
  in Setup → Trusted URLs; the list is in `datasets/sfdmu/q3/en-US/q3-pcm/README.md`. Remove
  them only after that org's q3 `DisplayUrl` values point at the placeholder: removed first, the
  q3 images that still use those hosts disappear without an error (the fallback below). An org
  where the q3-pcm plan was never loaded can delete the 16 sites at once.
- **An external `https` address loads only from an allowed host.** In Lightning, the page's
  `img-src` policy is the org's `img-src` CSP Trusted Sites plus Salesforce's built-in list
  (`*.ctfassets.net`, `*.cloudinary.com`, `*.salesforce.com`, `*.force.com` and others), with no
  `https:` wildcard; a host in neither is blocked by the browser. Method: the policy was read off
  a Lightning Product2 record page in Chrome, and each address was loaded in that page as a test
  image (`new Image()` with a `securitypolicyviolation` listener): `images.ctfassets.net` loaded
  with no trusted site, a `gstatic` host loaded through its trusted site (deployed by the build
  of that day; the repo no longer ships it, so a fresh build has none), and hosts in neither list
  were blocked. A record page does not render the product image itself; its Details tab
  shows `DisplayUrl` as text. [Measured: 2026-11-24, fresh 264 ent-sb0 scratch org] So ship
  images as static resources rather than adding a trusted site per host.
- **Catalog cards and the configurator header follow the same rule, and fail silently.** Browse
  Catalogs product cards and the configurator header render `DisplayUrl`; an allowed host
  (`images.ctfassets.net` with no trusted site) and a static resource (`/resource/powerswerve`,
  `/resource/RLM_product_placeholder`) both render. A host outside `img-src` shows no error: the
  card falls back to Salesforce's own `/img/industriesCpq/plp-image-placeholder.svg`, the image a
  blank `DisplayUrl` gets, and the configurator leaves the image block out. Seen on test quotes in
  Chrome. [Measured: 2026-11-24, fresh 264 ent-sb0 scratch org] So a bad or disallowed external `DisplayUrl` goes
  unnoticed in a demo until someone looks for the picture.

In the qb plan, all but one of the 314 products carry a `DisplayUrl`, in 53 distinct values,
and one logo covers 220 of them. [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`]
