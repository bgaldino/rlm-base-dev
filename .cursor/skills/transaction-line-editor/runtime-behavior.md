# Line Editor Runtime Behaviour

> Sub-file of [`SKILL.md`](SKILL.md). Read it before rehearsing or debugging a demo in the line
> editor or the configurator. Source tags are defined in the parent. Items tagged `[Measured]` were
> observed on 264 demo orgs in early November 2026, or on a fresh 264 `ent-sb0` scratch org where the
> tag says so, and are not in the Help.

## 1. Adding products

[Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_view_and_edit_orders`, `ind.qocal_discover_and_configure_products`]

Three ways in: **Browse Catalogs**, the **Add Product** quick-add search, and **Add Assets** (existing
assets on an initial sale). The first add sets the price book; keep every product, children included,
on one price book. Added products are unsaved **transient lines** that can't be edited until the
quote or order is saved. Saving creates the lines and their attribute records.

Browse Catalogs flow: select a catalog > Next (skipped when a Default Catalog is set, below) > filter > set quantities > **Show buying options** for
products with selling models, **Configure** for configurable ones > **Add** or **Add Selection to
Quote** into the New Quote Line Items preview > **Add Items to Quote**. A configured product that is
saved is created even if it doesn't show in the preview. Derived-price products show list price 0 until
added. If the page has no line editor, save from the Browse Catalogs page. Using it needs Use Product
Discovery, Manage Revenue Management and Run Flows.

Child products appear in the editor only when **Quote Visibility** on the product-related component is
blank, Always or Transaction Line Editor (the dev guide's value label is *Transaction Line Editor Only*) [Help: `ind.qocal_view_and_edit_quotes`; Dev guide:
`product_catalog_management_fields_on_product_related_component`].

Measured traps:

- **Where Browse Catalogs opens depends on the Default Catalog.** With a Default Catalog in Product
  Discovery Settings it skips the catalog picker and opens straight into that catalog. The build sets
  it to QuantumBit Software when `qb` is on (`configure_product_discovery_settings`, in
  `prepare_pricing_discovery`) [Repo: `cumulusci.yml`, `robot/rlm-base/resources/E2ECommon.robot`
  `Select Catalog By Name`]. On one measured org, Browse Catalogs opened on a catalog that showed
  "No products to show" until the rep switched catalog [Measured: early Nov 2026, 264]; the org's
  Default Catalog setting wasn't recorded. Before a demo, check which catalog it opens on.
- **A top-level category whose products sit only in subcategories shows no products** until a
  subcategory is picked [Measured: early Nov 2026, 264].
- On a group ramp, Browse Catalogs from a segment row asked for the **catalog first**, then **Select
  Segments to Add Products** [Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org]; an earlier fresh
  build (2026-10-29) recorded the segment prompt first, and the cause of the difference isn't
  established. Check which prompt comes first before a demo. Ramp steps: `ramped-quotes/ui-group-ramp.md`
  [Repo: `.cursor/skills/ramped-quotes/ui-group-ramp.md`].

## 2. Editing lines

[Help: `ind.qocal_view_and_edit_quotes`]

- Click a cell, edit, save. **Bulk edit:** select several lines, edit the cell on one, save; the value
  goes to all selected lines. The STLE bulk-edits groups too; its bulk actions include editing fields,
  updating discounts and deleting selected lines or groups [Help: `ind.qocal_view_and_edit_orders`,
  `ind.qocal_customize_transaction_line_editor`]. Those articles and `ind.qocal_limits` give no cap on
  the selection, and they don't say whether bundle child lines can be selected.
  **Measured in the STLE: bundle children can be selected and bulk edited.** Each child row has its
  own checkbox; with four children of one bundle ticked (root unticked), an Adjustment Type edit on one
  of them went to all four, with no "apply to selected" prompt, and Save stored it on each child (repo
  quote page, Instant Pricing on; off wasn't measured) [Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org]. Move Selected Items on child lines, and the
  legacy TLE, weren't measured. For automation: a pointer click on the checkbox ticked it; a click on
  the element reference didn't.
  **Bulk Delete** can't be used on a quote or order with a group ramp schedule
  [Help: `ind.qocal_ramp_deal_for_groups_manage`].
- Unsaved edits are lost on page reload or session expiry.
- Decimal quantities only for products with a unit of measure; the grid shows two decimals and stores
  the unit of measure's scale.
- The **Adjustment Type** cell editor is a value box plus a type picklist; on the repo's quote page it
  offers **Discount (Percentage)** and **Discount (Amount)**, the two fields the page selects for that
  column [Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org; Repo:
  `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml` `adjustmentTypeFields`].
- If the editor won't switch a line between Discount (Percentage) and Discount (Amount), clear the value
  on the line record, then enter the new type in the editor.
- Hover **Net Unit Price** for the price waterfall (bundle, tier, attribute, derived and contract
  adjustments); hover **Total Price** for bundle parent price, sum of lines and bundle subtotal.
- **Freeze up to this Column** pins columns; the filter row searches columns. Column filtering covers
  parent lines only: with bundles on the quote, "the editor excludes child items from the filter
  results" [Help: `ind.qocal_view_and_edit_quotes`]; the order article says the same
  [Help: `ind.qocal_view_and_edit_orders`].
- **STLE filters:** predefined All Lines, Errored Lines, Ramped Lines, Unconfigured Lines; advanced
  filters take up to 5 conditions with AND/OR, scoped to all or selected groups. The most recently
  applied of a column filter and a predefined or advanced filter wins
  [Help: `ind.qocal_filter_line_items_with_standard_and_advanced_filters`].
- **Variation products:** quick add lists variations, not their parents. Row action **Change** replaces
  the line with a new one and drops its discounts and adjustments [Help: `ind.qocal_product_variation_use_in_transaction_management`].

## 3. Line groups

[Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_view_and_edit_orders`]

- Needs **Enable Groups** in Revenue Settings (on in this repo). Once a transaction is grouped, every
  line must be in a group.
- **Add Group** the first time moves all existing lines into one group; click again for more. Name
  each group. **Move Selected Items** reassigns lines or groups; **load more** reveals more groups.
- Up to five levels of nested groups and lines in one table, with subtotals per level.
- **Group By** on a groupable column groups automatically (Help's example is Location), in the
  **TLE only**; not in the STLE, and not on formula fields. Help doesn't list which columns are
  groupable or say how Group By places bundle child lines.
- Sort Order on the Quote Line Groups related list sets group order; blank ones go last, by creation date.
- **Ungroup** returns to a flat list. Groups carry over from quote to order.
- Lines created through the Place Sales Transaction API should carry a group ID when the STLE will be
  used on that quote afterwards [Dev guide: `connect_resources_place_sales_transaction`].
- Group ramps (Create Ramp Schedule, segments, uplift) are covered in
  [`ramped-quotes`](../ramped-quotes/SKILL.md); the legacy TLE doesn't support them.

### One discount on one product line inside a bundle

A rep may want one discount on every line of one product line, for example all the components of
one family inside a suite bundle. None of the line editor articles cited here describes a feature
for this. Help rules out the column filter route; selecting the lines by hand is measured to work in the
STLE, and the others are unconfirmed:

- **Column filter, then bulk edit:** the column filter returns parent lines only and leaves bundle
  children out [Help: `ind.qocal_view_and_edit_quotes`], so it can't narrow the grid to one product
  line inside a bundle.
- **STLE advanced filter, then bulk edit:** advanced filters take up to 5 conditions on line fields or
  fields one relationship away [Help: `ind.qocal_filter_line_items_with_standard_and_advanced_filters`];
  that article doesn't say whether bundle child lines are included.
- **Group By that column, then discount the group:** automatic grouping is TLE only
  [Help: `ind.qocal_view_and_edit_quotes`], and the STLE is the editor Help recommends
  [Help: `ind.qocal_customize_transaction_line_editor`]. A group row takes an Adjustment Type field
  only when that field is in Display Columns and selected for the Adjustment Type column
  [Help: `ind.qocal_adjustment_type_column`]; the repo's quote page selects only
  `QuoteLineItem.DiscountAmount` and `QuoteLineItem.Discount` there, and none of its display columns is
  a group discount field [Repo: `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml`]. The group-ramp articles
  show a rep entering a discount on a group [Help: `ind.qocal_basic_example_ramp_deals_for_groups`,
  `ind.qocal_ramp_deals_for_groups_transition`, `ind.qocal_ramp_schedule_with_trial_and_proration_segments`],
  and the STLE overview lists updating discounts among its bulk actions on lines or groups
  [Help: `ind.qocal_customize_transaction_line_editor`].
  On the pricing side, the Propagation element applies discounts from groups to line items
  [Help: `ind.pricing_essentials`]; this repo ships it off (`IsPropagationEnabled` false) in the
  procedures that carry it [Repo: `.cursor/skills/pricing-procedures/elements/price-propagation.md`].
- **Select the lines by hand and bulk edit (works in the STLE):** tick that product line's child rows,
  edit the Adjustment Type cell on one of them (for example Discount (Percentage) 10), Save. The value
  went to every selected child and priced each one; the other children and the root were untouched,
  and no error log was written. The result matched the same discount set on those lines through the
  Place API [Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org]. With many children the rep ticks
  each one by hand.

Whether Move Selected Items, Group By or the STLE filters reach bundle child lines, whether a
group-row discount reaches bundle child lines in that group, and whether a bundle's children can sit
in a different group from their root are open (see the parent's Open list). So the measured route is
select-by-hand; don't promise a filter- or group-based one-step discount in a demo until one is
measured. Whether a hand-applied discount survives a clone and reprice wasn't measured.
A discount that must apply on every quote, not by a rep's hand, is a pricing question; see
[`pricing-procedures`](../pricing-procedures/SKILL.md).

## 4. Pricing actions

| Action | What it does | Source |
|--------|--------------|--------|
| **Save** | Prices inline edits | [Help: `ind.qocal_view_and_edit_quotes`] |
| **Instant Pricing** | Reprices each price-impacting change at once; turns off on page reload or session expiry. *Instant Pricing Active by Default* (STLE only) turns it on by default | [Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_turn_on_quote_and_order_capture`] |
| **Reprice All** | Full repricing of every line, even with no changes and even where Delta Pricing is on; sends Force pricing with configuration skipped (traced request shape) [Platform behaviour, traced] | [Help: `ind.qocal_reprice_all_quotes_and_orders`] |
| **Refresh Prices** | Pricing, configuration and taxes | [Help: `ind.qocal_view_and_edit_quotes`] |
| **Estimate Taxes** | Tax estimate; needs the Revenue Setting *Add Estimated Taxes to Quotes and Orders* | [Help: `ind.qocal_reprice_all_quotes_and_orders`, `ind.qocal_turn_on_quote_and_order_capture`] |

Use Reprice All when pricing was skipped at commit, validation errors stopped a run, discounts or
adjustments need a refresh, or usage resource grants on a quote line were deleted (it rebuilds them)
[Help: `ind.qocal_reprice_all_quotes_and_orders`]. The same article also lists bundle configurations
needing a refresh, though it says Reprice All skips configuration; for configuration use Refresh
Prices (and see the parent's Open list). Any update to an order or its products outside the
line editor, including Description, sets the validation result to Transaction Incomplete, and the order
must be repriced before activation; the same applies to quote lines
[Help: `ind.qocal_limitations_for_using_quote_and_order_capture`].

Measured: **Reprice All on a quote whose lines are already priced changed nothing** and showed "The prices
were refreshed and the configuration was validated." [Measured: early Nov 2026, 264]. The message's
mention of configuration is unexplained: Reprice All sends Force pricing with configuration skipped (traced
request shape) [Platform behaviour, traced], but where the toast text comes from was not traced, so whether
configuration is validated beyond that request shape is not established.

Measured: **a header-only Place PATCH doesn't reprice the lines.** A Place PATCH that changed only a quote
header field, one the pricing procedure reads through the sales transaction context, saved the field
and left every line's price as it was; a header-only PATCH with no field change didn't reprice either
(each line's `PriceWaterfallIdentifier` stayed the same). **Reprice All** applied the new header value to the lines
[Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org]. The rule behind it: under System pricing a Place
request is priced only when it includes at least one quote or order line record, or line attribute record
(a create, update or unchanged-value PATCH counts; a request that only deletes lines is priced only if the transaction still has lines). A request with only the header record
is not priced, whichever header field changed. Force pricing (Reprice All) passes the request test
unconditionally [Platform behaviour, traced]. A request that carries a context id is priced whenever the transaction has
lines, so a header-only change through that path would reprice; which path a given client request takes
was not determined, and the context-id case was not measured. After changing a header field that pricing
reads, include a line record in the same request, use Force pricing, or click Reprice All. Pricing can also be
skipped by an org-level platform setting that has no documented name [Platform behaviour, traced].
A line PATCH on the graph-style Place path reprices the transaction, but on a Compound group ramp a partial line edit can re-apply the
uplift to lines you didn't touch. Delta pricing (on in every Foundations-built org
[Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`]) is defined once in
[pricing-procedures](../pricing-procedures/runtime-and-observability.md#delta-pricing);
when it doesn't apply, every line reprices, and a non-idempotent uplift step re-applies.
Help adds that a Compound Uplift Price Revision step reprices every line in the ramp group on each
run regardless of delta pricing [Help:
`ind.pricing_use_the_price_revision_element_in_a_pricing_procedure`]; that fits the re-uplift of
untouched ramp lines [inferred]. Which relations count as a dependency isn't traced.
Delta Pricing was probably on in the 2026-11-11 measurement but wasn't read there; on a second org with it read on, a
System PATCH of one ramp line with no field change (configuration Skip) left every line's waterfall id unchanged, yet re-applied the compound uplift to every uplifted line's `NetUnitPrice`, unrounded, with totals unchanged [Measured: 2026-11-12, 264, scratch; one org]. Help's rule fits which lines moved, but not the unchanged waterfalls or the uplift compounding on the stored net; that path is not traced (`ramped-quotes` SKILL.md → DO NOT). A header edit in the record UI wasn't measured. For quotes,
Help's Reprice All requirement names updates to Quote Line Items outside the line editors, not the
Quote header (for orders it covers Order records too)
[Help: `ind.qocal_limitations_for_using_quote_and_order_capture`].

## 5. Header adjustments

[Help: `ind.qocal_header_adjustments_use`, `ind.qocal_header_adjustments_overview`]

**Manage Header Adjustment** > type (**Amount**, **Percentage**, **Amount Override**) > value >
distribution (**Equal**, or **Proportionate** to each line's list price × quantity). Where Delta Pricing is on
(Help: `ind.qocal_use_delta_pricing_for_quotes_and_orders`; every repo build enables it, and it
applies only when all its conditions hold, see [runtime and
observability](../pricing-procedures/runtime-and-observability.md#delta-pricing)),
click **Reprice All** afterwards. The waterfall shows each line's share. Users need
Salesforce Pricing Run Time User.

**The setup is in the pricing procedure, not the editor.** Manage Header Adjustment takes the type,
value and distribution logic [Help: `ind.qocal_header_adjustments_use`], and Help's setup uses the
Discount Distribution Service (DDS) element in the pricing procedure to support it
[Help: `ind.qocal_header_adjustments_overview`]. So the setup is:

- **Header Adjustments** on in Revenue Settings.
- A pricing procedure with a DDS element, fed by list groups that read the header discount type
  (Amount, Percentage, Override) [Help: `ind.qocal_header_adjustments_overview`]. Help disagrees on
  what may follow DDS: the limits article says it must be the last element
  [Help: `ind.pricing_discount_distribution_service_limits`], the element article allows only Rounding
  Values and Aggregate Price after it [Help: `ind.pricing_use_the_discount_spread_service_element`];
  the repo's default procedure follows it with aggregates. DDS can be used once per procedure
  [Help: `ind.pricing_discount_distribution_service_limits`], and it can't share a procedure with Derived Price. When derived pricing is needed, put DDS in its own
  procedure and run both through a procedure plan with Procedure Plan Orchestration for Pricing on
  [Help: `ind.qocal_header_adjustments_overview`]. Element detail:
  `pricing-procedures/elements/discount-distribution-service.md`.

In this repo, `RLM_DefaultPricingProcedure` has the header-discount list groups (seq 36–38) and a DDS
step (seq 39), followed by the aggregates. That is the Revenue Settings procedure, so header adjustments
work with the procedure plan inactive. `RLM_Price_Distribution_Procedure` (`unpackaged/post_procedureplans`)
has a second DDS, and the plan's Header Distribution section runs it after the default procedure
[Repo: `.cursor/skills/pricing-procedures/elements/discount-distribution-service.md`,
`datasets/sfdmu/procedure-plans/README.md`].

Measured: **a 10% header discount was applied twice (19% total)** with an active pricing procedure plan
and `skipOrgSttPricing` on; line discounts on the same quote were exact [Measured: early Nov 2026, 264].
Both DDS steps ran, the default procedure's and then the plan's distribution procedure's. The repo's own
measurement agrees: 10% on 5,240 gave 4,244.40, not 4,716 [Repo: `datasets/sfdmu/procedure-plans/README.md`].
The repo builds the plan inactive and `skipOrgSttPricing` false, so a default build runs one DDS.
If the plan must be active, follow `pricing-procedures/operations-and-troubleshooting.md` section 3:
with `skipOrgSttPricing` off the Revenue Settings default procedure re-runs after the plan (a price
revision doubles) [Repo: `datasets/sfdmu/procedure-plans/README.md`], so the fix is not only a
question of where DDS sits.

## 6. Configuring a bundle from a line

[Help: `ind.product_configurator_configure_bundled_products`, `ind.product_configurator_get_latest_pricing`]

- On the quote's line tab or the order's Lines tab, open the line's quick action menu > **Configure**.
- The record's **Transaction Type** selects which rules engine runs configuration rules.
- In the configurator: Compact Mode, **Load Configuration** for a saved one, add products to a component
  group, **Clone** an option card (needs the flow's Display Clone Option attribute; quantity isn't
  cloned). **Instant Pricing** in the configurator updates the summary on each change; otherwise click
  **Update Price**. **Save and Exit** returns to the editor.
- The configurator keeps no state: deselect then reselect a child and it comes back as a new line with
  defaults.
- Help notes that amending and cancelling a child product doesn't update the line quantity.

Measured:

- **A line placed by API with configuration rules off can open in the configurator with a different
  configuration than the one saved.** Lines placed with rules on opened correctly
  [Measured: early Nov 2026, 264]. Place demo lines with rules on, or check each one in the configurator
  before the demo. Rule behaviour itself is in [`constraint-models`](../constraint-models/SKILL.md).

## 7. Amendment, renewal and cancellation lines

What Help says:

- Amendment and renewal quotes and orders copy asset attribute values to the line attributes
  [Help: `ind.qocal_amend_assets`, `ind.qocal_renew_assets`]; the cancellation article doesn't say.
- A negative delta quantity on an amendment or cancellation is priced from prior sale prices, last in,
  first out [Help: `ind.qocal_amend_assets`, `ind.qocal_cancel_assets`].
- With derived pricing on amendments, the derived product's Net Unit Price isn't shown; the line total
  is accurate [Help: `ind.qocal_amend_assets`].
- A price amendment has delta quantity zero, action Amend, and a total that is a prorated credit for the
  old price plus a charge for the new one [Help: `ind.qocal_field_and_pricing_amendments`]. The repo
  turns on Sales Price Amendments [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`].
- Swaps, upgrades and downgrades show their action in the **Type** column and SwapIn/SwapOut,
  UpgradeFrom/UpgradeTo, DowngradeFrom/DowngradeTo in **Subtype** [Help: `ind.qocal_swap_upgrade_downgrade_amendments`].

Measured on amendment lines [Measured: early Nov 2026, 264]:

- **After a UI quantity edit, Sales Price and Net Unit Price are blank on the parent line.** The price
  moves to detail rows (for example +2 and −1 at the unit price) and the line total is right. The API's
  `quantityChange` keeps the price on the parent line, so UI and API amendments look different in the
  editor.
- **A UI quantity edit with configuration rules on resets the line's attributes to the product
  defaults**, and activation writes those defaults to the asset. Reopening such a line in the
  configurator shows the diff against the asset. Don't demo an inline quantity edit on an amendment of a
  configured product; change the quantity in the configurator, or demo a product without attributes.

Renewal and cancellation line display in the STLE was not measured; see the parent's Open list.

## 8. Demo checklist

1. Quote page: line editor on the default tab, Progress Indicator above it, Transaction Summary in the
   same tab (repo quote page does this).
2. Change Data Capture on Quote and Order, if the demo runs a flow or agent action against the open
   quote (`enable_change_data_capture`).
3. Browse Catalogs: check which catalog it opens on (the Default Catalog, if set), switch to the demo
   catalog if needed, and pick a leaf subcategory before adding.
4. Demo lines placed with configuration rules on; open each configurable line once in the configurator.
5. Procedure plan inactive before any header-discount demo.
6. Amendment demo: no inline quantity edit on configured products; explain blank parent prices as
   detail-row pricing if they appear.
7. Don't count on Reprice All producing a visible change: on an already-priced quote with nothing
   changed since, our run showed none. After changing a header field that pricing reads, do click it:
   a header-only Place PATCH left the lines' prices alone (section 4). After changing prices or the
   catalog, refresh the decision tables first [Help: `ind.qocal_limitations_for_using_quote_and_order_capture`]; Reprice All alone
   may not show the new price.
